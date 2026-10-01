# Transkripsi kode slide 21 (Praktikum 3) - logika TIDAK diubah.
from mpi4py import MPI
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import os, re, time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

DATA_DIR = "./data_wc"      # folder berisi banyak .txt
N_THREADS = 4

def count_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read().lower()
    # tokenisasi sederhana (huruf+angka)
    words = re.findall(r"[a-z0-9]+", txt)
    return Counter(words)

def chunk_range(total, parts, idx):
    base = total // parts; rem = total % parts
    start = idx * base + min(idx, rem)
    end   = start + base + (1 if idx < rem else 0)
    return start, end

if __name__ == "__main__":
    # siapkan daftar file (sama di semua rank)
    all_files = []
    if rank == 0:
        if not os.path.isdir(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
            # buat dummy jika kosong
            for k in range(1, 81):
                open(os.path.join(DATA_DIR, f"doc_{k:03d}.txt"), "w").write(
                    "Parallel and distributed computing. " * 200
                )
        all_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR)
                     if f.endswith(".txt")]
    # broadcast daftar file
    all_files = comm.bcast(all_files if rank == 0 else None, root=0)

    start, end = chunk_range(len(all_files), size, rank)
    my_files = all_files[start:end]

    t0 = time.time()
    local_counter = Counter()
    with ThreadPoolExecutor(max_workers=N_THREADS) as ex:
        futs = [ex.submit(count_file, p) for p in my_files]
        for fut in as_completed(futs):
            local_counter += fut.result()
    t1 = time.time()

    # kumpulkan semua counter ke root
    gathered = comm.gather(local_counter, root=0)

    if rank == 0:
        global_counter = Counter()
        for c in gathered:
            global_counter += c
        top = global_counter.most_common(10)
        print(f"[MPI ranks={size}] files={len(all_files)} threads/rank={N_THREADS}")
        print(f"Time (max per rank) ~ {t1-t0:.3f} s (aproksimasi)")
        print("Top-10 kata global:")
        for w, cnt in top:
            print(f"{w:>15s} : {cnt}")
