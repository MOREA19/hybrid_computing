# amdahl_a5.py - Perhitungan Hukum Amdahl untuk soal A5
# NIM 247006111176 -> A = 6 -> bagian serial = (5 + A)% = 11%
A = 6
s = (5 + A) / 100          # fraksi serial

def speedup(n):
    """Speedup teoretis Amdahl: S = 1 / (s + (1 - s) / n)"""
    return 1.0 / (s + (1.0 - s) / n)

print(f"A = {A} | bagian serial s = {s:.2%}")
print(f"{'Konfigurasi':32s} {'Worker':>7s} {'Speedup':>9s} {'Efisiensi':>10s}")
for nama, n in [("(a) 4 node x 8 core", 4 * 8),
                ("(b) 16 node x 8 core", 16 * 8)]:
    S = speedup(n)
    print(f"{nama:32s} {n:7d} {S:8.2f}x {S / n:10.2%}")

S_max = 1.0 / s
print(f"Batas maksimum teoretis (n -> tak hingga): {S_max:.2f}x")
print(f"Kenaikan speedup 32 -> 128 worker: {speedup(128) / speedup(32) - 1:.1%}")
print(f"Persentase batas maksimum yang tercapai: 32 worker = {speedup(32) / S_max:.1%}, 128 worker = {speedup(128) / S_max:.1%}")