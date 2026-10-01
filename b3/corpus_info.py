"""MODIFIED: laporkan ukuran dan jumlah token setiap file korpus."""

import argparse
import re
from pathlib import Path


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")  # MODIFIED: samakan tokenisasi dengan penghitung kata B3.


def main():
    """MODIFIED: tampilkan statistik aktual korpus yang diberikan melalui CLI."""
    parser = argparse.ArgumentParser(description="Ringkasan ukuran dan token korpus teks.")
    parser.add_argument("directory", nargs="?", default="data_wc", help="direktori file teks")
    args = parser.parse_args()
    directory = Path(args.directory).resolve()
    if not directory.is_dir():
        parser.error(f"Direktori tidak ditemukan: {directory}")

    files = sorted(path for path in directory.iterdir() if path.is_file() and path.suffix.lower() == ".txt")
    total_bytes = 0
    total_words = 0
    print("nama\tukuran_KB\tjumlah_kata")
    for path in files:
        content = path.read_text(encoding="utf-8", errors="ignore").lower()
        size_bytes = path.stat().st_size
        word_count = len(TOKEN_PATTERN.findall(content))
        total_bytes += size_bytes
        total_words += word_count
        print(f"{path.name}\t{size_bytes / 1000:.3f}\t{word_count}")
    print(f"TOTAL_FILE\t{len(files)}")
    print(f"TOTAL_MB\t{total_bytes / 1_000_000:.6f}")
    print(f"TOTAL_KATA\t{total_words}")


if __name__ == "__main__":
    main()