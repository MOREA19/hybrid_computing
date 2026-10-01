"""MODIFIED: buat grafik dan laporan analisis markdown hasil B1."""

from math import sqrt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def markdown_table(headers, rows):
    """MODIFIED: susun tabel markdown tanpa dependensi formatter tambahan."""
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def main():
    """MODIFIED: hasilkan grafik dan seluruh tabel evaluasi B1."""
    base_dir = Path(__file__).resolve().parent.parent
    results_dir = base_dir / "results"
    data = pd.read_csv(results_dir / "b1_results.csv")
    figure, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)

    for axis, queue_size in zip(axes, (4, 32)):
        subset = data[data["q_max"] == queue_size]
        for loaders, group in subset.groupby("n_loader_threads"):
            group = group.sort_values("n_workers")
            axis.plot(
                group["n_workers"],
                group["throughput"],
                marker="o",
                label=f"Loader {loaders}",
            )
        axis.axvline(6, color="black", linestyle="--", linewidth=1, label="6 core fisik")  # MODIFIED: tandai batas core fisik.
        axis.axvline(12, color="dimgray", linestyle=":", linewidth=1.3, label="12 thread logis")  # MODIFIED: tandai batas thread logis.
        axis.set_title(f"Q_MAX = {queue_size}")
        axis.set_xlabel("N_WORKERS")
        axis.set_xticks((1, 2, 4, 6, 8, 12, 16))  # MODIFIED: tampilkan semua worker yang diukur.
        axis.grid(True, alpha=0.3)
        axis.legend(fontsize=8)

    axes[0].set_ylabel("Throughput (files/s)")
    figure.tight_layout()
    plot_path = results_dir / "b1_throughput.png"
    figure.savefig(plot_path, dpi=160)
    plt.close(figure)

    ordered = data.sort_values(["q_max", "n_loader_threads", "n_workers"])
    full_rows = [
        (
            int(row.n_loader_threads),
            int(row.n_workers),
            int(row.q_max),
            f"{row.total_time:.6f}",
            f"{row.throughput:.3f}",
            f"{row.avg_latency:.8f}",
            f"{row.std_throughput:.3f}",
        )
        for row in ordered.itertuples()
    ]
    best_rows = [
        (
            int(row.n_loader_threads),
            int(row.n_workers),
            int(row.q_max),
            f"{row.throughput:.3f}",
            f"{row.std_throughput:.3f}",
        )
        for row in data.nlargest(5, "throughput").itertuples()
    ]

    mean_tables = {}
    for column, label in (("n_workers", "N_WORKERS"), ("n_loader_threads", "Loader threads"), ("q_max", "Q_MAX")):
        means = data.groupby(column, as_index=False)["throughput"].mean().sort_values(column)
        mean_tables[label] = markdown_table(
            [label, "Rata-rata throughput (files/s)"],
            [(int(row[column]), f"{row['throughput']:.3f}") for _, row in means.iterrows()],
        )

    delta_rows = []
    for (loaders, workers), group in data.groupby(["n_loader_threads", "n_workers"]):
        q4 = group[group["q_max"] == 4].iloc[0]
        q32 = group[group["q_max"] == 32].iloc[0]
        delta = q32["throughput"] - q4["throughput"]
        percent = delta / q4["throughput"] * 100 if q4["throughput"] else 0.0
        combined_noise = sqrt(q4["std_throughput"] ** 2 + q32["std_throughput"] ** 2)
        delta_rows.append(
            (
                int(loaders),
                int(workers),
                f"{q4['throughput']:.3f}",
                f"{q32['throughput']:.3f}",
                f"{percent:+.2f}%",
                f"{combined_noise:.3f}",
                "Ya" if abs(delta) > combined_noise else "Tidak",
            )
        )

    report = "\n".join(
        [
            "# Analisis B1",
            "",
            "Setiap baris merangkum median dari 5 ulangan setelah 1 warm-up. `std_throughput` adalah simpangan baku sampel throughput pada lima ulangan.",
            "",
            "## Semua konfigurasi",
            markdown_table(
                ["Loader", "Workers", "Q_MAX", "Total time median (s)", "Throughput median (files/s)", "Avg latency median (s/file)", "Std throughput (files/s)"],
                full_rows,
            ),
            "",
            "## Lima throughput tertinggi",
            markdown_table(["Loader", "Workers", "Q_MAX", "Throughput (files/s)", "Std throughput (files/s)"], best_rows),
            "",
            "## Rata-rata throughput per jumlah worker",
            mean_tables["N_WORKERS"],
            "",
            "## Rata-rata throughput per jumlah loader",
            mean_tables["Loader threads"],
            "",
            "## Rata-rata throughput per Q_MAX",
            mean_tables["Q_MAX"],
            "",
            "## Selisih Q_MAX 32 dibanding 4",
            "Perubahan persen = `(throughput Q32 - throughput Q4) / throughput Q4`. Ambang noise deskriptif dihitung sebagai `sqrt(std_Q4^2 + std_Q32^2)`; tanda Ya berarti selisih absolut median melewati satu simpangan baku gabungan, bukan uji signifikansi statistik.",
            markdown_table(
                ["Loader", "Workers", "Q4 throughput", "Q32 throughput", "Perubahan", "Noise gabungan (files/s)", "Selisih > noise?"],
                delta_rows,
            ),
            "",
        ]
    )
    report_path = results_dir / "b1_tables.md"
    report_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"Grafik tersimpan: {plot_path}")
    print(f"Tabel tersimpan: {report_path}")


if __name__ == "__main__":
    main()