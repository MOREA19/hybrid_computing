# Audit B3

Audit kode dilakukan pada `b3/praktikum3_modified.py`; salinan lengkap dengan nomor baris ditampilkan di terminal saat audit.

## Penempatan timer dan kesetaraan

- `started = time.perf_counter()` berada di baris 78, sesudah `comm.Barrier()` pada baris 77.
- Pembuatan executor dimulai pada baris 91. Karena timer dimulai pada baris 78, konstruksi executor dan startup worker ikut terhitung.
- Timer berhenti pada baris 95 setelah blok `with` selesai. Penutupan executor ikut terhitung untuk thread maupun process.
- Mode thread memilih `ThreadPoolExecutor` di baris 81-83; mode process memilih `ProcessPoolExecutor` dan konteks `spawn` di baris 84-89. Keduanya melewati pola submit, tunggu hasil, dan batas timer yang sama pada baris 91-95. Jadi pengukuran kedua mode setara dalam cakupan waktu, walau biaya startup intrinsiknya memang berbeda.
- Kode tidak membuat mode process berjalan sebagai thread pada satu rank. Pemilihan executor selalu berdasarkan `args.mode` pada baris 81-89.

## Mengapa waktu satu rank hampir identik

CSV sebelumnya mencatat thread 1 rank = 0.227278 s dan process 1 rank = 0.227523 s. Perbedaan kecil ini tidak menunjukkan jalur kode yang sama: kedua durasi mencakup startup executor, dan pada korpus kecil overhead executor, penjadwalan, pembacaan file, serta penggabungan hasil dapat menutupi selisih kerja komputasi. Ini penjelasan yang masuk akal dari struktur kode, bukan penyebab yang dibuktikan secara terpisah.

## STOPWORDS

Set lengkap yang digunakan kode: `{"dan", "yang", "di", "the", "of", "and"}`. Keenam kata wajib tersedia. Filter diterapkan pada baris 29.