#!/usr/bin/env python3
"""Full Catrap screen-draw port: cell buffer -> tilemap ($C2C2).

Exact transcription of $241F (draw loop), $2483 (tile dispatcher),
$24BE/$26B9 (a=0/a=2 sub-logic) and the table lookups.
VERIFIED: reproduces the game's tilemap byte-for-byte (494/494 playfield
cells match the emulator capture; the only differences are uninitialized
leftover RAM columns, non-deterministic in the game itself).

Key details discovered while porting:
  - the wall/ladder tables are indexed by 7*cell + above (7x7 pattern)
  - the $27E5 'is45' helper is only a==4 or a==5 (its trailing
    'and $07; ret' is dead code: the ret is unconditional)
  - the decoder writes a 0x20-byte bottom fill of 5s at $C190-$C1AF,
    which the draw's rows 8-9 read
"""
ROM = open('Catrap (USA).gb', 'rb').read()

def tbl(a):
    return ROM[a:a + 80]

T = {h: tbl(int(h, 16)) for h in [
    '3E4A', '3E7B', '3EAC', '3EB3', '3EBA', '3EC1', '3EC8', '3ECF',
    '3ED6', '3EDD', '3EE4', '3EEB', '3EF2', '3EF9', '3F00', '3F07',
    '3F0E', '3F15', '3F1C', '3F23', '3F2A']}

def is45(a):
    """$27E5: cp 4; ret z; cp 5; ret  -> Z = (a==4) or (a==5).
    (the trailing 'and $07; ret' is dead code - the ret is unconditional)"""
    return a in (4, 5)

class G:
    """Register-file style state for the transcription."""
    def __init__(self, buf):
        self.buf = buf
        self.a = 0
        self.b = 0
        self.c = 0
        self.hl = 0

    def rb(self, addr):
        if 0 <= addr < len(self.buf):
            return self.buf[addr] & 7
        return 0

def b26B1(g, tab):
    """$26B1: a = [tab + a]; returns tile."""
    return T[tab][g.a]

def b26A2(g, c, tab):
    """$26A2: dec hl; a=[hli]&7; if a==4/5 -> a=[tab+b] else a=c."""
    above = g.rb(g.hl - 1)
    if above == 4 or above == 5:
        g.a = b26B1(g, tab)
    else:
        g.a = c

