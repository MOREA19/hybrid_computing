# Checklist Screenshot

Jalankan perintah berurutan dari folder `tugas_hybrid`. Untuk gambar, buka PNG saat tabel terminal terlihat.

1. **Spesifikasi sistem**

   ```powershell
   type .\results\sysinfo.txt
   ```

   Pastikan CPU dan `Core fisik: 6` serta `Thread/logical CPU: 12` terlihat.

2. **B1 original, format slide 19**

   ```powershell
   Push-Location .\b1
   ..\.venv\Scripts\python.exe .\hybrid_pipeline_original.py
   Pop-Location
   ```

   Tampilkan jumlah file, thread/worker bawaan, total time, throughput, dan latency.

3. **Tabel dan grafik B1**

   ```powershell
   Get-Content .\results\b1_tables.md
   Start-Process .\results\b1_throughput.png
   ```

   Tampilkan semua konfigurasi, lima terbaik, agregat, selisih Q_MAX/noise, serta dua panel grafik dengan batas 6 dan 12.

4. **Error lambda B2 original**

   ```powershell
   Push-Location .\b2
   mpiexec -n 1 ..\.venv\Scripts\python.exe .\praktikum2_original.py
   Pop-Location
   ```

   Tampilkan pesan lengkap `PicklingError` yang menyebut `<lambda>`.

5. **B2 fixed, empat rank dan empat worker**

   ```powershell
   Push-Location .\b2
   mpiexec -n 4 ..\.venv\Scripts\python.exe .\praktikum2_fixed.py --workers 4
   Pop-Location
   ```

   Tampilkan jumlah task, worker/rank, makespan, total sampel, dan estimasi pi.

6. **Tabel dan grafik B2**

   ```powershell
   Get-Content .\results\b2_table.md
   Start-Process .\results\b2_speedup.png
   ```

   Pastikan `n`, speedup, efisiensi, oversubscription, total_processes, dan batas 6/12 terlihat.

7. **Inventaris korpus**

   ```powershell
   & .\.venv\Scripts\python.exe .\b3\corpus_info.py .\b3\data_wc
   ```

   Tampilkan nama/ukuran/token setiap file serta total file, MB, dan kata.

8. **B3 thread dan process dengan Top-10**

   ```powershell
   Push-Location .\b3
   mpiexec -n 4 ..\.venv\Scripts\python.exe .\praktikum3_modified.py --mode thread
   mpiexec -n 4 ..\.venv\Scripts\python.exe .\praktikum3_modified.py --mode process
   Pop-Location
   ```

   Untuk tiap perintah tampilkan mode, waktu maksimum, dan kesepuluh kata beserta frekuensinya.

9. **Tabel dan grafik B3**

   ```powershell
   Get-Content .\results\b3_table.md
   Start-Process .\results\b3_compare.png
   ```

   Tampilkan median/std, speedup relatif 1 rank, rasio process/thread, dan grafik perbandingan.