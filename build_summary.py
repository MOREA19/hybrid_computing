"""MODIFIED: gabungkan semua tabel eksperimen dan temuan berbasis hasil aktual."""

from pathlib import Path
import csv

# MODIFIED: builder ini menghasilkan ringkasan gabungan dari tabel benchmark yang aktual.


def main():
    """MODIFIED: rangkai ringkasan temuan dan tabel B1/B2/B3 yang dihasilkan."""
    root = Path(__file__).resolve().parent
    results = root / "results"
    b1_table = (results / "b1_tables.md").read_text(encoding="utf-8").strip()
    b2_table = (results / "b2_table.md").read_text(encoding="utf-8").strip()
    b3_table = (results / "b3_table.md").read_text(encoding="utf-8").strip()
    large_csv = results / "b3_large_results.csv"
    large_section = ""
    if large_csv.exists():
        with large_csv.open(newline="", encoding="utf-8") as csv_file:
            large_rows = list(csv.DictReader(csv_file))
        large_values = {
            (row["mode"], int(row["ranks"])): row for row in large_rows
        }
        large_total_mb = sum(
            path.stat().st_size for path in (root / "b3" / "data_wc_large").glob("*.txt")
        ) / 1_000_000
        ratio_rows = []
        for row in sorted(large_rows, key=lambda item: (int(item["ranks"]), item["mode"])):
            ranks = int(row["ranks"])
            thread_time = float(large_values[("thread", ranks)]["median_time"])
            process_time = float(large_values[("process", ranks)]["median_time"])
            ratio_rows.append(
                f"| {row['mode']} | {ranks} | {float(row['median_time']):.6f} | "
                f"{float(row['std']):.6f} | {process_time / thread_time:.3f} |"
            )
        large_section = "\n\n".join(
            [
                "### Eksperimen korpus besar opsional",
                f"Salinan 30 file, masing-masing minimal 1 MB, berukuran total {large_total_mb:.6f} MB. Lima ulangan setelah warm-up; worker/rank=4.",
                "| Mode | Ranks | Median (s) | Std (s) | Rasio process/thread |",
                "|:---|---:|---:|---:|---:|",
                *ratio_rows,
                "Pada 1 dan 2 rank, process lebih cepat (rasio < 1); pada 4 rank thread lebih cepat. Hasil ini berlaku untuk salinan korpus dan mesin yang diuji, bukan aturan umum.",
            ]
        )
    content = "\n\n".join(
        [
            "# Ringkasan Hasil Hybrid Computing",
            "",
            "Semua angka di bawah berasal dari eksekusi yang direkam di `results/logs/`. Mesin terverifikasi di `results/sysinfo.txt`: AMD Ryzen 7 7445HS, 6 core fisik, 12 thread logis, RAM 15.23 GiB, Windows 11, Python 3.11.9, mpi4py 4.1.2, Microsoft MPI 10.1.12498.52.",
            "",
            "## B1: Hybrid Pipeline",
            "",
            "Temuan utama:",
            "1. Grid menjalankan 42 konfigurasi pada dataset 160 file, dengan satu warm-up dan lima ulangan tercatat per konfigurasi.",
            "2. Throughput median tertinggi terukur 1031.861 files/s pada loader=2, workers=1, Q_MAX=4.",
            "3. Rata-rata throughput menurut workers turun dari 964.068 files/s pada 1 worker menjadi 414.246 files/s pada 16 workers.",
            "4. Rata-rata throughput Q_MAX=32 adalah 744.185 files/s dan Q_MAX=4 adalah 738.919 files/s; selisih agregatnya kecil dibanding variasi antar konfigurasi.",
            "5. Hanya 3 dari 21 pasangan loader/worker memiliki selisih median Q_MAX yang melewati satu simpangan baku gabungan berdasarkan metrik deskriptif yang digunakan.",
            "",
            "### Tabel B1",
            b1_table,
            "",
            "## B2: MPI dan ProcessPool",
            "",
            "Temuan utama:",
            "1. Baseline makespan lama T1 adalah 0.382761 s; nilai ini dipakai ulang tanpa pengukuran ulang untuk membandingkan seluruh konfigurasi.",
            "2. Makespan terendah dalam data lama adalah 0.288248 s pada ranks=2, workers=1 (n=2), dengan speedup 1.327888 dan efisiensi 0.663944.",
            "3. Kombinasi ranks=4, workers=4 memakai n=16 dan total 20 proses (4 rank induk + 16 worker), melewati ambang fisik dan logis.",
            "4. TOTAL_TASKS=8 membatasi paralelisme maksimum delapan tugas global meski konfigurasi menyediakan lebih banyak worker.",
            "5. Biaya startup pool/import NumPy mungkin mendominasi makespan pada tugas kecil; ini dugaan dari bentuk beban dan bukan fakta yang diisolasi oleh pengukuran.",
            "",
            "### Tabel B2",
            b2_table,
            "",
            "Eksekusi validasi baru `mpiexec -n 4 ... --workers 4` menghasilkan makespan 0.414518 s, 2,080,000 sampel, dan estimasi pi 3.140917. Angka ini tidak mengganti dataset makespan lama.",
            "",
            "## B3: Word Count",
            "",
            "Temuan utama:",
            "1. Korpus terdiri dari 30 artikel (15 Indonesia, 15 Inggris), berukuran total 2.325818 MB dengan 340129 token regex.",
            "2. Audit baris 78-95 menunjukkan timer mencakup pembuatan dan penutupan executor pada kedua mode; kode B3 tidak diubah karena cakupan waktunya setara.",
            "3. Pada 1 rank, median thread 0.140518 s dan process 0.221649 s; rasio process/thread 1.577.",
            "4. Pada 4 rank, median thread 0.051737 s sedangkan process 0.407472 s; rasio process/thread 7.876. Thread memberi hasil lebih cepat pada beban korpus ini.",
            "5. Top-10 4-rank thread dan process identik; enam stopword wajib tidak muncul. Runner juga memverifikasi kesamaan Top-10 untuk 1, 2, dan 4 rank.",
            "",
            "### Inventaris korpus",
            "Output per file dan total token ada di [corpus_info.txt](corpus_info.txt); sumber dan URL ada di [corpus_sources.md](corpus_sources.md).",
            "",
            "### Audit kode",
            "Detail timer, penjelasan waktu, dan STOPWORDS ada di [b3_audit.md](b3_audit.md).",
            "",
            "### Tabel B3",
            b3_table,
            large_section,
            "",
            "## Keterbatasan",
            "- B1 memakai lima ulangan per konfigurasi; variasi sistem, cache filesystem, dan proses latar dapat memengaruhi hasil singkat.",
            "- B2 tabel utama memakai makespan lama yang tidak diukur ulang dan tidak menyediakan distribusi ulangan untuk menghitung noise. Satu eksekusi baru hanya berfungsi sebagai validasi program.",
            "- Beban B1 berisi file kecil. Benchmark utama B3 memakai korpus asli sekitar 2.33 MB; eksperimen tambahan memakai pengulangan konten untuk membesarkan file, bukan dokumen besar yang independen dan bervariasi.",
            "- Hasil korpus besar tidak boleh digeneralisasi ke dokumen nyata lain karena setiap file dibentuk dengan mengulang teks sumber sampai minimal 1 MB.",
            "- B3 memakai lima ulangan per konfigurasi; waktu sangat singkat pada mode thread sensitif terhadap noise timer dan aktivitas OS.",
            "- Ambang noise Q_MAX adalah pemeriksaan deskriptif 1 simpangan baku gabungan, bukan uji hipotesis atau interval kepercayaan.",
            "- Dugaan dominasi startup pada B2 belum diuji dengan baseline tanpa pool atau variasi ukuran task.",
            "",
        ]
    )
    output = results / "RINGKASAN.md"
    output.write_text(content, encoding="utf-8")
    print(f"Ringkasan lengkap tersimpan: {output}")
    print(f"Ukuran dokumen: {len(content)} karakter")


if __name__ == "__main__":
    main()