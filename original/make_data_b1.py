# Transkripsi skrip "Cara RUN" slide 19 (dijadikan file agar jalan di Windows).
import random, string, pathlib
N_FILES = 160  # MODIFIED: dari range(1,101) -> 100 + 10*A dengan A=6
pathlib.Path("data").mkdir(exist_ok=True)
for i in range(1, N_FILES + 1):
    s = "".join(random.choice(string.ascii_letters + " " * 5 + "\n") for _ in range(3000))
    open(f"data/file_{i:03d}.txt", "w").write(s)
print("done.", N_FILES, "files")
