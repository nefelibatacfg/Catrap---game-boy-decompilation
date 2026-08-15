"""
Catrap (USA) music decoder — walks the game's music command language and prints
the score (note names + octaves), using the engine semantics decoded from
$40FB-$443F (see sound.py for the full port).

Usage:
    python music.py                 # decode the title theme (state 1)
    python music.py <song> <state>  # e.g. python music.py 7 1

Command language (dispatcher $40FB):
    <note>      note byte; b = note-$A0 (>= $A0, len = [$FB] value, second byte
                ignored) or note-$50 ($50..$9F, second byte = len-1) or note
                (< $50, second byte = len-1). b == $49 = rest. Frequency
                divider = le16[$4460 + b*2] -> Hz = 131072/(2048-d).
    F0 <v>      envelope (NR12/22/32/42)
    F1 <w>      wave select (channel 3): $464F + w*16 -> wave RAM
    F2 <n>      loop setup: next $F3 repeats n times
    F3          loop back (2 data bytes skipped)
    F4 <lo> <hi>  jump
    F5 <lo> <hi>  call (return via $F6)
    F6          return to the $F5 continuation
    F7 <i>      slide spec: le16[$46EF + i*2] (pointer to 2-byte delta)
    F8 <v>      channel 1 sweep NR10
    F9 <v>      channel 4 value
    FA <v>      panning (NR51)
    FB <v>      note length for >= $A0 notes
    00          end of song
"""

NOTE_FREQ = 0x4460
F7_TABLE = 0x46EF
MUSIC_TABLE = 0x44F4
SFX_TABLE = 0x454C

ROM = None


def load(path='Catrap (USA).gb'):
    global ROM
    with open(path, 'rb') as f:
        ROM = f.read()


def rb(a):
    return ROM[a & 0x7FFF]


def rbw(a):
    return rb(a) | (rb(a + 1) << 8)


def freq_hz(d):
    """Game Boy frequency from the NR13/NR14 divider."""
    return 131072.0 / (2048 - d)


NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


import math


def note_name(d):
    hz = freq_hz(d)
    if hz <= 0:
        return '---'
    midi = round(69 + 12 * math.log2(hz / 440.0))
    n = NOTES[midi % 12]
    octv = midi // 12 - 1
    cents = round(1200 * math.log2(hz / (440 * 2 ** ((midi - 69) / 12))))
    if abs(cents) < 15:
        return f'{n}{octv}'
    return f'{n}{octv}{cents:+d}c'


def note_freq(b):
    return rbw(NOTE_FREQ + b * 2)


def decode_commands(addr, f7val=0, fb_len=8, depth=0, seen=None):
    """Walk the command stream at addr, yielding (addr, desc) tuples."""
    seen = seen if seen is not None else set()
    if depth > 12 or addr in seen:
        return
    a = addr
    f7 = f7val
    nlen = fb_len
    while a < 0x8000:
        if a in seen:
            break
        seen.add(a)
        cmd = rb(a)
        if cmd == 0:
            yield a, 'END'
            return
        if cmd & 0xF0 != 0xF0:
            # note
            if cmd >= 0xA0:
                b = cmd - 0xA0
                if b == 0x49:
                    yield a, f'REST {nlen}f  (note ${cmd:02X})'
                else:
                    yield a, f'{note_name(note_freq(b)):6s} {nlen:2d}f  (${cmd:02X} b=${b:02X} d=${note_freq(b):04X} {freq_hz(note_freq(b)):.1f}Hz)'
                a += 2  # second byte skipped for >= $A0 notes
            elif cmd >= 0x50:
                b = cmd - 0x50
                d = rb(a + 1)
                if b == 0x49:
                    yield a, f'REST {d}f  (note ${cmd:02X})'
                else:
                    yield a, f'{note_name(note_freq(b)):6s} {d:2d}f  (${cmd:02X} b=${b:02X} d=${note_freq(b):04X} {freq_hz(note_freq(b)):.1f}Hz)'
                a += 2
            else:
                b = cmd
                d = rb(a + 1)
                if b == 0x49:
                    yield a, f'REST {d}f  (note ${cmd:02X})'
                else:
                    yield a, f'{note_name(note_freq(b)):6s} {d:2d}f  (${cmd:02X} b=${b:02X} d=${note_freq(b):04X} {freq_hz(note_freq(b)):.1f}Hz)'
                a += 2
            continue
        if cmd == 0xF0:
            yield a, f'F0 env=${rb(a+1):02X}'
            a += 2
        elif cmd == 0xF1:
            yield a, f'F1 wave#${rb(a+1):02X}'
            a += 2
        elif cmd == 0xF2:
            yield a, f'F2 loop-x{rb(a+1)}'
            a += 2
        elif cmd == 0xF3:
            yield a, f'F3 loop-back (skip ${rb(a+1):02X} ${rb(a+2):02X})'
            a += 3
        elif cmd == 0xF4:
            tgt = rbw(a + 1)
            yield a, f'F4 jump ${tgt:04X}'
            a = tgt
        elif cmd == 0xF5:
            tgt = rbw(a + 1)
            yield a, f'F5 call ${tgt:04X}'
            yield from decode_commands(tgt, f7, nlen, depth + 1, seen)
            a += 3
        elif cmd == 0xF6:
            yield a, 'F6 return'
            return
        elif cmd == 0xF7:
            i = rb(a + 1)
            f7 = rbw(F7_TABLE + i * 2)
            yield a, f'F7 slide#${i:02X} -> ${f7:04X} (delta=${rbw(f7):04X})'
            a += 2
        elif cmd == 0xF8:
            yield a, f'F8 sweep=${rb(a+1):02X}'
            a += 2
        elif cmd == 0xF9:
            yield a, f'F9 ch4=${rb(a+1):02X}'
            a += 2
        elif cmd == 0xFA:
            yield a, f'FA pan={rb(a+1)}'
            a += 2
        elif cmd == 0xFB:
            nlen = rb(a + 1)
            yield a, f'FB len={nlen}'
            a += 2
        else:
            yield a, f'?? ${cmd:02X}'
            a += 1


def decode_song(state=1, ch=0, table=MUSIC_TABLE, title='music'):
    """Decode one channel's song for a state."""
    p = table + state * 8 + ch * 2
    addr = rbw(p)
    if addr == 0:
        print(f'  (no song)')
        return
    print(f'  channel {ch+1}: song @ ${addr:04X}')
    for a, desc in decode_commands(addr):
        print(f'    ${a:04X}: {desc}')


def decode_all(state=1):
    print(f'=== state {state} ({MUSIC_TABLE:04X} table) ===')
    for ch in range(4):
        decode_song(state, ch)
    print(f'=== state {state} SFX ($454C) ===')
    for ch in range(4):
        decode_song(state, ch, SFX_TABLE, 'sfx')


if __name__ == '__main__':
    import sys
    load()
    song = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    decode_all(song)
