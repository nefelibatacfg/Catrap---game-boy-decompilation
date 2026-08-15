#!/usr/bin/env python3
"""Decode and render all Catrap levels.

Faithful port of the game's level decoder ($27F8-$2865):
  - level data: 33 bytes per level at $51BE + level*33
  - each level is an 11x8 grid of 3-bit cells (88 cells, 264 bits)
  - cell value 7 is replaced by 0x10 (player/enemy spawn marker)
  - borders are wall (5)
"""
ROM = open('Catrap (USA).gb', 'rb').read()

def decode_level(level):
    """Port of the $27F8 decoder. Returns 8 rows of 11 cell values."""
    src = 0x51BE + level * 33
    data = ROM[src:src + 33]
    cells = []
    # bit reader: 3 bits per cell, MSB-first within each input byte
    bitpos = 0
    for _ in range(88):
        # extract 3 bits from the byte stream
        val = 0
        for _ in range(3):
            byte = data[bitpos >> 3]
            shift = 7 - (bitpos & 7)
            val = (val << 1) | ((byte >> shift) & 1)
            bitpos += 1
        cells.append(val)
    rows = []
    for r in range(8):
        row = cells[r * 11:(r + 1) * 11]
        rows.append(row)
    return rows

TILE = {0: '.', 1: '#', 2: '#', 3: '#', 4: '#', 5: '#', 6: '#', 7: '?', 0x10: '@'}

def render_level(level, width=1):
    rows = decode_level(level)
    lines = []
    for r in rows:
        line = "".join(TILE.get(v, '?') for v in r)
        lines.append(line)
    return lines

if __name__ == "__main__":
    import sys
    # decode and print levels 0-9 (or the range given on the command line)
    lo = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0
    hi = int(sys.argv[2], 0) if len(sys.argv) > 2 else lo + 10
    for lv in range(lo, min(hi, 110)):
        print(f"--- Level {lv} (data at ${0x51BE + lv*33:04X}) ---")
        for line in render_level(lv):
            print("   " + line)
