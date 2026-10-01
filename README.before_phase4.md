# Tugas Hybrid Computing

Benchmark ini menggunakan berkas sumber asli yang disimpan tanpa perubahan di `original/`. Versi eksperimen berada di `b1/`, `b2/`, dan `b3/`; semua angka dalam `results/` berasal dari eksekusi pada Windows 11 dan dicatat pada `results/sysinfo.txt`.

## Setup Windows

Python 3.11 dan Microsoft MPI runtime/SDK diperlukan. Buat ulang environment dari folder workspace:

```powershell
py -3.11 -m venv .\tugas_hybrid\.venv
& .\tugas_hybrid\.venv\Scripts\python.exe -m pip install numpy matplotlib pandas psutil mpi4py
mpiexec -help
& .\tugas_hybrid\.venv\Scripts\python.exe -c "from mpi4py import MPI; print(MPI.COMM_WORLD.Get_size()); print(MPI.Get_library_version())"
```

`mpiexec --version` tidak didukung Microsoft MPI. Gunakan `mpiexec -help` dan `MPI.Get_library_version()` untuk memeriksa versi. Jika MPI belum terpasang, pasang Microsoft MPI runtime (`msmpisetup.exe`) dan SDK (`msmpisdk.msi`), lalu buka terminal baru. Alternatifnya, jalankan di WSL dengan Open MPI terpasang dan buat venv Linux tersendiri.

Catat spesifikasi aktual mesin:

```powershell
& .\tugas_hybrid\.venv\Scripts\python.exe .\tugas_hybrid\sysinfo.py
```

## B1: Hybrid Pipeline

Generator menghasilkan 160 file di `b1/data`. Jalankan dari direktori B1 agar lokasi data sesuai:

```powershell
Push-Location .\tugas_hybrid\b1
..\.venv\Scripts\python.exe .\make_data_b1.py
Pop-Location
& .\tugas_hybrid\.venv\Scripts\python.exe .\tugas_hybrid\b1\run_b1.py
& .\tugas_hybrid\.venv\Scripts\python.exe .\tugas_hybrid\b1\plot_b1.py
```

Runner menjalankan satu warm-up dan tiga pengulangan untuk tiap kombinasi loader, worker, dan ukuran antrean. Median metrik disimpan di `results/b1_results.csv`; grafik ada di `results/b1_throughput.png`.

## B2: MPI + ProcessPool

Jalankan program asli untuk melihat error lambda, lalu runner versi perbaikan:

```powershell
& .\tugas_hybrid\.venv\Scripts\python.exe .\tugas_hybrid\b2\praktikum2_original.py
& .\tugas_hybrid\.venv\Scripts\python.exe .\tugas_hybrid\b2\run_b2.py
& .\tugas_hybrid\.venv\Scripts\python.exe .\tugas_hybrid\b2\plot_b2.py
```

Runner menguji 1, 2, dan 4 rank serta 1, 2, dan 4 worker lokal sebanyak tiga kali. Hasil median, speedup, efisiensi, dan penanda oversubscription tersimpan di `results/b2_results.csv`; grafik ada di `results/b2_speedup.png`. `TOTAL_TASKS=8` membatasi jumlah tugas independen global menjadi delapan.

## B3: Word Count

Unduh 15 artikel Wikipedia Indonesia dan 15 Inggris, lalu jalankan runner dan grafik:

```powershell
& .\tugas_hybrid\.venv\Scripts\python.exe .\tugas_hybrid\b3\download_corpus.py
& .\tugas_hybrid\.venv\Scripts\python.exe .\tugas_hybrid\b3\run_b3.py
& .\tugas_hybrid\.venv\Scripts\python.exe .\tugas_hybrid\b3\plot_b3.py
```

Mode tunggal untuk memeriksa top-10:

```powershell
Push-Location .\tugas_hybrid\b3
mpiexec -n 1 ..\.venv\Scripts\python.exe .\praktikum3_modified.py --mode thread
mpiexec -n 1 ..\.venv\Scripts\python.exe .\praktikum3_modified.py --mode process
Pop-Location
```

Teks korpus dan atribusinya berada di `b3/data_wc/`; `corpus_sources.csv` mencatat bahasa, judul, dan URL sumber. Artikel Wikipedia memakai lisensi CC BY-SA; cantumkan atribusi dan ketentuan lisensi saat mendistribusikan teksnya. Jika jaringan tidak tersedia, letakkan minimal 30 file `.txt` campuran Indonesia/Inggris di folder tersebut.

## Hasil dan Berkas

Tabel, analisis, dan batas eksperimen ada di `results/RINGKASAN.md`. CSV hasil dan PNG grafik disimpan di `results/`. Paket `tugas_hybrid_kode.zip` hanya memuat kode, sumber, dokumentasi, dan hasil ringkas; venv serta data teks tidak dimasukkan.

## Checklist Screenshot Laporan

1. Output `sysinfo.py` dan isi `results/sysinfo.txt`.
2. Perintah generator B1, jumlah 160 file, output runner, tabel markdown dari `plot_b1.py`, dan `b1_throughput.png`.
3. Traceback asli B2 yang menunjukkan `PicklingError` lambda serta salinan `results/b2_error.txt`.
4. Output runner B2, tabel speedup/efisiensi dari `plot_b2.py`, dan `b2_speedup.png`.
5. Output downloader B3 atau jumlah file dan `corpus_sources.csv`, output top-10 untuk masing-masing mode, tabel median dari `plot_b3.py`, dan `b3_comparison.png`.
6. `results/RINGKASAN.md` dan daftar isi `tugas_hybrid_kode.zip` untuk menunjukkan artefak akhir.