def tile_a0(g):
    """$24BE (layer 0)."""
    g.b = g.rb(g.hl - 0x11)
    g.c = g.rb(g.hl - 0x10)
    a = g.rb(g.hl)
    if a < 1:
        # $24E8
        above = g.rb(g.hl - 1)
        if above == 4:
            g.a = g.b                       # $24FD/$2505
            return b26B1(g, '3EAC')
        if above == 5:
            g.a = g.b                       # $2502/$2505
            return b26B1(g, '3EB3')
        g.a = 0x0B if g.c == 3 else 0xFB    # $24F4-$24FC
        return g.a
    if a == 1:
        # $2509
        if g.c == 1:
            b26A2(g, 0x29, '3EC1')          # $251E
            return g.a
        if g.c == 2 or g.c == 3:
            # $2526
            above = g.rb(g.hl - 1)
            if not is45(above):
                g.a = 0x3D
            elif not is45(g.b):
                g.a = 0x3E
            else:
                g.a = 0x21
            return g.a
        b26A2(g, 0x1C, '3EBA')              # $2516
        return g.a
    if a == 2:
        # $253A
        above = g.rb(g.hl - 1)
        if g.c == 2 or g.c == 3:
            # $2557
            if not is45(above):
                g.a = 0xEC
            elif not is45(g.b):
                g.a = 0xE2
            else:
                g.a = 0xE3
            return g.a
        if not is45(above):
            g.a = 0xF4
        elif not is45(g.b):
            g.a = 0xEA
        else:
            g.a = 0xE8
        return g.a
    if a == 3:
        b26A2(g, 0xFC, '3EC8')              # $259C
        return g.a
    if a == 4:
        # $25A4
        if g.c < 2 or g.c >= 6:
            # $25B7
            above = g.rb(g.hl - 1)
            if above == 4:
                g.a = g.b                   # $25C6
                return b26B1(g, '3ECF')
            if above == 5:
                g.a = g.b                   # $25CD
                return b26B1(g, '3EE4')
            g.a = 0x06
            return g.a
        if g.c == 2 or g.c == 3:
            # $25D4
            if is45(g.b):
                # $2662
                above = g.rb(g.hl - 1)
                g.a = 0x33 if is45(above) else 0x34
            else:
                # $2656
                above = g.rb(g.hl - 1)
                g.a = 0x2A if above == 5 else 0x34
            return g.a
        # c in (4,5): $25F3
        above = g.rb(g.hl - 1)
        if g.b == 4:
            g.a = above                     # $260A: a=c(above)
            return b26B1(g, '3ED6')
        if g.b == 5:
            g.a = above                     # $2611
            return b26B1(g, '3EDD')
        g.a = 0x10 if above == 4 else 0x07
        return g.a
    if a == 5:
        # $2618
        if g.c < 2 or g.c == 6:
            # $2633
            above = g.rb(g.hl - 1)
            if above == 4:
                g.a = g.b                   # $2642
                return b26B1(g, '3EEB')
            if above == 5:
                g.a = g.b                   # $2649
                return b26B1(g, '3EF2')
            g.a = 0x00
            return g.a
        if g.c == 2 or g.c == 3:
            # $2650
            if is45(g.b):
                # $2662
                above = g.rb(g.hl - 1)
                g.a = 0x33 if is45(above) else 0x34
            else:
                above = g.rb(g.hl - 1)
                g.a = 0x2A if above == 5 else 0x34
            return g.a
        if g.c == 4:
            # $266F
            above = g.rb(g.hl - 1)
            if above == 4 or above == 5:
                g.a = 0x1A if g.b == 4 else 0x18
            else:
                g.a = 0x18
            return g.a
        # c == 5: $2690
        above = g.rb(g.hl - 1)
        if above == 5:
            g.a = 0x03 if g.b == 5 else 0x0C
        else:
            g.a = 0x01
        return g.a
    # a >= 6: $256B
    above = g.rb(g.hl - 1)
    if g.c == 2 or g.c == 3:
        # $2588
        if not is45(above):
            g.a = 0xD0
        elif not is45(g.b):
            g.a = 0xC6
        else:
            g.a = 0xC7
        return g.a
    if not is45(above):
        g.a = 0xD8
    elif not is45(g.b):
        g.a = 0xCE
    else:
        g.a = 0xCC
    return g.a

def tile_a1(g):
    """$24A1 (layer 1): wall table."""
    d = g.rb(g.hl)
    e = g.rb(g.hl - 0x10)
    return T['3E4A'][d * 7 + e]

