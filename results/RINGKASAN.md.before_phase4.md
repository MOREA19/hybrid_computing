# Ringkasan Eksperimen Hybrid Computing

Semua waktu dan throughput di bawah berasal dari eksekusi nyata. B1 dan B2 diukur pada 30 konfigurasi dan 9 konfigurasi, masing-masing dengan satu warm-up (B1) dan tiga pengulangan; B3 memakai median tiga ulangan per konfigurasi. Spesifikasi host saat pengujian tercatat di `sysinfo.txt`.

## Lingkungan

| Komponen | Hasil deteksi |
|:---|:---|
| CPU | AMD Ryzen 7 7445HS w/ Radeon 740M Graphics |
| Core fisik / logis | 6 / 12 |
| RAM | 15.23 GiB |
| OS | Microsoft Windows 11 Home Single Language, build 26200 |
| Python | 3.11.9 |
| mpi4py | 4.1.2 |
| MPI | Microsoft MPI 10.1.12498.52 |

 Hasil eksperimen menggunakan perangkat yang terdeteksi. Pada Microsoft MPI, `mpiexec --version` menghasilkan `Unknown option`; versinya diverifikasi lewat `MPI.Get_library_version()`.

## B1: Hybrid Pipeline

Dataset berisi 160 file teks. Angka merupakan median tiga pengukuran setelah satu warm-up untuk konfigurasi tersebut.

| Loader | Workers | Q_MAX | Total time (s) | Throughput (files/s) | Avg latency (s/file) |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 4 | 0.2697 | 593.266 | 0.000371 |
| 1 | 2 | 4 | 0.2062 | 775.917 | 0.000265 |
| 1 | 4 | 4 | 0.1950 | 820.589 | 0.000295 |
| 1 | 8 | 4 | 0.2267 | 705.666 | 0.000399 |
| 1 | 16 | 4 | 0.3696 | 432.937 | 0.000446 |
| 2 | 1 | 4 | 0.1712 | 934.323 | 0.000283 |
| 2 | 2 | 4 | 0.1782 | 897.916 | 0.000352 |
| 2 | 4 | 4 | 0.1867 | 857.106 | 0.000321 |
| 2 | 8 | 4 | 0.2214 | 722.814 | 0.000399 |
| 2 | 16 | 4 | 0.3667 | 436.294 | 0.000483 |
| 4 | 1 | 4 | 0.1710 | 935.596 | 0.000268 |
| 4 | 2 | 4 | 0.1684 | 950.362 | 0.000413 |
| 4 | 4 | 4 | 0.1806 | 886.106 | 0.000300 |
| 4 | 8 | 4 | 0.2209 | 724.148 | 0.000332 |
| 4 | 16 | 4 | 0.3503 | 456.780 | 0.000459 |
| 1 | 1 | 32 | 0.2234 | 716.095 | 0.000301 |
| 1 | 2 | 32 | 0.2006 | 797.639 | 0.000384 |
| 1 | 4 | 32 | 0.1895 | 844.550 | 0.000352 |
| 1 | 8 | 32 | 0.2235 | 715.852 | 0.000362 |
| 1 | 16 | 32 | 0.3776 | 423.737 | 0.000464 |
| 2 | 1 | 32 | 0.1832 | 873.373 | 0.000264 |
| 2 | 2 | 32 | 0.1733 | 923.247 | 0.000308 |
| 2 | 4 | 32 | 0.1882 | 850.270 | 0.000326 |
| 2 | 8 | 32 | 0.2296 | 696.776 | 0.000328 |
| 2 | 16 | 32 | 0.3803 | 420.727 | 0.000471 |
| 4 | 1 | 32 | 0.1750 | 914.318 | 0.000217 |
| 4 | 2 | 32 | 0.1756 | 911.100 | 0.000327 |
| 4 | 4 | 32 | 0.1790 | 893.695 | 0.000363 |
| 4 | 8 | 32 | 0.2168 | 738.032 | 0.000341 |
| 4 | 16 | 32 | 0.3551 | 450.573 | 0.000419 |

Throughput tertinggi pada sweep ini adalah 950.362 files/s untuk 4 loader, 2 worker, dan `Q_MAX=4` (median total time 0.1684 s). Pada keenam kombinasi loader/Q, 16 worker lebih lambat daripada konfigurasi 1–4 worker; biaya proses tambahan tidak terbayar oleh tugas baca file pendek. Grafik: `b1_throughput.png`.

## B2: MPI + ProcessPool

`T1` adalah median makespan konfigurasi 1 rank × 1 worker, yaitu 0.382761 s. Speedup dihitung sebagai `T1 / T`, efisiensi sebagai `speedup / (rank × worker)`. `TOTAL_TASKS=8` berarti maksimum delapan tugas Monte Carlo independen tersedia secara global.

