"""Simpan spesifikasi mesin dan versi runtime ke results/sysinfo.txt."""

import platform
import subprocess
import sys
from pathlib import Path

import mpi4py
import psutil
from mpi4py import MPI


def powershell_value(expression):
    """Ambil satu nilai dari Windows Management Instrumentation bila tersedia."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", expression],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "Tidak tersedia"
    return result.stdout.strip() or "Tidak tersedia"


def main():
    """Kumpulkan informasi runtime aktual dan simpan sebagai teks."""
    cpu_name = powershell_value(
        "(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name)"
    )
    os_name = powershell_value(
        "(Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty Caption)"
    )
    physical_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)
    ram_gib = psutil.virtual_memory().total / (1024**3)

    lines = [
        f"CPU: {cpu_name}",
        f"Core fisik: {physical_cores}",
        f"Thread/logical CPU: {logical_cores}",
        f"RAM terdeteksi: {ram_gib:.2f} GiB",
        f"OS: {os_name} ({platform.release()}, build {platform.version()})",
        f"Python: {sys.version}",
        f"mpi4py: {mpi4py.__version__}",
        f"MPI: {MPI.Get_library_version().strip()}",
    ]

    output_path = Path(__file__).resolve().parent / "results" / "sysinfo.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"Disimpan ke: {output_path}")


if __name__ == "__main__":
    main()