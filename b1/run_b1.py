"""MODIFIED: jalankan sweep eksperimen pipeline dengan pengulangan terukur."""

import csv
import itertools
import statistics
from pathlib import Path

from hybrid_pipeline_exp import run_pipeline  # MODIFIED: jalankan salinan eksperimen, bukan sumber asli.

N_LOADER_THREADS = (1, 2, 4)  # MODIFIED: gunakan seluruh jumlah loader yang diminta.
N_WORKERS = (1, 2, 4, 6, 8, 12, 16)  # MODIFIED: sertakan ambang core fisik dan logis.
Q_MAX = (4, 32)  # MODIFIED: bandingkan kedua batas antrean yang diminta.
N_REPEATS = 5  # MODIFIED: ukur lima ulangan setelah warm-up.


def main():
    """Jalankan satu warm-up dan lima ulangan untuk setiap konfigurasi B1."""
    output_path = Path(__file__).resolve().parent.parent / "results" / "b1_results.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "n_loader_threads",
        "n_workers",
        "q_max",
        "total_time",
        "throughput",
        "avg_latency",
        "std_throughput",  # MODIFIED: catat simpangan baku throughput lima ulangan.
        "n_repeats",  # MODIFIED: simpan jumlah pengukuran tercatat.
        "oversub_physical",  # MODIFIED: tandai jumlah proses di atas enam core fisik.
        "oversub_logical",  # MODIFIED: tandai jumlah proses di atas dua belas thread logis.
    ]
    rows = []

    for loaders, workers, queue_size in itertools.product(
        N_LOADER_THREADS, N_WORKERS, Q_MAX
    ):
        # MODIFIED: lakukan warm-up terpisah dan tampilkan nilainya tanpa memasukkannya ke statistik.
        warmup = run_pipeline(loaders, workers, queue_size)
        print(
            f"WARMUP loader={loaders} workers={workers} Q={queue_size}: "
            f"time={warmup['total_time']:.6f}s throughput={warmup['throughput']:.6f} files/s"
        )
        measurements = []
        for repeat in range(1, N_REPEATS + 1):
            measurement = run_pipeline(loaders, workers, queue_size)
            measurements.append(measurement)
            print(
                f"REPEAT {repeat}/{N_REPEATS} loader={loaders} workers={workers} Q={queue_size}: "
                f"time={measurement['total_time']:.6f}s "
                f"throughput={measurement['throughput']:.6f} files/s "
                f"avg_latency={measurement['avg_latency']:.8f}s/file"
            )
        row = {
            "n_loader_threads": loaders,
            "n_workers": workers,
            "q_max": queue_size,
            "total_time": statistics.median(m["total_time"] for m in measurements),
            "throughput": statistics.median(m["throughput"] for m in measurements),
            "avg_latency": statistics.median(m["avg_latency"] for m in measurements),
            "std_throughput": statistics.stdev(m["throughput"] for m in measurements),  # MODIFIED: sampel simpangan baku.
            "n_repeats": N_REPEATS,  # MODIFIED: simpan lima ulangan yang diukur.
            "oversub_physical": workers > 6,  # MODIFIED: gunakan batas enam core fisik terverifikasi.
            "oversub_logical": workers > 12,  # MODIFIED: gunakan batas dua belas thread logis terverifikasi.
        }
        rows.append(row)
        print(
            f"MEDIAN loader={loaders} workers={workers} Q={queue_size}: "
            f"throughput={row['throughput']:.6f} files/s "
            f"std={row['std_throughput']:.6f} files/s"
        )

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Tersimpan: {output_path} ({len(rows)} konfigurasi)")


if __name__ == "__main__":
    main()