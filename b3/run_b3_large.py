"""MODIFIED: benchmark opsional pada salinan korpus besar tanpa mengubah korpus utama."""

import argparse
import csv
import math
import multiprocessing
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

from praktikum3_modified import STOPWORDS, count_file

# MODIFIED: eksperimen besar menggunakan fungsi worker top-level agar aman untuk spawn.


def chunk_range(total, parts, index):
    """MODIFIED: bagikan file secara merata antarrank MPI."""
    base, remainder = divmod(total, parts)
    start = index * base + min(index, remainder)
    return start, start + base + (1 if index < remainder else 0)


def make_large_corpus(source_dir, target_dir):
    """MODIFIED: buat file baru minimal 1 MB dari setiap file sumber."""
    target_dir.mkdir(parents=True, exist_ok=True)
    source_files = sorted(source_dir.glob("*.txt"))
    existing = sorted(target_dir.glob("*.txt"))
    if existing:
        if len(existing) < 30 or any(path.stat().st_size < 1_000_000 for path in existing):
            raise RuntimeError(f"Direktori besar sudah ada tetapi tidak valid: {target_dir}")
        print(f"Korpus besar yang sudah ada dipertahankan: {len(existing)} file")
        return existing

    if len(source_files) < 30:
        raise RuntimeError(f"Korpus sumber memiliki {len(source_files)} file; diperlukan minimal 30")
    created = []
    for source in source_files:
        original = source.read_bytes()
        if not original:
            raise RuntimeError(f"File sumber kosong: {source}")
        repetitions = math.ceil(1_000_000 / len(original))
        payload = original * repetitions
        output = target_dir / source.name
        output.write_bytes(payload)
        created.append(output)
        print(f"CORPUS {output.name}: {output.stat().st_size} bytes")
    print(f"CORPUS TOTAL: {len(created)} files, {sum(path.stat().st_size for path in created)} bytes")
    return created


def mpi_worker(args):
    """MODIFIED: proses korpus pada MPI ranks dengan batas timing yang sama."""
    import mpi4py

    mpi4py.rc.initialize = False
    from mpi4py import MPI

    if not MPI.Is_initialized():
        MPI.Init()
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    if rank == 0:
        all_files = [str(path) for path in sorted(Path(args.data_dir).glob("*.txt"))]
    else:
        all_files = None
    all_files = comm.bcast(all_files, root=0)
    start, end = chunk_range(len(all_files), size, rank)
    tasks = [(path, STOPWORDS) for path in all_files[start:end]]

    comm.Barrier()
    started = time.perf_counter()
    if args.mode == "thread":
        executor_type = __import__("concurrent.futures", fromlist=["ThreadPoolExecutor"]).ThreadPoolExecutor
        options = {"max_workers": 4}
    else:
        executor_type = __import__("concurrent.futures", fromlist=["ProcessPoolExecutor"]).ProcessPoolExecutor
        options = {"max_workers": 4, "mp_context": multiprocessing.get_context("spawn")}
    with executor_type(**options) as executor:
        counters = list(executor.map(count_file, tasks))
    local_words = sum(sum(counter.values()) for counter in counters)
    elapsed = time.perf_counter() - started
    max_elapsed = comm.reduce(elapsed, op=MPI.MAX, root=0)
    global_words = comm.reduce(local_words, op=MPI.SUM, root=0)
    if rank == 0:
        print(f"[MPI ranks={size}] mode={args.mode} files={len(all_files)} workers/rank=4")
        print(f"Time (max per rank): {max_elapsed:.6f} s")
        print(f"Words processed: {global_words}")
    MPI.Finalize()


def run_once(script_dir, python_executable, data_dir, ranks, mode):
    """MODIFIED: jalankan satu konfigurasi MPI dan baca durasi terukur."""
    command = [
        "mpiexec", "-n", str(ranks), python_executable, "run_b3_large.py",
        "--mpi-worker", "--data-dir", str(data_dir), "--mode", mode,
    ]
    result = subprocess.run(
        command,
        cwd=script_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=900,
    )
    output = result.stdout + result.stderr
    if result.returncode != 0:
        raise RuntimeError(f"Perintah gagal ({result.returncode}): {' '.join(command)}\n{output}")
    match = re.search(r"^Time \(max per rank\):\s*([0-9.]+)\s*s", output, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Waktu tidak ditemukan dalam output:\n{output}")
    return float(match.group(1)), output


def main():
    """MODIFIED: buat data besar dan ukur enam konfigurasi dengan median/std."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--mpi-worker", action="store_true")
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--mode", choices=("thread", "process"))
    args = parser.parse_args()
    if args.mpi_worker:
        if args.data_dir is None or args.mode is None:
            parser.error("--mpi-worker memerlukan --data-dir dan --mode")
        mpi_worker(args)
        return

    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent
    data_dir = script_dir / "data_wc_large"
    files = make_large_corpus(script_dir / "data_wc", data_dir)
    print(f"TOTAL LARGE MB: {sum(path.stat().st_size for path in files) / 1_000_000:.6f}")
    rows = []
    log_path = root / "results" / "logs" / "b3_large_sweep.txt"
    for mode in ("thread", "process"):
        for ranks in (1, 2, 4):
            warmup, warmup_output = run_once(script_dir, sys.executable, data_dir, ranks, mode)
            print(f"WARMUP mode={mode} ranks={ranks}: {warmup:.6f} s")
            with log_path.open("a", encoding="utf-8") as log_file:
                log_file.write(f"\nWARMUP mode={mode} ranks={ranks}\n{warmup_output}")
            times = []
            for repeat in range(1, 6):
                elapsed, output = run_once(script_dir, sys.executable, data_dir, ranks, mode)
                times.append(elapsed)
                print(f"REPEAT {repeat}/5 mode={mode} ranks={ranks}: {elapsed:.6f} s")
                with log_path.open("a", encoding="utf-8") as log_file:
                    log_file.write(f"\nREPEAT {repeat}/5 mode={mode} ranks={ranks}\n{output}")
            rows.append(
                {
                    "mode": mode,
                    "ranks": ranks,
                    "workers_per_rank": 4,
                    "median_time": statistics.median(times),
                    "std": statistics.stdev(times),
                }
            )
            print(
                f"MEDIAN mode={mode} ranks={ranks}: {statistics.median(times):.6f} s "
                f"std={statistics.stdev(times):.6f} s"
            )

    output_path = root / "results" / "b3_large_results.csv"
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=("mode", "ranks", "workers_per_rank", "median_time", "std"))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Tersimpan: {output_path}")


if __name__ == "__main__":
    main()