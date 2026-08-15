"""
Catrap (USA) sound engine port — byte-exact translation of $3F73-$443F.

Engine map:
  $3F73 MusicUpdate        : state $FFFB -> table $44F4 (8-byte entries, 4 pointers)
  $3FA0 MusicEntryStep     : start/stop a music channel
  $3FCE MusicUpdate2       : state $FFFD -> table $454C (sound effects)
  $3FFB MusicEntryStep2    : start/stop an SFX channel
  $4034 SoundChannelsUpdate: step all 8 channels (4 music @ $D55C + 4 SFX @ $D75C)
  $4078 SoundChannelStep   : per-channel frame step
  $40FB dispatcher         : music command interpreter
  $4329 note handler       : note decode + NR13/NR14 writes
  $440A ChannelOff         : silence a channel
  $442B ReadOperand        : read command operand, store advanced pointer
  $4434 WriteNR            : NR write gated by $FFCD (SFX muting)
  $443F WriteSlot          : write (counter, target-lo, target-hi) into a 3-byte slot

Music command language (dispatcher at $40FB):
  < $F0  note byte; offset b = note-$A0 (>= $A0, length = [$FB] value)
                            or note-$50 ($50..$9F, second byte = length-1)
                            or note (< $50, second byte = length-1)
          b == $49 -> rest (channel off). Frequency = le16[$4460 + b*2].
  $F0 <v>   envelope -> NR12/NR22/NR32/NR42 on next note (state+5)
  $F1 <w>   channel 3 wave: 16 bytes from $464F+w*16 -> $FF30 (wave RAM) / $D95C
  $F2 <n>   loop setup: slot counter = n at [state+7 + level*3] (level in state+6)
  $F3       loop back: target from the $F2 slot; count in state+6
  $F4 <lo> <hi>  jump
  $F5 <lo> <hi>  call: slot at [state+$20 + depth*3] = (3, return address)
  $F6       subroutine end: jump to the $F5 slot target
  $F7 <i>   freq/slide: [state+$38..39] = le16[$46EF + i*2]
  $F8 <v>   channel 1 sweep: NR10 = v
  $F9 <v>   channel 4: [state+$43] = v
  $FA <v>   panning: NR51 channel bits = v-class & mask
  $FB <v>   note length for >= $A0 notes (state+$48)
  $00       end of song

Channel state (0x80 bytes; music at $D55C+i*$80, SFX at $D75C+i*$80):
  +0    flags: bit0 = stopped, bit1 = SFX busy (music mirror)
  +1    note duration counter (0 -> fetch next command)
  +2    current note value
  +3..4 music data pointer
  +5    $F0 envelope value
  +6    $F3 loop level
  +7..  $F3 loop slots, 3 bytes: (counter, target lo, target hi)
  +$1F  $F5 call depth
  +$20.. $F5 slots, 3 bytes: (counter, target lo, target hi)
  +$38..39  $F7 value (pointer to 2-byte slide data)
  +$3A..3B  next-slide pointer (self-modifying)
  +$3C..3D  slide data pointer + 2
  +$3E..3F  slide delta (16-bit from $F7-value)
  +$3F..40  (entry2-entry1)*4 slide accumulator seed
  +$40..41  slide accumulator
  +$41..43  note frequency write buffers
  +$42..43  entry2 + $FFCF delta
  +$43      $F9 value (channel 4)
  +$44      $F8 sweep value (channel 1)
  +$45..46  $FA pan masks
  +$48      $FB note length
"""

NR = [0] * 0x40          # $FF10..$FF3F sound registers
FFCD = 0                 # NR write gate
FFCE = 0                 # $FFCE: last note byte
FFCF = 0                 # $FFCF: pitch delta byte

MUSIC_TABLE = 0x44F4
SFX_TABLE = 0x454C
NOTE_FREQ = 0x4460       # 16-bit little-endian freq dividers, indexed b*2
F7_TABLE = 0x46EF        # $F7 operands: pointers to 2-byte slide data
WAVE_TABLE = 0x464F      # 16-byte wave samples per $F1 index


def load(path='Catrap (USA).gb'):
    global ROM
    with open(path, 'rb') as f:
        ROM = f.read()


def rb(a):
    return ROM[a & 0x7FFF]


def rbw(a):
    return rb(a) | (rb(a + 1) << 8)


# --- $4434 WriteNR: write a to NR[c] unless muted ---
def write_nr(c, a):
    if FFCD == 0:
        NR[c] = a & 0xFF


# --- $440A ChannelOff ---
def channel_off(c):
    if c == 0x1B:                       # channel 3: NR33 = 0
        write_nr(c + 1, 0x00)
    else:
        write_nr(c + 1, 0x08)           # volume/envelope = 0
        c += 2
        if c != 0x23:
            c += 1
        write_nr(c, 0x80)               # trigger


# --- $442B ReadOperand: advance de past operand, store pointer at [hl-1..hl] ---
def read_operand(st, de, hl):
    de += 1
    a = rb(de)
    de += 1
    st[hl] = de >> 8
    st[hl - 1] = de & 0xFF
    return de, a


