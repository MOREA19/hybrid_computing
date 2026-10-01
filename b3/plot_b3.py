"""MODIFIED: bandingkan median waktu word count thread dan process."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def main():
    """MODIFIED: simpan grafik dan tabel speedup/rasio dari hasil B3."""
    base_dir = Path(__file__).resolve().parent.parent
    results_dir = base_dir / "results"
    data = pd.read_csv(results_dir / "b3_results.csv")
    figure, axis = plt.subplots(figsize=(8.5, 5.5))
    for mode, group in data.groupby("mode"):
        group = group.sort_values("ranks")
        axis.errorbar(
            group["ranks"],
            group["median_time"],
            yerr=group["std"],
            marker="o",
            capsize=4,
            label=mode,
        )  # MODIFIED: tampilkan simpangan baku tiap lima ulangan.
    axis.set_xlabel("MPI ranks")
    axis.set_ylabel("Median waktu maksimum (s)")
    axis.set_title("Word Count: thread vs process")
    axis.set_xticks((1, 2, 4))
    axis.grid(True, alpha=0.3)
    axis.legend()
    figure.tight_layout()
    plot_path = results_dir / "b3_compare.png"
    figure.savefig(plot_path, dpi=160)
    plt.close(figure)

    baselines = data[data["ranks"] == 1].set_index("mode")["median_time"].to_dict()
    paired = data.pivot(index="ranks", columns="mode", values="median_time")
    data["speedup_vs_mode_rank1"] = data.apply(
        lambda row: baselines[row["mode"]] / row["median_time"], axis=1
    )  # MODIFIED: hitung speedup relatif baseline masing-masing mode.
    data["process_thread_ratio"] = data["ranks"].map(
        (paired["process"] / paired["thread"]).to_dict()
    )  # MODIFIED: rasio waktu process/thread per jumlah rank.
    table_rows = []
    for row in data.sort_values(["ranks", "mode"]).itertuples():
        table_rows.append(
            f"| {row.mode} | {row.ranks} | {row.workers_per_rank} | "
            f"{row.median_time:.6f} | {row.std:.6f} | "
            f"{row.speedup_vs_mode_rank1:.3f} | {row.process_thread_ratio:.3f} |"
        )
    report = "\n".join(
        [
            "# Tabel B3",
            "",
            "Median dan std dihitung dari lima pengulangan setelah satu warm-up. Speedup memakai baseline 1 rank untuk mode yang sama. Rasio process/thread adalah median process dibagi median thread; nilai di atas 1 berarti process lebih lambat.",
            "",
            "| Mode | MPI ranks | Workers/rank | Median waktu maks (s) | Std (s) | Speedup vs 1 rank mode sama | Rasio process/thread |",
            "|:---|---:|---:|---:|---:|---:|---:|",
            *table_rows,
            "",
            "![Perbandingan waktu B3 dengan simpangan baku](b3_compare.png)",
            "",
        ]
    )
    report_path = results_dir / "b3_table.md"
    report_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"Grafik: {plot_path}")
    print(f"Tabel: {report_path}")


if __name__ == "__main__":
    main()