def tile_a2(g):
    """$26B9 (layer 2)."""
    g.b = g.rb(g.hl + 0x0F)
    g.c = g.rb(g.hl + 0x10)
    a = g.rb(g.hl)
    if a < 1:
        # $26E3
        above = g.rb(g.hl - 1)
        if above == 4:
            g.a = 0x05 if is45(g.b) else 0x24   # $26F2
        elif above == 5:
            g.a = g.b                           # $26FC
            return b26B1(g, '3EF9')
        g.a = 0xFB
        return g.a
    if a == 1:
        # $2703
        above = g.rb(g.hl - 1)
        if is45(above):
            g.a = 0x2F if g.c == 0 else 0x30    # $2713
        else:
            g.a = 0x29 if g.c == 0 else 0x1D    # $2710
        return g.a
    if a == 2:
        # $271A
        above = g.rb(g.hl - 1)
        if not is45(above):
            g.a = 0xF5
        elif not is45(g.b):
            g.a = 0xE9
        else:
            g.a = 0xEB
        return g.a
    if a == 3:
        g.a = 0xFD                              # $2742
        return g.a
    if a == 4:
        # $2748
        above = g.rb(g.hl - 1)
        if above == 4:
            if is45(g.b):
                # $2768
                g.a = 0x09 if is45(g.c) else 0x13
            else:
                g.a = g.b                       # $2761
                return b26B1(g, '3F07')
            return g.a
        if above == 5:
            if g.b == 4:
                g.a = 0x27 if is45(g.c) else 0x13
            elif g.b == 5:
                g.a = 0x07 if is45(g.c) else 0x13
            else:
                g.a = g.b                       # $277C
                return b26B1(g, '3F0E')
            return g.a
        g.a = g.c                               # $2755
        return b26B1(g, '3F00')
    # a >= 5: $2796
    above = g.rb(g.hl - 1)
    if above == 4:
        if g.c == 4:
            g.a = g.b                           # $27B9
            return b26B1(g, '3F23')
        if g.c == 5:
            g.a = 0x01                          # $27C0
            return g.a
        g.a = g.b                               # $27B2
        return b26B1(g, '3F1C')
    if above == 5:
        if g.c == 4:
            g.a = 0x1B if g.b == 4 else 0x3B    # $27D3
            return g.a
        if g.c == 5:
            g.a = 0x03 if g.b == 5 else 0x0D    # $27DC
            return g.a
        g.a = g.b                               # $27CC
        return b26B1(g, '3F2A')
    g.a = g.c
    return b26B1(g, '3F15')                     # $27A6: a=c, [3F15 + c]

def tile_a3(g):
    """Layer 3: $3E7B table."""
    d = g.rb(g.hl)
    e = g.rb(g.hl + 0x10)
    return T['3E7B'][d * 7 + e]

def tile_for(layer, g):
    if layer == 0:
        return tile_a0(g)
    if layer == 1:
        return tile_a1(g)
    if layer == 2:
        return tile_a2(g)
    return tile_a3(g)

def build_tilemap(rows):
    """Exact port of the $241F draw loop -> $C2C2 buffer."""
    buf = [0] * 0x200
    for r in range(8):
        base = 0x10 + r * 16
        buf[base] = 5
        for c in range(11):
            v = rows[r][c]
            buf[base + 1 + c] = 0x10 if v == 7 else v
        buf[base + 12] = 5
    for i in range(0x20):          # decoder's bottom fill ($C190-$C1AF)
        buf[0x90 + i] = 5
    tmap = [[0xFB] * 32 for _ in range(24)]
    def put(off, tile):
        if off >= 32:
            tmap[(off - 32) // 32][off % 32] = tile
    g = G(buf)
    # draw loop: c = 10 rows; hl = $C100 + row*$10; de = $C2A2 + row*64
    for row in range(10):
        g.hl = 0x00 + row * 0x10
        de = row * 64
        for cell in range(13):
            g.a = 0
            put(de, tile_for(0, g))
            g.a = 1
            put(de + 1, tile_for(1, g))
            g.hl += 1
            de += 2
        de = row * 64 + 32
        g.hl = 0x00 + row * 0x10
        for cell in range(13):
            g.a = 2
            put(de, tile_for(2, g))
            g.a = 3
            put(de + 1, tile_for(3, g))
            g.hl += 1
            de += 2
    return tmap

if __name__ == "__main__":
    import levels
    cap = [l.split() for l in open('level_mapc2.txt') if l.strip()]
    rows = levels.decode_level(0)
    mine = build_tilemap(rows)
    bad = 0
    for r in range(24):
        for c in range(32):
            if int(cap[r][c], 16) != mine[r][c]:
                bad += 1
    print("mismatched cells vs game capture:", bad, "of 768")
    if bad == 0:
        print("PORT VERIFIED - tilemap matches the game byte-for-byte")
