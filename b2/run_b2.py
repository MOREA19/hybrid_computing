"""MODIFIED: ukur kombinasi rank MPI dan worker proses B2."""

import csv
import itertools
import re
import statistics
import subprocess
import sys
from pathlib import Path


def run_once(mpiexec, python_executable, script_dir, ranks, workers):
    """Jalankan satu eksperimen dan ambil makespan dari stdout rank nol."""
    command = [
        mpiexec,
        "-n",
        str(ranks),
        python_executable,
        "praktikum2_fixed.py",
        "--workers",
        str(workers),
    ]
    result = subprocess.run(
        command,
        cwd=script_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    output = result.stdout + result.stderr
    if result.returncode != 0:
        raise RuntimeError(f"Perintah gagal ({result.returncode}): {' '.join(command)}\n{output}")
    match = re.search(r"^Makespan\s*:\s*([0-9.]+)\s*s", output, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Baris Makespan tidak ditemukan pada output:\n{output}")
    return float(match.group(1)), output


def main():
    """Ambil tiga pengukuran per konfigurasi dan simpan CSV hasil."""
    script_dir = Path(__file__).resolve().parent
    results_dir = script_dir.parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    mpiexec = "mpiexec"
    measurements = []

    for ranks, workers in itertools.product((1, 2, 4), (1, 2, 4)):
        times = []
        for repetition in range(1, 4):
            makespan, _ = run_once(mpiexec, sys.executable, script_dir, ranks, workers)
            times.append(makespan)
            print(
                f"rank={ranks} workers={workers} run={repetition}: "
                f"makespan={makespan:.6f} s"
            )
        measurements.append(
            {"ranks": ranks, "workers": workers, "makespan": statistics.median(times)}
        )

    baseline = next(
        row["makespan"] for row in measurements
        if row["ranks"] == 1 and row["workers"] == 1
    )
    for row in measurements:
        parallelism = row["ranks"] * row["workers"]
        speedup = baseline / row["makespan"]
        row.update(
            {
                "total_tasks": 8,
                "parallelism": parallelism,
                "speedup": speedup,
                "efficiency": speedup / parallelism,
                "oversubscription_gt_8": parallelism > 8,
            }
        )

    output_path = results_dir / "b2_results.csv"
    fields = [
        "ranks",
        "workers",
        "total_tasks",
        "parallelism",
        "makespan",
        "speedup",
        "efficiency",
        "oversubscription_gt_8",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(measurements)
    print(f"Tersimpan: {output_path}")


if __name__ == "__main__":
    main()