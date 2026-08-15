#!/usr/bin/env python3
"""Rebuild the ROM from the checked-in RGBDS sources (src/ + main.asm).

The src/ tree is the byte-exact disassembly of Catrap (USA).gb, already
generated - this script only assembles it. RGBDS is needed either in
tools/ or on PATH.

Usage: python build.py
"""
import os, subprocess, sys

TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
ORIGINAL = "Catrap (USA).gb"
OUTPUT = "catrap.gb"

def find(exe):
    p = os.path.join(TOOLS, exe)
    if os.path.exists(p):
        return p
    p2 = shutil.which(exe)
    if p2:
        return p2
    raise SystemExit(f"missing {exe} - put RGBDS in tools/ or on PATH")

def run(cmd):
    print(">", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
        raise SystemExit(f"command failed: {' '.join(cmd)}")
    return r

def main():
    rgbasm = find("rgbasm.exe" if os.name == "nt" else "rgbasm")
    rgblink = find("rgblink.exe" if os.name == "nt" else "rgblink")
    rgbfix = find("rgbfix.exe" if os.name == "nt" else "rgbfix")
    run([rgbasm, "-o", "main.o", "main.asm"])
    run([rgblink, "-o", OUTPUT, "main.o"])
    run([rgbfix, "-p", "0", "-v", OUTPUT])
    if os.path.exists(ORIGINAL):
        with open(OUTPUT, "rb") as f:
            built = f.read()
        with open(ORIGINAL, "rb") as f:
            orig = f.read()
        if built == orig:
            print(f"OK: byte-identical ({len(built)} bytes)")
        else:
            print(f"MISMATCH: built {len(built)} bytes, original {len(orig)} bytes")
    else:
        print(f"built {OUTPUT} ({os.path.getsize(OUTPUT)} bytes); no original ROM to compare")

if __name__ == "__main__":
    main()
