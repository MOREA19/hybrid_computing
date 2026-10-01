"""MODIFIED: word count dengan thread/process, stopwords, dan timing MPI."""

import argparse
import multiprocessing
import os
import re
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

import mpi4py

# MODIFIED: worker spawn hanya mengimpor definisi; MPI diinisialisasi rank utama.
mpi4py.rc.initialize = False
from mpi4py import MPI


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_wc")  # MODIFIED: jalur data stabil.
N_WORKERS = 4
STOPWORDS = {"dan", "yang", "di", "the", "of", "and"}  # MODIFIED: stopwords minimum tugas.
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def count_file(task):
    """Hitung token dari satu dokumen sesudah stopwords dibuang."""
    path, stopwords = task
    with open(path, "r", encoding="utf-8", errors="ignore") as text_file:
        text = text_file.read().lower()
    words = (word for word in TOKEN_PATTERN.findall(text) if word not in stopwords)
    return Counter(words)


def chunk_range(total, parts, index):
    """Bagi daftar file antarrank secara merata."""
    base = total // parts
    remainder = total % parts
    start = index * base + min(index, remainder)
    end = start + base + (1 if index < remainder else 0)
    return start, end


def parse_args():
    """Baca mode executor dan jumlah worker dari argumen CLI."""
    parser = argparse.ArgumentParser(description="Word count MPI dengan thread atau proses.")
    parser.add_argument("--mode", choices=("thread", "process"), required=True)
    parser.add_argument("--workers", type=int, default=N_WORKERS)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers harus >= 1")
    return args


def main():
    """Jalankan pemrosesan korpus, reduce waktu maksimum, dan tampilkan top-10."""
    args = parse_args()
    if not MPI.Is_initialized():
        MPI.Init()  # MODIFIED: MPI hanya dimulai pada proses rank utama, bukan worker spawn.
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    all_files = []
    if rank == 0:
        if not os.path.isdir(DATA_DIR):
            raise SystemExit(f"Folder korpus tidak ditemukan: {DATA_DIR}")
        all_files = [
            os.path.join(DATA_DIR, name)
            for name in sorted(os.listdir(DATA_DIR))
            if name.lower().endswith(".txt")
        ]
        if not all_files:
            raise SystemExit(f"Tidak ada file .txt dalam {DATA_DIR}")
    all_files = comm.bcast(all_files if rank == 0 else None, root=0)
    start, end = chunk_range(len(all_files), size, rank)
    my_files = all_files[start:end]

    comm.Barrier()
    started = time.perf_counter()
    local_counter = Counter()
    tasks = [(path, STOPWORDS) for path in my_files]
    if args.mode == "thread":
        executor_type = ThreadPoolExecutor
        executor_options = {"max_workers": args.workers}
    else:
        executor_type = ProcessPoolExecutor
        executor_options = {
            "max_workers": args.workers,
            "mp_context": multiprocessing.get_context("spawn"),
        }  # MODIFIED: mode process menggunakan spawn agar sesuai perilaku Windows.

    with executor_type(**executor_options) as executor:
        futures = [executor.submit(count_file, task) for task in tasks]
        for future in as_completed(futures):
            local_counter.update(future.result())
    elapsed = time.perf_counter() - started

    max_elapsed = comm.reduce(elapsed, op=MPI.MAX, root=0)  # MODIFIED: ukur makespan rank terlama.
    gathered = comm.gather(local_counter, root=0)

    if rank == 0:
        global_counter = Counter()
        for rank_counter in gathered:
            global_counter.update(rank_counter)
        print(f"[MPI ranks={size}] mode={args.mode} files={len(all_files)} workers/rank={args.workers}")
        print(f"Time (max per rank): {max_elapsed:.6f} s")
        print("Top-10 kata global (stopwords dibuang):")
        for word, count in global_counter.most_common(10):
            print(f"{word:>15s} : {count}")

    MPI.Finalize()  # MODIFIED: akhiri MPI sesudah semua komunikasi selesai.


if __name__ == "__main__":
    main()