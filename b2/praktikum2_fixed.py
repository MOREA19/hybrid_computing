"""MODIFIED: versi MPI + ProcessPool dengan tugas yang dapat di-pickle."""

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from mpi4py import MPI


SAMPLES_PER_TASK = 260_000  # MODIFIED: ukuran tugas sesuai spesifikasi eksperimen.


def mc_task(task):
    """MODIFIED: fungsi top-level membuat tugas aman dikirim ke worker proses."""
    n_samples, seed = task
    rng = np.random.default_rng(seed)
    x = rng.random(n_samples)
    y = rng.random(n_samples)
    inside = (x * x + y * y) <= 1.0
    return int(inside.sum())  # MODIFIED: normalisasi hasil NumPy menjadi int Python.


def chunk_range(total, parts, index):
    """Bagi indeks tugas secara merata, termasuk sisa pembagian."""
    base = total // parts
    remainder = total % parts
    start = index * base + min(index, remainder)
    end = start + base + (1 if index < remainder else 0)
    return start, end


def parse_args():
    """MODIFIED: baca konfigurasi dari CLI, dengan fallback ke environment."""
    parser = argparse.ArgumentParser(description="Estimasi pi dengan MPI dan proses.")
    parser.add_argument(
        "--workers",
        type=int,
        default=int(os.environ.get("WORKERS", "4")),
        help="jumlah proses lokal per rank (default: env WORKERS atau 4)",
    )
    parser.add_argument(
        "--total-tasks",
        type=int,
        default=int(os.environ.get("TOTAL_TASKS", "8")),
        help="jumlah tugas global (default: env TOTAL_TASKS atau 8)",
    )
    args = parser.parse_args()
    if args.workers < 1 or args.total_tasks < 1:
        parser.error("--workers dan --total-tasks harus >= 1")
    return args


def main():
    """Jalankan sebagian tugas pada rank ini dan reduksi hasil ke root."""
    args = parse_args()
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    start, end = chunk_range(args.total_tasks, size, rank)
    tasks = [(SAMPLES_PER_TASK, 1234 + task_index) for task_index in range(start, end)]

    comm.Barrier()
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        local_hits = sum(executor.map(mc_task, tasks))
    elapsed = time.perf_counter() - started

    global_hits = comm.reduce(int(local_hits), op=MPI.SUM, root=0)
    global_samples = comm.reduce(len(tasks) * SAMPLES_PER_TASK, op=MPI.SUM, root=0)
    makespan = comm.reduce(elapsed, op=MPI.MAX, root=0)  # MODIFIED: waktu terpanjang antar-rank.

    if rank == 0:
        pi_estimate = 4.0 * global_hits / global_samples
        print(f"[MPI ranks={size}] tasks={args.total_tasks}, per_task={SAMPLES_PER_TASK}")
        print(f"Workers per rank: {args.workers}")
        print(f"Makespan       : {makespan:.6f} s")
        print(f"Total samples  : {global_samples:,}")
        print(f"Estimasi pi    : {pi_estimate:.6f}")


if __name__ == "__main__":
    main()