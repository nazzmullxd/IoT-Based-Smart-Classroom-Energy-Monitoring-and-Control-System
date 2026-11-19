"""Rebuild the bundled Wokwi visual: uv run --with ziglang==0.17.1 python tools/build_appliance.py"""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
chips = root / "apps/firmware/chips"
subprocess.run([
    sys.executable, "-m", "ziglang", "cc", "--target=wasm32-wasi",
    "-O2", "-s", "-nostdlib", "-ffreestanding", "-fno-builtin", "-Wl,--import-memory",
    # Zig's default 16 MiB stack exceeds Wokwi's 64-page (4 MiB) chip limit.
    "-Wl,-z,stack-size=65536",
    "-Wl,--export-table", "-Wl,--no-entry", "-Werror",
    "-o", str(chips / "appliance.chip.wasm"),
    str(chips / "appliance.chip.c"),
], check=True)
print("Built apps/firmware/chips/appliance.chip.wasm")