| Rank | Worker/rank | Rank × worker | Median makespan (s) | Speedup | Efisiensi | Rank × worker > 8 |
|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 1 | 1 | 0.382761 | 1.000 | 1.000 | Tidak |
| 1 | 2 | 2 | 0.297574 | 1.286 | 0.643 | Tidak |
| 1 | 4 | 4 | 0.328545 | 1.165 | 0.291 | Tidak |
| 2 | 1 | 2 | 0.288248 | 1.328 | 0.664 | Tidak |
| 2 | 2 | 4 | 0.316255 | 1.210 | 0.303 | Tidak |
| 2 | 4 | 8 | 0.401250 | 0.954 | 0.119 | Tidak |
| 4 | 1 | 4 | 0.309163 | 1.238 | 0.310 | Tidak |
| 4 | 2 | 8 | 0.396123 | 0.966 | 0.121 | Tidak |
| 4 | 4 | 16 | 0.389541 | 0.983 | 0.061 | Ya |

Konfigurasi tercepat adalah 2 rank × 1 worker, dengan speedup 1.328 dan efisiensi 0.664. Menambah worker tidak selalu membantu karena hanya ada delapan tugas, overhead MPI/proses ikut dihitung, dan konfigurasi 16 proses melampaui ambang 8 yang ditetapkan tugas. Ambang tugas `>8` ditandai pada CSV; karena host aktual hanya memiliki 6 core fisik, konfigurasi dengan 8 proses juga sudah melebihi jumlah core fisik walaupun flag tugasnya belum aktif. Traceback sumber tersimpan di `b2_error.txt`; akar masalahnya lambda yang diberikan ke `ProcessPoolExecutor` tidak dapat di-pickle. Grafik: `b2_speedup.png`.

## B3: Word Count

Korpus berisi 30 artikel Wikipedia nyata (15 Indonesia, 15 Inggris), sekitar 2.33 MB. Pencarian dilakukan via Wikimedia REST API; `b3/data_wc/corpus_sources.csv` menyimpan judul dan URL. Waktu yang dilaporkan adalah median tiga ulangan dan reduce maksimum antarrank, dengan 4 worker per rank.

| Mode | MPI ranks | Workers/rank | Median waktu maksimum (s) |
|:---|---:|---:|---:|
| thread | 1 | 4 | 0.227278 |
| thread | 2 | 4 | 0.102745 |
| thread | 4 | 4 | 0.056809 |
| process | 1 | 4 | 0.227523 |
| process | 2 | 4 | 0.240746 |
| process | 4 | 4 | 0.391756 |

Untuk korpus dan host ini, thread mode lebih cepat pada 2 dan 4 rank, sedangkan kedua mode hampir sama pada 1 rank. Thread memanfaatkan I/O file yang dapat menunggu tanpa menahan GIL, tetapi regex dan pembaruan `Counter` adalah kerja Python yang CPU-bound dan thread peringkat tunggal tidak menjalankannya paralel karena GIL. Scaling thread yang terlihat di tabel terutama berasal dari pembagian file antar-rank MPI. Process mode menggunakan `spawn`; biaya memulai proses dan mengirim hasil `Counter` lebih besar daripada manfaatnya pada dokumen sekitar 2.33 MB. Pada 4 rank × 4 proses, terdapat 16 worker proses terhadap 6 core fisik yang terdeteksi, sehingga kontensi menambah waktu. Kesimpulan ini terbatas pada ukuran korpus/mesin dan konfigurasi yang diukur. Top-10 sesudah stopwords dicetak oleh program saat dijalankan; grafik perbandingan: `b3_comparison.png`.

Top-10 berikut dicetak oleh kedua mode pada pengujian langsung 1 rank; hitungannya sama.

| Kata | Frekuensi |
|:---|---:|
| in | 3288 |
| tanggal | 2885 |
| indonesia | 2577 |
| a | 2425 |
| dari | 2088 |
| to | 2040 |
| 1 | 1719 |
| pada | 1673 |
| diakses | 1305 |
| 2 | 1298 |

## Perintah dan Validasi

- Dari direktori `b1`, `..\.venv\Scripts\python.exe .\make_data_b1.py` menghasilkan `done. 160 files`.
- `python .\tugas_hybrid\b1\run_b1.py` menghasilkan 30 konfigurasi; tabel final dicetak oleh `plot_b1.py`.
- `python .\tugas_hybrid\b2\praktikum2_original.py` gagal dengan `_pickle.PicklingError: Can't pickle <function <lambda> ...>` karena fungsi lambda lokal tidak dapat dipickle untuk worker proses.
- `python .\tugas_hybrid\b2\run_b2.py` berhasil menjalankan 27 proses pengukuran (9 konfigurasi × 3); hasil median ada di `b2_results.csv`.
- `python .\tugas_hybrid\b3\run_b3.py` berhasil menjalankan 18 proses pengukuran (6 konfigurasi × 3); hasil median ada di `b3_results.csv`.
- Semua skrip eksperimen memiliki guard `if __name__ == "__main__"` untuk kompatibilitas Windows spawn.