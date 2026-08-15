#!/usr/bin/env python3
"""Render all Catrap levels with the game's actual tiles.

Pipeline: decode the level grid (levels.py) -> build the tilemap exactly
like the game ($241F port, draw.py) -> paint the VRAM tiles.
The tilemap port is verified byte-exact against the running game.
"""
from PIL import Image
import levels, draw

ROM = open('Catrap (USA).gb', 'rb').read()

def build_vram():
    """Assemble the VRAM tile set exactly as the game loads it."""
    vram = bytearray(0x2000)
    # $640A -> $8000 (192 tiles)
    vram[0x0000:0x0C00] = ROM[0x640A:0x640A + 0x0C00]
    # $778A -> $8800 (66 tiles, overwrites the $640A set)
    vram[0x0800:0x0800 + 0x420] = ROM[0x778A:0x778A + 0x420]
    # $770A -> $8F80 (8 tiles)
    vram[0x0F80:0x0F80 + 0x080] = ROM[0x770A:0x770A + 0x080]
    # $7F92 -> $9740 (6 tiles)
    vram[0x1740:0x1740 + 0x060] = ROM[0x7F92:0x7F92 + 0x060]
    return vram

VRAM = build_vram()

PALETTE = [(255, 255, 255), (190, 190, 190), (110, 110, 110), (8, 8, 8)]

def render_tilemap(tmap, scale=4):
    """Paint a 24x32 tilemap with the VRAM tiles."""
    img = Image.new('RGB', (32 * 8 * scale, 24 * 8 * scale), (255, 255, 255))
    px = img.load()
    for r in range(24):
        for c in range(32):
            tid = tmap[r][c] & 0xFF
            base = tid * 16
            for y in range(8):
                lo = VRAM[base + y * 2]
                hi = VRAM[base + y * 2 + 1]
                for x in range(8):
                    bit = 7 - x
                    col = ((hi >> bit) & 1) * 2 + ((lo >> bit) & 1)
                    color = PALETTE[col]
                    for sy in range(scale):
                        for sx in range(scale):
                            px[(c * 8 + x) * scale + sx, (r * 8 + y) * scale + sy] = color
    return img

def render_level(lv, scale=3):
    grid = levels.decode_level(lv)
    tmap = draw.build_tilemap(grid)
    return render_tilemap(tmap, scale)

def render_contact(levels_list, cols=5, scale=2):
    imgs = [render_level(lv, scale) for lv in levels_list]
    w = cols * imgs[0].width
    rows = (len(imgs) + cols - 1) // cols
    h = rows * imgs[0].height
    sheet = Image.new('RGB', (w, h), (255, 255, 255))
    for i, im in enumerate(imgs):
        sheet.paste(im, ((i % cols) * im.width, (i // cols) * im.height))
    return sheet

if __name__ == "__main__":
    import sys
    # verify level 0 against the emulator's captured screen if present
    try:
        flat = {}
        for l in open('draw_out.txt'):
            p = l.split(': ')
            base = int(p[0], 16)
            for i, x in enumerate(p[1].split()):
                flat[base + i] = int(x, 16)
        mine = draw.build_tilemap(levels.decode_level(0))
        bad = sum(1 for r in range(19) for c in range(26)
                  if 0xC2C2 + r*32 + c in flat and flat[0xC2C2 + r*32 + c] != mine[r][c])
        print(f"port check vs game capture: {bad} mismatches in playfield")
    except FileNotFoundError:
        pass
    # render the requested levels
    lo = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0
    hi = int(sys.argv[2], 0) if len(sys.argv) > 2 else 110
    if hi - lo == 1:
        img = render_level(lo)
        img.save(f'level_{lo:02d}.png')
        print(f'saved level_{lo:02d}.png', img.size)
    else:
        sheet = render_contact(list(range(lo, hi)))
        sheet.save('catrap_levels_rendered.png')
        print('saved catrap_levels_rendered.png', sheet.size)
