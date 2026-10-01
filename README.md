# Tugas Hybrid Computing

Eksperimen paralel B1, B2, dan B3 untuk Windows 11. Sumber praktikum asli berada di `original/` dan tidak diubah; versi eksperimen serta alat analisis berada di `b1/`, `b2/`, dan `b3/`. Hasil numerik di `results/` berasal dari eksekusi dan lingkungan yang dicatat di `results/sysinfo.txt`.

## Persiapan Windows

Gunakan Python 3.11, Microsoft MPI runtime dan SDK, lalu buat venv dari folder proyek:

```powershell
py -3.11 -m venv .\.venv
& .\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
mpiexec -help
& .\.venv\Scripts\python.exe -c "from mpi4py import MPI; print(MPI.Get_library_version())"
```

Untuk mencatat mesin yang sedang dipakai:

```powershell
& .\.venv\Scripts\python.exe .\sysinfo.py
Get-Content .\results\sysinfo.txt
```

## B1: Hybrid Pipeline

Jika data belum tersedia, jalankan generator dari `b1/`. Data yang digunakan untuk hasil ini sudah berisi 160 file.

```powershell
Push-Location .\b1
..\.venv\Scripts\python.exe .\make_data_b1.py
..\.venv\Scripts\python.exe .\run_b1.py
Pop-Location
& .\.venv\Scripts\python.exe .\b1\plot_b1.py
```

Grid berisi 3 loader x 7 jumlah worker (termasuk 6 core fisik) x 2 batas queue; tiap konfigurasi menjalani satu warm-up dan lima ulangan. `results/b1_results.csv` menyimpan median, simpangan baku throughput, jumlah ulangan, dan flag oversubscription. Tabel lengkap dan analisis ada di `results/b1_tables.md`; grafik ada di `results/b1_throughput.png`. Untuk satu run dengan parameter slide asli, jalankan `hybrid_pipeline_original.py` dari `b1/`.

## B2: MPI dan ProcessPool

Program perbaikan menerima worker lokal melalui CLI:

```powershell
Push-Location .\b2
mpiexec -n 4 ..\.venv\Scripts\python.exe .\praktikum2_fixed.py --workers 4
Pop-Location
```

`results/b2_results.csv` mempertahankan makespan lama dan menghitung ulang speedup, efisiensi, ambang fisik/logis, serta jumlah proses rank+worker. Tabel ada di `results/b2_table.md`, grafik di `results/b2_speedup.png`. `TOTAL_TASKS=8` membatasi jumlah tugas yang dapat berjalan sekaligus menjadi paling banyak delapan.

## B3: Word Count

Korpus berisi 15 artikel Wikipedia Indonesia dan 15 Inggris di `b3/data_wc/`. Jalankan pemeriksaan ukuran/token, benchmark median lima ulangan, dan grafik:

```powershell
& .\.venv\Scripts\python.exe .\b3\corpus_info.py .\b3\data_wc
& .\.venv\Scripts\python.exe .\b3\run_b3.py
& .\.venv\Scripts\python.exe .\b3\plot_b3.py
```

Untuk menjalankan mode secara langsung dari folder `b3/`:

```powershell
Push-Location .\b3
mpiexec -n 4 ..\.venv\Scripts\python.exe .\praktikum3_modified.py --mode thread
mpiexec -n 4 ..\.venv\Scripts\python.exe .\praktikum3_modified.py --mode process
Pop-Location
```

Sumber dan URL tiap artikel tercatat di `b3/data_wc/corpus_sources.csv` dan diringkas di `results/corpus_sources.md`. Artikel Wikipedia memakai lisensi CC BY-SA; cantumkan atribusi dan ketentuan lisensi jika teks korpus didistribusikan. Jika perlu membuat korpus baru, jalankan `b3/download_corpus.py` saat jaringan tersedia.

Eksperimen tambahan membuat salinan 30 file minimal 1 MB dan membandingkan kedua mode:

```powershell
& .\.venv\Scripts\python.exe .\b3\run_b3_large.py
```

Hasil median/std ada di `results/b3_large_results.csv`; salinan korpus ada di `b3/data_wc_large/` dan tidak mengubah data utama.

## Hasil dan Paket

Ringkasan hasil serta keterbatasan ada di `results/RINGKASAN.md`. Artefak analisis lainnya berada di `results/`, termasuk log mentah di `results/logs/`. Paket `tugas_hybrid_kode.zip` hanya berisi skrip Python, README, dan requirements; data korpus, venv, cache, dan hasil pengukuran tidak disertakan.

Untuk membangun ulang ringkasan dari tabel terkini, jalankan `& .\.venv\Scripts\python.exe .\build_summary.py`.