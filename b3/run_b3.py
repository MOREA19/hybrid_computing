"""MODIFIED: ukur word count thread/process untuk beberapa jumlah rank."""

import csv
import itertools
import re
import statistics
import subprocess
import sys
from pathlib import Path


def run_once(script_dir, ranks, mode):
    """Jalankan satu ulangan MPI dan parsing waktu maksimum per rank."""
    command = [
        "mpiexec",
        "-n",
        str(ranks),
        sys.executable,
        "praktikum3_modified.py",
        "--mode",
        mode,
        "--workers",
        "4",
    ]
    result = subprocess.run(
        command,
        cwd=script_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=240,
    )
    output = result.stdout + result.stderr
    if result.returncode != 0:
        raise RuntimeError(f"Perintah gagal ({result.returncode}): {' '.join(command)}\n{output}")
    match = re.search(r"^Time \(max per rank\):\s*([0-9.]+)\s*s", output, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Waktu tidak ditemukan dalam output:\n{output}")
    if "Top-10 kata global (stopwords dibuang):" not in output:
        raise RuntimeError(f"Bagian Top-10 tidak ditemukan dalam output:\n{output}")
    top_lines = output.split("Top-10 kata global (stopwords dibuang):", 1)[1].strip()
    top_words = tuple(
        (line.rsplit(":", 1)[0].strip(), int(line.rsplit(":", 1)[1].strip()))
        for line in top_lines.splitlines()
        if ":" in line
    )
    return float(match.group(1)), top_words, output


def main():
    """MODIFIED: ukur enam kombinasi dengan warm-up dan lima ulangan."""
    script_dir = Path(__file__).resolve().parent
    results_dir = script_dir.parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    top_output = {}
    for mode, ranks in itertools.product(("thread", "process"), (1, 2, 4)):
        warmup_time, warmup_top, _ = run_once(script_dir, ranks, mode)
        print(
            f"WARMUP mode={mode} ranks={ranks}: time={warmup_time:.6f} s "
            f"Top-10 entries={len(warmup_top)}"
        )
        times = []
        repeat_top = []
        for repetition in range(1, 6):
            elapsed, top_words, _ = run_once(script_dir, ranks, mode)
            times.append(elapsed)
            repeat_top.append(top_words)
            print(f"REPEAT {repetition}/5 mode={mode} ranks={ranks}: max_time={elapsed:.6f} s")
        if any(top_words != repeat_top[0] for top_words in repeat_top[1:]):
            raise RuntimeError(f"Top-10 berubah antarulangan untuk mode={mode}, ranks={ranks}")
        top_output[(mode, ranks)] = repeat_top[0]
        rows.append(
            {
                "mode": mode,
                "ranks": ranks,
                "workers_per_rank": 4,
                "median_time": statistics.median(times),
                "std": statistics.stdev(times),  # MODIFIED: simpan simpangan baku lima ulangan.
            }
        )
        print(
            f"MEDIAN mode={mode} ranks={ranks}: {statistics.median(times):.6f} s "
            f"std={statistics.stdev(times):.6f} s"
        )

    for ranks in (1, 2, 4):
        thread_top = top_output[("thread", ranks)]
        process_top = top_output[("process", ranks)]
        if thread_top != process_top:
            raise RuntimeError(f"Top-10 thread/process berbeda pada ranks={ranks}")
        stopwords = {"dan", "yang", "di", "the", "of", "and"}
        present = sorted(word for word, _ in thread_top if word in stopwords)
        if present:
            raise RuntimeError(f"Stopwords wajib ditemukan di Top-10 ranks={ranks}: {present}")
        print(f"VERIFIED ranks={ranks}: Top-10 identik; stopwords wajib tidak ada")

    output_path = results_dir / "b3_results.csv"
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        fields = ["mode", "ranks", "workers_per_rank", "median_time", "std"]
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Tersimpan: {output_path}")


if __name__ == "__main__":
    main()