# --- $443F WriteSlot: [hl + a*3 + 1] = b; [hl + a*3 + 2..3] = de; [hl] += 1 ---
def write_slot(st, hl, a, b, de):
    st[hl] = (st[hl] + 1) & 0xFF
    i = hl + a * 3 + 1
    st[i] = b
    st[i + 1] = de & 0xFF
    st[i + 2] = de >> 8


# --- $3FA0 MusicEntryStep ---
def music_entry_step(p, st, c):
    global FFCD
    if rbw(p) == 0:
        st[0] |= 1                      # stopped
        FFCD = st[0] & 0xFE
        channel_off(c - 1)
    else:
        st[0] &= ~1
        st[1] = 0
        st[2] = 0
        st[3] = rb(p)
        st[4] = rb(p + 1)
        st[5] = 0
        st[0x1F] = 0


# --- $3FFB MusicEntryStep2 (SFX) ---
def sfx_entry_step(p, st, c, mirror):
    global FFCD
    if rbw(p) == 0:
        st[0] |= 1
        FFCD = st[0] & 0xFE
        mirror[0] &= ~2                 # clear SFX-busy in the music state
        if mirror[0] & 1:
            channel_off(c - 1)
    else:
        st[0] &= ~1
        mirror[0] |= 2                  # SFX busy: mutes the music channel
        st[2] = 0
        st[3] = rb(p)
        st[4] = rb(p + 1)
        st[5] = 0


# --- $3F73 MusicUpdate ---
def music_update(fb, fc):
    if fb == fc:
        return fc
    base = MUSIC_TABLE + fb * 8
    c = 0x12
    for i in range(4):
        music_entry_step(base + i * 2, CHANS[i], c)
        c += 5
    return fb


# --- $3FCE MusicUpdate2 ---
def sfx_update(fd, fe):
    if fd == fe:
        return fe
    base = SFX_TABLE + fd * 8
    c = 0x12
    for i in range(4):
        sfx_entry_step(base + i * 2, SFX_CHANS[i], c, CHANS[i])
        c += 5
    return fd


# --- $4034 SoundChannelsUpdate ---
def sound_channels_update():
    for i in range(4):
        sound_channel_step(CHANS[i], 0x11 + i * 5)
    for i in range(4):
        sound_channel_step(SFX_CHANS[i], 0x11 + i * 5)


# --- $4078 SoundChannelStep ---
def sound_channel_step(st, c):
    global FFCD
    if st[0] & 1:
        return
    FFCD = st[0] & 0xFE
    if st[1] == 0:
        dispatcher(st, c)
        return
    if c == 0x1B:                       # channel 3 wave volume while counting
        v = st[1]
        if v < 5:
            write_nr(c + 1, 0x60 if v < 3 else 0x40)
    st[1] = (st[1] - 1) & 0xFF
    # slide / note tail
    if st[0x3C] == 0:
        return
    if c == 0x20:
        return
    b = st[0x3D]
    if b != 0:
        de = st[0x3E] | (st[0x3F] << 8)
        neg = b & 0x80
        if neg:
            de = (-de) & 0xFFFF
            b = (-b) & 0xFF
        hl = (de * b) & 0xFFFF           # delta * count (mod 65536)
        acc = st[0x40] | (st[0x41] << 8)
        acc += hl
        carry = 1 if acc > 0xFFFF else 0
        acc &= 0xFFFF
        st[0x40] = acc & 0xFF
        st[0x41] = acc >> 8
        if c == 0x16:
            print(f'  ch2 slide: delta=${de:04X} b=${b:02X} hl=${hl:04X} acc=${acc:04X} w=${st[0x41]:02X}')
        write_nr(c + 2, st[0x41])
        st[0x42] = (st[0x42] + (0xFF if neg else 0) + carry) & 0xFF
        write_nr(c + 3, st[0x42])
    st[0x3C] = (st[0x3C] - 1) & 0xFF
    if st[0x3C] != 0:
        return
    de = st[0x3A] | (st[0x3B] << 8)      # next slide spec
    st[0x3C] = rb(de)
    de += 1
    st[0x3D] = rb(de)
    de += 1
    st[0x3B] = de >> 8
    st[0x3A] = de & 0xFF


