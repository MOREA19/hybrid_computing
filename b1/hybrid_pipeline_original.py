# Transkripsi kode slide 19 (Praktikum 1) - logika TIDAK diubah.
import os, time, threading, queue, string
from concurrent.futures import ProcessPoolExecutor, as_completed

DATA_DIR = "./data"          # isi dg banyak file teks kecil (.txt)
Q_MAX = 32                   # backpressure queue
N_LOADER_THREADS = 2         # threads untuk I/O
N_WORKERS = 4                # proses untuk CPU-bound

def cpu_task(path):
    t0 = time.time()
    with open(path, "rb") as f:
        data = f.read()
    text = data.decode(errors="ignore").lower()
    alpha = sum(c in string.ascii_lowercase for c in text)
    latency = time.time() - t0
    return {"path": path, "alpha": alpha, "latency": latency}

def loader_worker(q: queue.Queue, files):
    for p in files:
        q.put(p)            # block jika penuh (backpressure)
    q.put(None)             # sentinel selesai

def run_pipeline():
    files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR)
             if os.path.isfile(os.path.join(DATA_DIR, f))]
    if not files:
        raise SystemExit("Folder ./data kosong - siapkan beberapa .txt dulu.")

    # bagi daftar file utk tiap loader thread
    chunks = [files[i::N_LOADER_THREADS] for i in range(N_LOADER_THREADS)]
    q = queue.Queue(maxsize=Q_MAX)

    # mulai loader threads
    loaders = []
    for ch in chunks:
        t = threading.Thread(target=loader_worker, args=(q, ch), daemon=True); t.start()
        loaders.append(t)

    done = 0
    results, lat = [], []
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        futs = set()
        while done < N_LOADER_THREADS:
            item = q.get()                  # block
            if item is None:
                done += 1; continue
            futs.add(ex.submit(cpu_task, item))

        for fut in as_completed(futs):
            r = fut.result()
            results.append(r); lat.append(r["latency"])

    total = time.time() - t0
    thr = len(results) / total if total > 0 else 0.0
    avg_lat = sum(lat)/len(lat) if lat else 0.0

    print(f"Files          : {len(results)}")
    print(f"Threads (I/O)  : {N_LOADER_THREADS} | Processes (CPU): {N_WORKERS}")
    print(f"Total time     : {total:.3f} s")
    print(f"Throughput     : {thr:.2f} files/s")
    print(f"Avg latency    : {avg_lat:.4f} s/file")
    for r in results[:3]:
        print(f"- {os.path.basename(r['path'])}: alpha={r['alpha']}, latency={r['latency']:.4f}s")

if __name__ == "__main__":
    run_pipeline()
