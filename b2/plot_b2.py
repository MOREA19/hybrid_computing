"""MODIFIED: hitung ulang analisis, tabel, dan grafik B2 dari makespan terukur."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def main():
    """MODIFIED: hitung ulang seluruh metrik dengan ambang enam dan dua belas."""
    base_dir = Path(__file__).resolve().parent.parent
    results_dir = base_dir / "results"
    input_path = results_dir / "b2_results.csv"
    data = pd.read_csv(input_path)
    required = {"ranks", "workers", "makespan"}
    if not required.issubset(data.columns):
        raise ValueError(f"CSV harus memiliki kolom sumber {sorted(required)}")

    baseline_rows = data[(data["ranks"] == 1) & (data["workers"] == 1)]
    if len(baseline_rows) != 1:
        raise ValueError("CSV harus memiliki tepat satu baseline ranks=1, workers=1")
    baseline = float(baseline_rows.iloc[0]["makespan"])
    data["n"] = data["ranks"] * data["workers"]
    data["speedup"] = baseline / data["makespan"]
    data["efficiency"] = data["speedup"] / data["n"]
    data["oversub_physical"] = data["n"] > 6
    data["oversub_logical"] = data["n"] > 12
    data["total_processes"] = data["ranks"] + data["ranks"] * data["workers"]  # MODIFIED: hitung rank induk dan worker pool per rank.
    data = data[[
        "ranks", "workers", "n", "makespan", "speedup", "efficiency",
        "oversub_physical", "oversub_logical", "total_processes",
    ]].sort_values(["ranks", "workers"])

    fields = list(data.columns)
    with input_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data.to_dict(orient="records"))

    figure, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for workers, group in data.groupby("workers"):
        group = group.sort_values("n")
        axes[0].plot(group["n"], group["speedup"], marker="o", label=f"{workers} worker/rank")
        axes[1].plot(group["n"], group["efficiency"], marker="o", label=f"{workers} worker/rank")
    axes[0].set_title("Speedup")
    axes[0].set_ylabel("T1 / T")
    axes[1].set_title("Efisiensi")
    axes[1].set_ylabel("Speedup / n")
    for axis in axes:
        axis.axvline(6, color="black", linestyle="--", linewidth=1, label="6 core fisik")  # MODIFIED: tandai ambang fisik.
        axis.axvline(12, color="dimgray", linestyle=":", linewidth=1.3, label="12 thread logis")  # MODIFIED: tandai ambang logis.
        axis.set_xlabel("n = ranks x workers")
        axis.set_xticks(sorted(data["n"].unique()))
        axis.grid(True, alpha=0.3)
        axis.legend(fontsize=8)
    figure.tight_layout()
    plot_path = results_dir / "b2_speedup.png"
    figure.savefig(plot_path, dpi=160)
    plt.close(figure)

    table_rows = []
    for row in data.itertuples():
        table_rows.append(
            f"| {row.ranks} | {row.workers} | {row.n} | {row.makespan:.6f} | "
            f"{row.speedup:.6f} | {row.efficiency:.6f} | "
            f"{'Ya' if row.oversub_physical else 'Tidak'} | "
            f"{'Ya' if row.oversub_logical else 'Tidak'} | {row.total_processes} |"
        )
    report = "\n".join(
        [
            "# Tabel B2",
            "",
            f"Metrik dihitung ulang dari makespan lama; baseline T1 = {baseline:.6f} s (ranks=1, workers=1). Makespan tidak diukur ulang untuk tabel ini.",
            "",
            "| Ranks | Workers/rank | n=ranks*workers | Makespan (s) | Speedup=T1/T | Efisiensi=speedup/n | Oversub fisik (n>6) | Oversub logis (n>12) | Total proses=ranks+n |",
            "|---:|---:|---:|---:|---:|---:|:---:|:---:|---:|",
            *table_rows,
            "",
            "Catatan: TOTAL_TASKS=8 membatasi paralelisme tugas maksimum menjadi 8 tugas serentak. Dugaan, bukan fakta terukur: pada beban ini makespan mungkin didominasi biaya startup pool proses dan impor NumPy.",
            "",
            "![Grafik speedup dan efisiensi B2](b2_speedup.png)",
            "",
        ]
    )
    report_path = results_dir / "b2_table.md"
    report_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"CSV tersimpan: {input_path}")
    print(f"Grafik tersimpan: {plot_path}")
    print(f"Tabel tersimpan: {report_path}")


if __name__ == "__main__":
    main()