# --- $40FB music command dispatcher ---
def dispatcher(st, c):
    global FFCD
    de = st[3] | (st[4] << 8)
    hl = 4
    while True:
        cmd = rb(de)
        if cmd == 0:
            # end of song: store pointer, stop channel
            st[4] = de >> 8
            st[3] = de & 0xFF
            if FFCD == 0:
                channel_off(c)
            return
        if cmd & 0xF0 != 0xF0:
            note_handler(st, c, de, hl, cmd)
            return
        if cmd == 0xFC or cmd == 0xFD or cmd == 0xFE or cmd == 0xFF:
            return                          # ignored
        if cmd == 0xF3:
            lvl = st[6]
            if lvl != 0:
                lvl -= 1
                slot = 7 + lvl * 3
                st[slot] = (st[slot] - 1) & 0xFF
                if st[slot] == 0:
                    st[6] = (st[6] - 1) & 0xFF
                    de += 1
                else:
                    de = st[slot + 1] | (st[slot + 2] << 8)
            continue
        if cmd == 0xF4:
            de = rb(de + 1) | (rb(de + 2) << 8)
            continue
        if cmd == 0xF5:
            tgt = rb(de + 1) | (rb(de + 2) << 8)
            de += 3
            depth = st[0x1F]
            if depth != 8:
                write_slot(st, hl + 0x1B, depth, 3, de)
                de = tgt
            continue
        if cmd == 0xF6:
            depth = st[0x1F]
            if depth != 0:
                st[0x1F] = depth - 1
                slot = 0x20 + (depth - 1) * 3
                st[slot] = (st[slot] - 1) & 0xFF
                if st[slot] == 0:
                    st[6] = (st[6] - 1) & 0xFF
                    de += 1
                else:
                    de = st[slot + 1] | (st[slot + 2] << 8)
            continue
        de, a = read_operand(st, de, hl)
        if cmd == 0xF0:
            st[5] = a                       # envelope
        elif cmd == 0xF1:
            if c == 0x1B:
                off = WAVE_TABLE + a * 16
                if FFCD == 0:
                    for i in range(16):
                        NR[0x20 + i] = rb(off + i)
                else:
                    for i in range(16):
                        NR[0x20 + i] = rb(off + i)
                NR[0x1A] = 0x80             # wave DAC on
        elif cmd == 0xF2:
            if st[6] != 8:
                write_slot(st, hl, st[6], a, de)
        elif cmd == 0xF7:
            v = rbw(F7_TABLE + a * 2)
            st[0x38] = v & 0xFF
            st[0x39] = v >> 8
        elif cmd == 0xF8:
            if c == 0x11:
                if FFCD == 0:
                    write_nr(0x10, a)
                st[0x44] = a
        elif cmd == 0xF9:
            if c == 0x20:
                st[0x43] = a
        elif cmd == 0xFA:
            if c == 0x11:
                m = 0x11
            elif c == 0x16:
                m = 0x22
            elif c == 0x1B:
                m = 0x44
            else:
                m = 0x88
            if a >= 3:
                v = 0xFF
            elif a == 2:
                v = 0x0F
            elif a == 1:
                v = 0xF0
            else:
                v = 0x00
            v &= m
            st[0x45] = (~m) & 0xFF
            st[0x46] = v
            NR[0x25] = (NR[0x25] & st[0x45]) | st[0x46]
        elif cmd == 0xFB:
            st[0x47] = a                   # note length


# --- $4329 note handler ---
def note_handler(st, c, de, hl, note):
    global FFCD
    global FFCE, FFCF
    FFCF = 0
    FFCE = note
    de += 1                              # past the note byte
    if note >= 0xA0:
        b = note - 0xA0
        dur = st[0x47]
    elif note >= 0x50:
        b = note - 0x50
        dur = rb(de)
        de += 1
    else:
        b = note
        dur = rb(de)
        de += 1
    st[2] = b
    st[1] = (dur - 1) & 0xFF
    st[3] = de & 0xFF
    st[4] = de >> 8
    if FFCD != 0:
        return
    if b == 0x49:
        channel_off(c)
        return
    # slide spec from the $F7 value: [state+$3A..3B] = value+2, [state+$3C..3D] = data
    d2 = st[0x38] | (st[0x39] << 8)
    st[0x3A] = (d2 + 2) & 0xFF
    st[0x3B] = (d2 + 2) >> 8
    st[0x3C] = rb(d2)
    st[0x3D] = rb(d2 + 1)
    # envelope
    write_nr(c + 1, st[5])
    if c == 0x20:
        return                             # channel 4: no frequency
    # frequency: sliding 4-byte window at $4460 + (b-1)*2
    x = NOTE_FREQ + (b - 1) * 2
    e1 = rbw(x)
    e2 = rbw(x + 2)
    diff4 = ((e2 - e1) & 0xFFFF) * 4 & 0xFFFF
    st[0x3E] = diff4 & 0xFF
    st[0x3F] = diff4 >> 8
    freq = (e2 + FFCF) & 0xFFFF
    st[0x40] = 0
    st[0x41] = freq & 0xFF
    st[0x42] = freq >> 8
    if c == 0x1B:
        # channel 3: wave DAC on, NR33 = $20, freq lo at NR34, hi+trigger at $FF1E
        write_nr(0x1A, 0x00)
        write_nr(0x1A, 0x80)
        write_nr(0x1C, 0x20)
        write_nr(c + 2, freq & 0xFF)
        write_nr(c + 3, 0x80 | (freq >> 8))
    else:
        write_nr(c + 2, freq & 0xFF)
        write_nr(c + 3, 0x80 | (freq >> 8))
