"""
Catrap (USA) gameplay engine port — byte-exact translation of $062C-$0665,
$0B5E-$0C0B, $27F8-$2876, $2876-$2F95 (TaskGame), $325B-$34C1 (TaskInput).

The port models the game's observable state: map, player, entities, objects,
flags. Drawing (VRAM/OAM) is stubbed. See the docstring map in each section.

Memory layout (same as the game):
  $C100-$C1FF  map 16x8 cells (playfield 11 cols at $C110; 5 = borders)
               cell: 0 empty, 1 wall, 2 block, 3 ladder, 4 platform,
                     5 wall, 6 special (hole), 7 enemy, 0x10 player
  $C7F7+       entity table, 3-byte entries (type, state, spare)
  $DABD+       object slots (0x20 x10): [0]=type [1]=timer [2]=dir
               [3..4]=cell ptr [+5]=frame [+$18..]=anim data
  $DADD+       HUD anim slots (0x20 x14)
  HRAM:
    FFD7/FFD8  player pos: row<<4 | col<<4 (cell = (FFD8>>4) | FFD7)
    FFD5       player state (bit0 facing, bits1-4 mode)
    FFD3/FFD4  anim timers; FFE1 action flag; FFE3/E4/E5 scratch
    FFA1       anim busy; FFA2 draw busy; FFBB anim phase; FFBC input lock
    FFA4       game state: 0 = play, 1 = cleared, $10 = next level
    FF8A/FF8B  joypad current/edges (bit0 A, 1 B, 2 Sel, 3 Start,
               4 R, 5 L, 6 U, 7 D)
    FFB0/FFAA  scroll state; FF43 SCX; FFB1/FFB2 HUD cursor
    FFB3       level flip; FFB4 entity type; FFB5/FFB6 entity pos
    FFB7/FFB8  entity index; FF9D push cell; FFDB/FFDC level flags
    FFA3       level number; FFA4 game state
  $DA5B       level flip marker ($FF = none); $DA5C same
  $DA5D       player flip/state; $DA5F/$DA60 spawn pos; $DA79 ground row
"""

ROM = None
mem = None


def rb(a):
    return mem[a & 0xFFFF]


def wb(a, v):
    mem[a & 0xFFFF] = v & 0xFF


def rbw(a):
    return rb(a) | (rb(a + 1) << 8)


def wbw(a, v):
    wb(a, v & 0xFF)
    wb(a + 1, (v >> 8) & 0xFF)


def load(path='Catrap (USA).gb'):
    global ROM
    try:
        with open(path, 'rb') as f:
            ROM = f.read()
    except FileNotFoundError:
        raise SystemExit(
            f"missing '{path}' - this is the playable port of the original game;\n"
            "place your own dump of 'Catrap (USA).gb' next to game.py to run it.")


def rom(a):
    return ROM[a & 0x7FFF]


# ===========================================================================
# cell helpers ($2D8F/$2E14/$2E1B/$2D7C/$2D72/$2D81/$2D88/$2D5B)
# ===========================================================================
# position: h = row<<4, l = col<<4 ; cell offset = (l>>4) | h


def cur_hl():
    """$2E14: hl = FFD7<<8 | FFD8."""
    return (rb(0xFFD7) << 8) | rb(0xFFD8)


def set_pos(h, l):
    wb(0xFFD7, h)
    wb(0xFFD8, l)


def add_pos(de):
    """$2E1B: position += de."""
    hl = (cur_hl() + (de & 0xFFFF)) & 0xFFFF
    set_pos(hl >> 8, hl & 0xFF)


def cell_off(hl):
    """$2D8F's offset: swap(l) | h  (l = col<<4, h = row<<4)."""
    l = hl & 0xFF
    return (((l & 0x0F) << 4) | ((l & 0xF0) >> 4)) | ((hl >> 8) & 0xFF)


def rd_cell(hl):
    return mem[0xC100 + cell_off(hl)]


def wr_cell(hl, v):
    mem[0xC100 + cell_off(hl)] = v & 0xFF


def rd_cur():
    return rd_cell(cur_hl())


def cur_off():
    return cell_off(cur_hl())


def cell_clear_player():
    """Clear the player bit at the current cell ($2D61-$2D6F)."""
    e = rb(0xFFD8) | rb(0xFFD7)           # col | row
    mem[0xC100 + e] &= 7


def set_state(state):
    """$2D5B: FF D5 = state; spawn entity 7; clear the player's cell."""
    wb(0xFFD5, state)
    entity_spawn(7, state)
    cell_clear_player()


def cell_below(hl):
    return mem[hl + 0x10]


# ===========================================================================
# entity table ($2DFF/$2DF5/$2DBE/$2DC7)
# ===========================================================================
def entity_de():
    """$2DFF: de = $C7F7 + ((FFB8&3)<<8 | FFB7) * 3."""
    idx = ((rb(0xFFB8) & 3) << 8) | rb(0xFFB7)
    return 0xC7F7 + idx * 3


def entity_next():
    """$2DF5: bump the index (inc FFB7, carry into FFB8)."""
    v = (rb(0xFFB7) + 1) & 0xFF
    wb(0xFFB7, v)
    if v == 0:
        wb(0xFFB8, (rb(0xFFB8) + 1) & 0xFF)
    return rb(0xFFB7) == 0 and rb(0xFFB8) == 0


def entity_write(etype, state, cell=0):
    """$2DBE: [0]=etype [1]=state [2]=cell; bump; [3]=0. Returns the slot."""
    de = entity_de()
    mem[de] = etype
    mem[de + 1] = state
    mem[de + 2] = cell
    entity_next()
    mem[de + 3] = 0
    return de


def entity_spawn(etype, state):
    entity_write(etype, state)


def state_cell():
    # the player's current cell & 7
    return rd_cur() & 7


# ===========================================================================
# object update ($2E37/$379F/$2F86/$2DAC/$2D98/$293A)
# ===========================================================================
def f_2f86(hl, frame):
    """$2F86: a = [le16([hl-1],[hl]) + frame*5] (the anim command)."""
    ptr = (rb(hl) << 8) | rb(hl - 1)
    return rom((ptr + frame * 5) & 0xFFFF)


def tile_lookup(obj, frame):
    """$2E61-$2E84: the anim-table ptr for the state -> [obj+6..9]."""
    t = rb(obj)                                  # the object type
    base = rom(0x384B + t * 2) | (rom(0x384B + t * 2 + 1) << 8)
    a = base + (frame & 0xFE)
    c = rom(a & 0xFFFF)
    b = rom((a + 1) & 0xFFFF)
    wb(obj + 6, c)
    wb(obj + 7, b)
    wb(obj + 8, 0xFF)
    wb(obj + 9, 1)


def anim_tick(obj):
    """$2E85-$2EE3: the sprite regs + the anim countdown; sets E1 = $80."""
    wb(0xFFC8, (rb(obj + 4) - 4) & 0xFF)
    wb(0xFFC9, (rb(obj + 5) - rb(0xFF43) + 8) & 0xFF)
    a = rb(obj + 9)
    if (a + 1) & 0xFF == 0:
        return
    wb(obj + 9, (a - 1) & 0xFF)
    if rb(obj + 9) == 0:
        # $2EA4: the frame-advance loop (jr 2EA4 at $2EBC)
        while True:
            wb(obj + 8, (rb(obj + 8) + 1) & 0xFF)
            f = rb(obj + 8)
            cmd = f_2f86(obj + 7, f)
            if cmd == 0:
                wb(obj + 8, 0xFF)
                continue                    # jr z $2EB8 -> jr $2EA4
            if cmd == 0xFF or cmd < 0xF0:
                break                       # jr z/c $2EBE: the entry copy
            wb(obj + 8, (cmd & 0x0F) - 1)   # $2EB6: the frame goto
        # $2EBE: the 5-byte entry copy
        tbl = (rb(obj + 7) << 8) | rb(obj + 6)
        for i in range(5):
            wb(obj + 9 + i, rom((tbl + f * 5 + i) & 0xFFFF))
    # $2EC9: the completion check ([obj+9] == 1)
    a = rb(obj + 9)
    if (a - 1) & 0xFF == 0:
        cmd2 = f_2f86(obj + 7, (rb(obj + 8) + 1) & 0xFF)
        if cmd2 == 0 or cmd2 >= 0xF0:
            wb(obj + 0x0E, 0x80)                 # the E1 flag!


def object_update(obj, override):
    """$2E37: the object update (the type change + the state-change lookup)."""
    wb(0xFFF3, override)
    de = obj
    wb(obj + 0x0E, 0)
    hl = obj
    a = rb(hl); hl += 1
    wb(0xFFCB, a)
    if a == 0xFF:
        return
    c = a
    a = rb(hl); hl += 1                          # [obj+1]
    if a != c:
        hl -= 1
        wb(hl, c); hl += 1                       # [obj+1] = c
        a = rb(hl); hl += 1                      # [obj+2]
        wb(0xFFCA, a)
        c = a
        wb(hl, a); hl += 1                       # [obj+2] = c; hl = obj+3
        tile_lookup(obj, c)
    else:
        a = rb(hl); hl += 1                      # [obj+2]
        wb(0xFFCA, a)
        c = a
        a = rb(hl); hl += 1                      # [obj+3]
        if a != c:
            hl -= 1
            wb(hl, c); hl += 1                   # [obj+3] = c; hl = obj+4
            tile_lookup(obj, c)
    anim_tick(obj)


def object_update_simple(obj, override):
    """$379F: the object update without the type-change check (the FFBB==1 anim)."""
    wb(0xFFF3, override)
    de = obj
    wb(obj + 0x0E, 0)
    hl = obj
    a = rb(hl); hl += 1
    wb(0xFFCB, a)
    if a == 0xFF:
        return
    hl += 1                                      # skip [obj+1]
    a = rb(hl); hl += 1                          # [obj+2]
    wb(0xFFCA, a)
    c = a
    a = rb(hl); hl += 1                          # [obj+3]
    if a != c:
        hl -= 1
        wb(hl, c); hl += 1                       # [obj+3] = c
        # $37B9+: the anim-table scan
        t = rb(obj)
        base = rom(0x384B + t * 2) | (rom(0x384B + t * 2 + 1) << 8)
        p = base + (c & 0xFE)
        cl = rom(p & 0xFFFF)
        bh = rom((p + 1) & 0xFFFF)
        wb(obj + 6, cl)
        wb(obj + 7, bh)
        bc = cl | (bh << 8)                      # the anim table ptr
        while True:                              # $37D8: find the end entry
            v = rom(bc & 0xFFFF)
            if v == 0:
                wb(obj + 8, 0xFF)                # $37EF: [obj+8] = $FF
                break
            if v >= 0xF0:
                break                            # $37EB: [obj+8] unchanged
            bc = (bc + 5) & 0xFFFF
        wb(obj + 9, 1)                           # $37F3
        wb(obj + 0x14, v & 0x0F if v >= 0xF0 else 0xFF)  # $37F9
    # $3812: the anim machine
    a = rb(obj + 9)
    if (a + 1) & 0xFF == 0:                      # [obj+9] == $FF
        return
    wb(obj + 9, (a - 1) & 0xFF)
    if rb(obj + 9) != 0:
        pass
    else:
        old8 = rb(obj + 8)
        wb(obj + 8, (old8 - 1) & 0xFF)
        if old8 == 0:
            wb(obj + 8, rb(obj + 0x14))          # the reload
            old8 = rb(obj + 8)
        frame = old8
        cmd = f_2f86(obj + 7, frame)
        tbl = (rb(obj + 7) << 8) | rb(obj + 6)
        for i in range(5):
            wb(obj + 9 + i, rom((tbl + frame * 5 + i) & 0xFFFF))
    # $3837: the completion check
    if rb(obj + 9) == 1 and rb(obj + 8) == 0:
        wb(obj + 0x0E, 0x80)                     # the E1!


def obj_dac():
    """$2DAC: the FFD3 object, then the DA5B object if present."""
    object_update(0xFFD3, 0)
    if rb(0xDA5B) != 0xFF:
        object_update(0xDA5B, 0x10)


def wait_1frame(b):
    """$2D98: b frames of (yield + the object update)."""
    for _ in range(b):
        yield
        obj_dac()


def wait_293A():
    """$293A: 1-frame wait; while FFA1: gravity + 1-frame wait."""
    while True:
        yield from wait_1frame(1)
        if rb(0xFFA1) == 0:
            return
        gravity()


def joypad_read(buttons, dpad, old8a, old8b, last8c, debounce):
    # $01D0+$01F1: debounce + read. Returns (FF8A, FF8B, FF8C, FF8D).
    if old8b == 0 and old8a != 0:
        if old8a == last8c:
            debounce -= 1
            if debounce != 0:
                return old8a, old8b, last8c, debounce
            debounce = 7
        else:
            last8c = old8a
            debounce = 0x18
    d = ((~dpad) & 0x0F) << 4
    b = (~buttons) & 0x0F
    new = d | b
    edge = (old8a ^ new) & new
    return new, edge, last8c, debounce


# ===========================================================================
# object slots ($2CC8/$2C99/$2CA1)
# ===========================================================================
def find_slot():
    """$2CC8: first free slot at $DABD; carry if none."""
    for i in range(10):
        s = 0xDABD + i * 0x20
        if mem[s] == 0:
            return s
    return None


def obj_spawn_2ca1(slot, state, timer, dirc, cellptr):
    """$2CA1: [0]=state [1]=timer [2]=dir [3..4]=cellptr; [+$16]=0x0B."""
    mem[slot] = state
    mem[slot + 1] = timer
    mem[slot + 2] = dirc
    mem[slot + 3] = cellptr & 0xFF
    mem[slot + 4] = cellptr >> 8
    mem[slot + 0x16] = 0x0B


# ===========================================================================
# level decode ($27F8)
# ===========================================================================
def level_decode(level):
    """Decode level into $C100. Returns the player spawn offset."""
    for a in range(0xC100, 0xC200):
        mem[a] = 0
    data = ROM[0x51BE + level * 33: 0x51BE + level * 33 + 33]
    de = 0xC110
    bitpos = 0
    for _ in range(8):
        mem[de] = 5                     # left border
        de += 1
        for _ in range(11):
            v = 0
            for _ in range(3):
                v = (v << 1) | ((data[bitpos >> 3] >> (7 - (bitpos & 7))) & 1)
                bitpos += 1
            if v == 7:
                v = 0x10
            mem[de] = v
            de += 1
        mem[de] = 5                     # right border
        de += 4
    for _ in range(0x20):
        mem[de] = 5
        de += 1
    d = 0xFF
    e = 0xFF
    for a in range(0xC100, 0xC1D0):
        if mem[a] == 0x10:
            if d == 0xFF:
                d = a & 0xFF
            else:
                e = a & 0xFF
    if e != 0xFF:
        d, e = e, d
    wb(0xFFD8, (d & 0x0F) << 4)
    wb(0xFFD7, d & 0xF0)
    wb(0xDA5B, 0xFF)
    wb(0xDA5C, 0xFF)
    wb(0xDA5F, d & 0xF0)
    wb(0xDA60, (d & 0x0F) << 4)
    wb(0xDA5D, 0)
    return d


# ===========================================================================
# gravity ($2C06)
# ===========================================================================
def gravity():
    """$2C06: scan $C17F upward; the first falling cell falls (early ret)."""
    b = 0x80
    hl = 0xC17F
    while b:
        v = mem[hl]
        if v == 2 or v == 3:
            if mem[hl + 0x10] == 0:
                # $2C5F: entity (type 2, state $40, cell) + the block fields
                de = entity_write(2, 0x40, hl & 0xFF)
                mem[de] = 3
                mem[de + 1] = 2
                mem[de + 2] = 5
                mem[hl] = 0
                # clear the "row" cell (C100 + swap(h&0xF)|(h&0xF0)) &= 7
                e = (((hl >> 8) & 0x0F) << 4) | ((hl >> 8) & 0xF0)
                mem[0xC100 + e] &= 7
                mem[hl + 0x10] = 3               # the landing cell = ladder
                wb(0xFFA1, 1)
                return rb(0xFFA1)
        elif v == 0x10:
            row4 = hl & 0xF0
            col4 = (hl & 0x0F) << 4
            if not (rb(0xFFD7) == row4 and rb(0xFFD8) == col4):
                if mem[hl + 0x10] == 0:
                    mem[hl] = 0
                    wb(0xDA5D, (rb(0xDA5D) & 1) | 4)
                    wb(0xFFA1, 1)
                    entity_write(7, 0x40, hl & 0xFF)
                    return rb(0xFFA1)
        hl -= 1
        b -= 1
    return rb(0xFFA1)


# --- player state machine ($2965-$2C05) ------------------------------------
def rd_cell_below():
    """$2D88: the cell at the position + $10 (below)."""
    return rd_cell((cur_hl() + 0x1000) & 0xFFFF)


def rd_cell_above():
    """$2D81: the cell at the position + $F0 (above)."""
    return rd_cell((cur_hl() + 0xF000) & 0xFFFF)


def state_set_facing(b):
    """$2BFD: FFD5 = (FFD5 & 1) | b."""
    wb(0xFFD5, (rb(0xFFD5) & 1) | b)


def player_tick():
    """$2965: the dispatch. Returns an action generator or None."""
    mem[0xFFE3] = 0
    joy = rb(0xFF8A)
    if joy & 0x02:                        # B: jump left
        return jump_try(0xF0, 2)
    if joy & 0x01:                        # A: jump right
        return jump_try(0x10, 3)
    if joy & 0x40:                        # up: climb up
        climb_up_state()
        return None
    if joy & 0x80:                        # down: climb down
        climb_down_state()
        return None
    state_recalc(rb(0xFFD5))
    return None


def jump_try(off, c):
    """$298F: the cell in the jump direction decides the action."""
    hl = (cur_hl() + (off & 0xFF)) & 0xFFFF
    cell = rd_cell(hl)
    if cell == 0:
        jump_start(c, hl)
        return None
    if cell == 1:
        jump_bump(c)
        return None
    if cell == 2 or cell == 6:
        return push_block(c, hl)
    if cell == 3:
        return ladder_grab(c, hl)
    if cell == 4:
        return step_up(c)
    state_recalc(c)
    return None


def jump_start(c, hl=None):
    """$29B2: begin a jump. The cell ahead gets the 0x10 marker."""
    if state_cell() == 1:
        c = (c & 1) | 0x0E
    set_state(c)
    mem[0xC100 + cell_off(hl if hl is not None else cur_hl())] |= 0x10
    return c


def jump_bump(c):
    """$2B20: bump into a wall (state $12/$0A)."""
    b = 0x0A
    if state_cell() == 1:
        b = 0x12
    c = (c & 1) | b
    set_state(c)
    return c


def step_up(c):
    """$29C6: step up onto a platform (states $1A/$2A; generator)."""
    if state_cell() == 1:
        c = (c & 1) | 0x2A
    else:
        c = (c & 1) | 0x1A
    hl = cur_hl()
    set_state(c)
    mem[0xC100 + cur_off()] |= 0x10
    mem[0xFFE4] = hl & 0xFF
    mem[0xFFE5] = hl >> 8
    mem[0xFFE3] = (c & 1) | 0x80
    yield from wait_1frame(2)                # $2D98(2)
    wb(0xFFFD, 6)
    slot = find_slot()
    if slot is not None:
        mem[slot] = 4
        mem[slot + 1] = 0
        mem[slot + 2] = ((c & 1) ^ 1) | 0x0C
        mem[slot + 3] = hl & 0xFF
        mem[slot + 4] = hl >> 8
    yield from wait_1frame(10)               # $2D98(10)
    slot = find_slot()
    if slot is not None:
        mem[slot] = 4
        mem[slot + 1] = 0
        mem[slot + 2] = (c & 1) | 0x0C
        mem[slot + 3] = hl & 0xFF
        mem[slot + 4] = hl >> 8
    return c


def ladder_grab(c, hl=None):
    """$2A3D: grab/extend the ladder ahead (states $1C/$1E; generator)."""
    if state_cell() == 1:
        c = (c & 1) | 0x1E
    else:
        c = (c & 1) | 0x1C
    wb(0xFFD5, c)
    if hl is None:
        hl = cur_hl()
    ahead = 0xC100 + cell_off(hl)
    side = ahead + 1 if (c & 1) else ahead - 1
    if mem[side] != 0:                         # $2A5A: the side cell
        state_recalc(c)
        return None
    mem[ahead] = 0                             # $2A5F: clear the ahead cell
    mem[side] = 3                              # $2A61: the ladder extends
    slot = find_slot()                         # $2C99
    if slot is not None:
        mem[slot] = (rb(0xFFD5) & 1) | 2
        mem[slot + 1] = 0
        mem[slot + 2] = 0
        mem[slot + 3] = side & 0xFF
        mem[slot + 4] = side >> 8
        mem[slot + 0x16] = 0x0B
    entity_write(0x13, rb(0xFFD5) & 1, side & 0xFF)   # $2DBE
    while True:                                # $2A76: wait while FFA1
        yield from wait_1frame(1)
        if rb(0xFFA1) == 0:
            break
    while True:                                # $2A80: wait + gravity
        yield from wait_1frame(1)
        gravity()
        if rb(0xFFA1) == 0:
            break
    if (rb(0xFFD5) & 0xFE) == 0x1E:            # $2A8D
        wb(0xFFD5, (rb(0xFFD5) & 1) | 0x10)
    else:
        wb(0xFFD5, rb(0xFFD5) & 1)
    return None


def push_block(c, hl=None):
    """$2AA1: push a block (states $20/$28; generator). hl = the block cell."""
    if hl is None:
        hl = cur_hl()
    cell = rd_cell(hl)
    mem[0xFF9D] = cell | 0x20
    wr_cell(hl, 0)
    if state_cell() == 1:
        c = (c & 1) | 0x28
    c |= 0x20
    set_state(c)
    mem[0xC100 + cell_off(hl)] |= 0x10
    # wait for the push animation (FFE1): $2AC0 loop
    while True:
        obj_dac()
        yield
        if rb(0xFFDB) == 4:
            wb(0xFFFD, 2)
        if rb(0xFFE1) != 0:
            break
    wb(0xFFD8, hl & 0xFF)                  # $2AD6: the col = the block's col
    state_set_facing(0x00)                 # $2BFB: D5 = D5 & 1
    slot = find_slot()
    if slot is not None:
        mem[slot] = mem[0xFF9D] & 0x0F
        mem[slot + 1] = 0
        mem[slot + 2] = (rb(0xFFD5) & 1) | 0x04
        mem[slot + 3] = hl & 0xFF
        mem[slot + 4] = hl >> 8
        mem[slot + 0x18] = 0
        mem[slot + 0x19] = hl & 0xFF
        mem[slot + 0x1A] = 0
    entity_spawn(7, (rb(0xFFD5) & 1) | 0x0E)
    return c


def state_recalc(c):
    """$2B82: idle state selection from the current/above cells."""
    st = state_cell()
    if st == 1:
        c = (c & 1) | 0x10
    else:
        above = rd_cell_above() & 7
        if above == 3:
            c = (c & 1) | 0x20
        else:
            c = c & 1
    mem[0xFFD5] = c
    return c


def climb_down_state():
    """$2B32: climb down (states $06/$16)."""
    if rb(0xFFD7) == 0x10:
        return state_recalc(rb(0xFFD5))
    above = rd_cell_above()
    if above >= 2:
        return state_recalc(rb(0xFFD5))
    b = 0x06
    if above != 1:
        b = 0x16
    if state_cell() != 1:
        return state_recalc(rb(0xFFD5))
    return climb_apply(b)


def climb_up_state():
    """$2B4D: climb up (states $08/$18)."""
    if state_cell() == 1:
        b = 0x08
        if rd_cell_below() >= 2:
            return state_recalc(rb(0xFFD5))
    else:
        b = 0x18
        if rd_cell_below() != 1:
            return state_recalc(rb(0xFFD5))
    return climb_apply(b)


def climb_apply(b):
    """$2B66: the state set + the cell move for a climb."""
    c = rb(0xFFD5)
    wb(0xFFD5, (c & 1) | b)
    entity_spawn(7, (c & 1) | b)
    a = mem[0xC100 + cur_off()]
    mem[0xC100 + cur_off()] = a & 7
    above_off = cell_off((cur_hl() + (0xF000 if b in (0x08, 0x18) else 0x1000)) & 0xFFFF)
    mem[0xC100 + above_off] |= 0x10
    return (c & 1) | b


# --- walk-down ($2948/$2BA8) ------------------------------------------------
def walk_down_2948():
    """$2948: start a descent when the cell below is empty and we stand free."""
    if rd_cell_below() != 0:
        return False
    if state_cell() != 0:
        return False
    mem[0xC100 + cur_off()] = 0
    state_set_facing(4)                        # $2BFD(4)
    yield from descend_2BA8()
    mem[0xC100 + cur_off()] |= 0x10            # $29C2
    return True


def descend_2BA8():
    """$2BA8: the descent (pos += $0200/frame until grounded, then E1-wait)."""
    entity_write(7, (rb(0xFFD5) & 1) | 4, cur_off() & 0xFF)
    while True:
        obj_dac()                              # $2DAC
        joy = rb(0xFF8A)
        if joy & 0x20:                         # left: face left
            wb(0xFFD5, rb(0xFFD5) & 0xFE)
        elif joy & 0x10:                       # right: face right
            wb(0xFFD5, rb(0xFFD5) | 1)
        add_pos(0x0200)
        if rb(0xFFD7) & 0x0F != 0:
            yield from wait_1frame(1)
            yield
            continue
        if rd_cell_below() == 0:
            yield from wait_1frame(1)
            yield
            continue
        break
    wb(0xFFFD, 1)                              # SFX
    state_set_facing(0x14)
    while True:
        yield from wait_1frame(1)
        if rb(0xFFE1) != 0:
            break
    state_set_facing(0x00)


# --- TaskGame main loop ($28D8) --------------------------------------------
def da5d_maintain():
    """$376F: the DA5D cell maintenance."""
    a = rb(0xDA5D)
    if a & 0x1E != 0:
        return
    hl = (((rb(0xDA5E) - 0x10) & 0xFF) << 8) | rb(0xDA5F)
    cell = rd_cell(hl)
    b = 0x20 if cell == 3 else 0
    wb(0xDA5D, (rb(0xDA5D) & 1) | b)


def task_game_loop():
    """$28D8: the TaskGame main loop (generator: one frame per yield)."""
    # the one-time init ($28D8-$28E7)
    yield                                  # rst $30
    yield from walk_down_2948()            # call $2948
    gravity()                              # call $2C06
    yield                                  # rst $30
    yield from wait_293A()                 # call $293A
    wb(0xFFB7, 0)
    wb(0xFFB8, 0)
    mem[0xC7F7] = 0
    # the main loop ($28EA)
    while True:
        # the movement/E1-wait ($28EA)
        while True:
            yield from wait_293A()
            st = rb(0xFFD5) & 0x0E
            if st == 0:
                break
            if rb(0xFFE1) != 0:
                break
        if st != 0:
            c = rb(0xFFD5)
            if st == 6:
                de = 0xF000
            elif st == 8:
                de = 0x1000
            elif c & 1:
                de = 0x10
            else:
                de = 0xFFF0
            add_pos(de)                        # call $2E1B
            state_recalc(c)                    # call $2B82
            yield from walk_down_2948()        # call $2948
            gravity()                          # call $2C06
        if rb(0xFFA1) != 0:
            yield from wait_293A()             # call nz $293A
        act = player_tick()                    # call $2965
        while act is not None:                 # the long action (push/step-up)
            try:
                next(act)
            except StopIteration:
                break
            yield
        da5d_maintain()                        # call $376F


# ===========================================================================
# game loop ($062C) + win check ($0B5E)
# ===========================================================================
def win_check():
    """$0B5E: any block(2) or special(6) left -> not cleared."""
    if rb(0xFFBB) != 0:
        return rb(0xFFA4)
    if rb(0xFFA2) != 0 or rb(0xFFA1) != 0:
        return rb(0xFFA4)
    for a in range(0xC110, 0xC1A0):
        v = mem[a]
        if v == 2 or v == 6:
            return rb(0xFFA4)
    wb(0xFFA4, 1)
    return 1


def validate_password():
    """$0F05: the password validation. Returns True (OK) or False (MISS).

    The LIFO unfold of the DA1A input into the DA5A, the FF9C-mode (the
    generator: sum the D9DB chars), the 10-bit level + 5-bit checksum
    ((2*level - b) >> 1) & 0x3F, the bounds, the D4F7 cleared-bitmap, and
    the continue setup (FFA3 = the first uncleared).
    """
    # $0F05-$0F20: the LIFO unfold (63 entries)
    c = 0
    hl = 0xDA1A
    de = 0xDA5A
    for _ in range(0x3F):
        a = mem[hl]; hl += 1
        if a & 0x80:
            mem[de] = a
            de -= 1
        else:
            a ^= mem[hl]
            mem[de] = a
            de -= 1
            c = (c + a) & 0xFF
    mem[de] = mem[hl]
    if rb(0xFF9C) != 0:
        # $0FD2: the generator mode: sum the D9DB chars, stop at a bit-7 char
        c2 = 0
        for i in range(8):
            a = mem[0xD9DB + i]
            if a & 0x80:
                break
            c2 = (c2 + a) & 0xFF
        return False
    # $0F2A: the level + the checksum (the exact carry-chained rotations)
    b = mem[0xDA1B]
    c = mem[0xDA1C]
    carry = 0
    a = c
    for _ in range(4):
        carry, a = (a >> 7) & 1, ((a << 1) | carry) & 0xFF
    for _ in range(2):
        carry, b = (b >> 7) & 1, ((b << 1) | carry) & 0xFF
        carry, a = (a >> 7) & 1, ((a << 1) | carry) & 0xFF
    d = mem[0xDA1E]
    a = d
    for _ in range(4):
        carry, a = (a >> 7) & 1, ((a << 1) | carry) & 0xFF
    for _ in range(4):
        carry, c = (c >> 7) & 1, ((c << 1) | carry) & 0xFF
        carry, a = (a >> 7) & 1, ((a << 1) | carry) & 0xFF
    c &= 0x7F
    # $0F4F: d = (rra x2 of d) & 0x20 | [DA1F]
    d = ((d >> 2) & 0x20) | mem[0xDA1F]
    if ((c * 2 - b) >> 1) & 0x3F != d:
        return False                        # $0FD0: the MISS
    if c < b or c >= 0x64:
        return False
    # $0F6A: the D4F7 cleared-bitmap: [i] = 1 for i < b
    for i in range(b):
        mem[0xD4F7 + i] = 1
    # $0F78-$0F97: the c-b bits from the DA1F 5-bit chars
    n = c - b
    if n:
        de = 0xDA1F
        bit = 0
        v = 0
        for i in range(n):
            if bit == 0:
                v = mem[de]; de += 1
                bit = 5
            mem[0xD4F7 + b + i] = 1 if (v & 0x10) else 0
            v = (v << 1) & 0xFF
            bit -= 1
    # $0F98: zero the rest of the D4F7
    for i in range(c, 0x64):
        mem[0xD4F7 + i] = 0
    # $0FA3: the continue setup (the $06AD count + the D559 scan -> FFA3)
    wb(0xD55A, 0)
    cnt = 0
    for i in range(0x63):
        if mem[0xD4F7 + i]:
            cnt += 1
    wb(0xD55B, cnt)
    b2 = 0x64
    a2 = 0
    hl2 = 0xD559
    while True:
        b2 -= 1
        if b2 == 0:
            break
        a2 |= mem[hl2]
        hl2 -= 1
        if a2 == 0:
            continue
        break
    if b2 == 0x63 and rb(0xD55B) < 0x63:
        b2 -= 1
    wb(0xFFA3, b2)
    return True


class Game:
    """The playable game: the tasks as coroutines driven by the frame loop."""

    def __init__(self, level=0):
        load()
        self.reset(level)

    def enemy_prefill(self):
        """$208D: the enemy spawn: the first two 0x10 cells become DA9B/DABB."""
        wb(0xDA9B, 0xFF)
        wb(0xDABB, 0xFF)
        wb(0xDA9C, 0xFF)
        wb(0xDABC, 0xFF)
        wb(0xDA9D, 0)
        wb(0xDABD, 0)
        wb(0xDAAA, 0)
        wb(0xDACA, 0)
        for a in range(0xC1C0, 0xC100, -1):       # the scan downward
            if mem[a] == 0x10:
                if rb(0xDA9B) == 0xFF:
                    wb(0xDA9B, 0)
                    wb(0xDA9C, 0xFF)
                    wb(0xDA9D, 0)
                    wb(0xDA9E, a & 0xF0)
                    wb(0xDA9F, ((a & 0x0F) << 4) & 0xF0)
                elif rb(0xDABB) == 0xFF:
                    wb(0xDABB, 1)
                    wb(0xDABC, 0xFF)
                    wb(0xDABD, 0)
                    wb(0xDABE, a & 0xF0)
                    wb(0xDABF, ((a & 0x0F) << 4) & 0xF0)
                else:
                    mem[a] = 0

    def reset(self, level):
        global mem
        mem = bytearray(0x10000)
        level_decode(level)
        self.level = level
        self.ff96 = 0x5A
        wb(0xFFA4, 0)
        wb(0xFFBB, 0)
        wb(0xFFBC, 0)
        wb(0xFFA1, 0)
        wb(0xFFA2, 0)
        self.tasks = {}
        self.tasks[1] = task_game_loop()
        self.task_input = None
        self.pending_action = False
        self.mode = 'play'
        self.paused = False
        self.ffa0 = 0; self.ffa1 = 0; self.ffa2 = 0; self.ffa3 = 0

    def joy(self, buttons, dpad):
        old = rb(0xFF8A)
        oldb = rb(0xFF8B)
        lastc = rb(0xFF8C)
        dbc = rb(0xFF8D)
        new, edge, lastc, dbc = joypad_read(buttons, dpad, old, oldb, lastc, dbc)
        wb(0xFF8A, new)
        wb(0xFF8B, edge)
        wb(0xFF8C, lastc)
        wb(0xFF8D, dbc)
        return new, edge

    def step(self, buttons, dpad):
        """One frame. Returns (FFA4, FFD7, FFD8, FFD5)."""
        new, edge = self.joy(buttons, dpad)
        if edge & 0x08 and self.mode == 'play':    # Start: pause ($06EA)
            self.paused = True
            wb(0xDDA1, 0)
        # advance the task generators one step
        g = self.tasks.get(1)
        if g is not None:
            try:
                next(g)
            except StopIteration:
                del self.tasks[1]
        if self.task_input is not None:
            try:
                r = next(self.task_input)
                if r == 'dead':
                    self.task_input = None
                    self.enter_continue()
            except StopIteration as si:
                self.task_input = None
                if si.value == 'dead':
                    self.enter_continue()
        # the A action registers TaskInput (game loop $094C)
        if edge & 0x01 and self.task_input is None and rb(0xFFBB) == 0 \
                and rb(0xFFA2) == 0 and rb(0xFFA1) == 0 and (rb(0xFFD5) & 0xFE) != 0x0C:
            wb(0xFFBB, 1)
            self.task_input = task_input()
        if edge & 0x02 and self.task_input is None and rb(0xFFBB) == 0 \
                and rb(0xFFA2) == 0 and rb(0xFFA1) == 0 and (rb(0xFFD5) & 0xFE) != 0x0C:
            wb(0xFFBB, 2)
            self.task_input = task_input()
        # the HUD timer ($08D5: the 1/60s, s, min, 10-min counters)
        if self.mode == 'play':
            if self.ffa0 < 0x3C:
                self.ffa0 += 1
            else:
                self.ffa0 = 0
                if self.ffa1 < 0x3C:
                    self.ffa1 += 1
                else:
                    self.ffa1 = 0
                    if self.ffa2 < 0x3C:
                        self.ffa2 += 1
                    else:
                        self.ffa2 = 0
                        if self.ffa3 < 0x0A:
                            self.ffa3 += 1
                        else:
                            self.ffa0 = 0; self.ffa1 = 0x3B; self.ffa2 = 0x3B; self.ffa3 = 9
        win_check()
        # the game loop's win check ($065D): A4 latched -> FF96 countdown
        if rb(0xFFA4) != 0 and self.mode == 'play':
            self.ff96 = (self.ff96 - 1) & 0xFF
            if self.ff96 == 0:
                self.clear_flow()
        # TaskHud frame ($2F9C): clears the busy flags every frame
        wb(0xFFA2, 0)
        wb(0xFFA1, 0)
        if self.paused:
            self.pause_step(new, edge)
        elif self.mode == 'select':
            self.select_step(buttons, dpad)
        elif self.mode == 'password':
            self.password_step(new, edge)
        elif self.mode == 'menu':
            self.menu_step(new, edge)
        elif self.mode == 'continue':
            self.continue_step(new, edge)
        return rb(0xFFA4), rb(0xFFD7), rb(0xFFD8), rb(0xFFD5)

    def pause_step(self, new, edge):
        """$0760: the pause loop (the cursor + the confirm)."""
        if edge & 0x0A:                      # B/Select: exit the pause
            self.paused = False
            return
        if edge & 0x80:                      # down: the cursor++
            c = (rb(0xDDA1) + 1) & 0xFF
            if c > 2:
                c = 0
            wb(0xDDA1, c)
        elif edge & 0x40:                    # up: the cursor--
            c = (rb(0xDDA1) - 1) & 0xFF
            if c > 2:
                c = 2
            wb(0xDDA1, c)
        elif edge & 0x01:                    # A: the confirm ($07CC)
            c = rb(0xDDA1)
            self.paused = False
            if c <= 1:                       # SCROLL/RESTART: restart the level
                self.restart_level()
            # c == 2: EXIT the pause -> resume

    def restart_level(self):
        """$07F0: redraw the level and restart."""
        lvl = rb(0xFFA3)
        level_decode(lvl)
        self.enemy_prefill()
        wb(0xFFA4, 0)
        self.ff96 = 0x5A
        self.tasks = {}
        self.tasks[1] = task_game_loop()
        self.task_input = None

    def continue_game(self):
        """$0F9F: the continue: FFA3 = the first uncleared level."""
        wb(0xD55A, 0)
        c = 0
        for i in range(0x63):
            if mem[0xD4F7 + i]:
                c += 1
        wb(0xD55B, c)
        for i in range(0x65):
            wb(0xD976 + i, mem[0xD4F7 + i])
        b = 0x64
        hl = 0xD559
        a = 0
        while True:
            b -= 1
            if b == 0:
                break
            a |= mem[hl]
            hl -= 1
            if a == 0:
                continue
            break
        if b == 0x63:
            if rb(0xD55B) < 0x63:
                b -= 1
        wb(0xFFA3, b)

    def clear_flow(self):
        """$0668: the level-clear: mark, level++, count, round-select."""
        self.tasks = {}
        self.task_input = None
        if rb(0xFF9E) != 0:
            return                      # the password flow (not ported)
        # $068D: mark the clear, $0698: level++
        lvl = rb(0xFFA3)
        if lvl != 0x63:
            mem[0xD4F7 + lvl] = 1
            if lvl != 0x62:
                wb(0xFFA3, (lvl + 1) & 0xFF)
        # $06AD: the cleared count -> D55B
        c = 0
        for i in range(0x63):
            if mem[0xD4F7 + i]:
                c += 1
        wb(0xD55B, c)
        # the round-select ($0510)
        self.mode = 'select'
        wb(0xDDA1, 0)
        wb(0xDDA2, 0)
        wb(0xDA80, 0)
        for i in range(0x40):
            wb(0xD9DB + i, 0x80)
        wb(0xFFB0, 0)

    def enter_continue(self):
        """$1F02: the continue screen (the level-grid cursor, A = the cell edit)."""
        self.mode = 'continue'
        wb(0xDDA1, 0)
        wb(0xDDA2, 0)
        self.pending_action = False

    def continue_step(self, new, edge):
        """$1F13: the continue input."""
        if edge & 0x10:                      # right: the col++
            wb(0xDDA2, (rb(0xDDA2) + 1) & 0x0F)
        elif edge & 0x20:                    # left: the col--
            wb(0xDDA2, (rb(0xDDA2) - 1) & 0x0F)
        elif edge & 0x40:                    # up: the row--
            wb(0xDDA1, (rb(0xDDA1) - 1) & 0x0F)
        elif edge & 0x80:                    # down: the row++
            wb(0xDDA1, (rb(0xDDA1) + 1) & 0x0F)
        elif edge & 0x01:                    # A: place the player ($1F5D)
            self.mode = 'play'
            self.ff96 = 0x5A
            wb(0xFFA4, 0)
            wb(0xFFD7, (rb(0xDDA1) << 4) & 0xF0)
            wb(0xFFD8, (rb(0xDDA2) << 4) & 0xF0)
            self.tasks = {}
            self.tasks[1] = task_game_loop()
            self.task_input = None
        elif edge & 0x02:                    # B: exit to the menu
            self.mode = 'select'
            self.enter_menu()

    def enter_password(self):
        """$124E: the password screen (the cursor = level/5, level%5)."""
        self.mode = 'password'
        lvl = rb(0xFFA3)
        wb(0xDDA1, lvl // 5)
        wb(0xDDA2, lvl % 5)
        wb(0xFFB0, 0)

    def password_step(self, new, edge):
        """$12B0: the password loop."""
        if edge & 0x80:                      # down: the row++
            v = (rb(0xDDA1) + 1) & 0xFF
            if v > 0x13:
                v = 0x13
            wb(0xDDA1, v)
        elif edge & 0x40:                    # up: the row--
            v = (rb(0xDDA1) - 1) & 0xFF
            if v > 0x13:
                v = 0
            wb(0xDDA1, v)
        elif edge & 0x01:                    # A: the confirm ($1318)
            lvl = rb(0xDDA1) * 5 + rb(0xDDA2)
            if lvl < 0x63:
                wb(0xFFA3, lvl)
            self.mode = 'select'
            self.enter_game_from_select()
        elif edge & 0x02:                    # B: back to the menu
            self.mode = 'select'

    def enter_menu(self):
        """$14F2: the main menu (the 5 preview items, the cursor)."""
        self.mode = 'menu'
        wb(0xFFFB, 7)
        wb(0xDDA1, 0)
        wb(0xDD9F, 0)

    def menu_step(self, new, edge):
        """$1536: the menu input."""
        if edge & 0x80:                      # down: the cursor--
            c = (rb(0xDDA1) - 1) & 0xFF
            if c == 0xFF:
                c = 4
            wb(0xDDA1, c)
        elif edge & 0x40:                    # up: the cursor++
            c = (rb(0xDDA1) + 1) & 0xFF
            if c > 4:
                c = 0
            wb(0xDDA1, c)
        elif edge & 0x20:                    # left: the FFCC flip
            wb(0xFFCC, rb(0xFFCC) ^ 1)
        elif edge & 0x01:                    # A: the confirm ($158F)
            c = rb(0xDDA1)
            if c == 1:                       # the password entry
                self.enter_password()
            elif c == 2:                     # the round-select
                self.mode = 'select'
            elif c == 3:                     # the password generator ($1142)
                self.generate_password()
            elif c == 4:                     # the game ($1D72)
                self.mode = 'select'
                self.enter_game_from_select()

    def generate_password(self):
        """$1142: write the 8-char password for the cleared levels into D9DB."""
        b = 0xFF
        for i in range(0x64):
            b += 1
            if mem[0xD4F7 + i]:
                break
        c = 0
        for i in range(0x65):
            if mem[0xD55A + i]:
                c += 1
        # the 8 chars: (2*level - b) & 0x3F in 5-bit chars
        lvl = b & 0xFF
        for i in range(8):
            v = (lvl * 2 - b) & 0x3F
            wb(0xD9DB + i, v)
            lvl = (lvl >> 5) | ((b & 0x1F) << 3) & 0xFF
            b = (b >> 5) | 0

    def select_step(self, buttons, dpad):
        """$0C5C: the round-select loop (the cursor + the confirm)."""
        new, edge = self.joy(buttons, dpad)
        # $0CDF dispatch: bit0 = A (confirm), bit1 = B (back), 2/3 = exit
        if edge & 0x01:                    # A: confirm ($0D9E)
            row = rb(0xDDA1)
            col = rb(0xDDA2)
            if row == 2:
                # the password row: only the col 7 (the OK) validates
                if col >= 7:
                    if validate_password():
                        # $0DF9: "OK  " -> the game entry with FFA3
                        self.enter_game_from_select()
                    else:
                        # $0DEF: "MISS" -> stay
                        pass
            else:
                idx = ((row & 0x0F) << 4) | col
                a80 = rb(0xDA80)
                wb(0xD9DB + a80, idx)
                if a80 < 0x3B:
                    wb(0xDA80, a80 + 1)
        elif edge & 0x02:                  # B: back ($0E40)
            a80 = rb(0xDA80)
            if a80 > 0:
                a80 -= 1
                wb(0xDA80, a80)
                wb(0xD9DB + a80, 0x80)
        elif edge & (0x20 | 0x40):         # up/down: exit ($0E6F)
            pass
        # cursor movement from the dpad (the round-select moves via A/B only)
        # the 8-character password complete -> the game entry
        if rb(0xDA80) >= 8:
            self.enter_game_from_select()

    def enter_game_from_select(self):
        """$1D72: decode the selected level and start."""
        lvl = rb(0xFFA3)
        self.mode = 'play'
        self.ff96 = 0x5A
        wb(0xFFA4, 0)
        wb(0xFFA3, lvl)
        level_decode(lvl)
        self.enemy_prefill()            # $208D
        self.tasks = {}
        self.tasks[1] = task_game_loop()
        self.task_input = None

    def play(self, inputs, frames):
        log = []
        for f in range(frames):
            buttons, dpad = inputs(f)
            self.step(buttons, dpad)
            log.append((rb(0xFFD7), rb(0xFFD8), rb(0xFFD5), rb(0xFFA4),
                        bytes(mem[0xC110:0xC1A0])))
        return log


def play_level(level, inputs, frames):
    """Convenience: run a level with a scripted input."""
    g = Game(level)
    return g.play(inputs, frames)

# --- TaskInput ($325B-$34C1): the entity/enemy AI --------------------------
def set_bc_flag():
    wb(0xFFBC, 1)


def wait_idle():
    """$36DC: wait while FFA1 (the frame-wait with the object update)."""
    while rb(0xFFA1) != 0:
        yield from frame_wait_anim()


def frame_wait_anim():
    """$36FF: one frame of the anim wait (the object update + yield)."""
    wb(0xFFBC, 1)                              # call $36D2
    if rb(0xFFBB) == 1:
        object_update_simple(0xFFD3, 0)
    elif rb(0xFFBB) == 2:
        object_update(0xFFD3, 0)
    if rb(0xDA5B) != 0xFF:
        if rb(0xFFBB) == 1:
            object_update_simple(0xDA5B, 0x10)
        elif rb(0xFFBB) == 2:
            object_update(0xDA5B, 0x10)
    yield


def wait_frames_b(b):
    """$36E8: b x (the object update) - a spin, no yield."""
    for _ in range(b):
        obj_dac()


def task_input():
    """$325B: the entity task (generator; the FFBB=1 action phase, FFBB=2 scan)."""
    set_bc_flag()
    obj_dac()                            # call $34BE (the $2DAC)
    yield
    while True:
        yield
        if rb(0xFFBB) == 1:
            # $3272: the backward entity scan ($2DDF steps the index)
            cont = False
            while True:
                if ((rb(0xFFB8) & 3) << 8 | rb(0xFFB7)) == 0:
                    break                    # jr z $32A0
                v = (rb(0xFFB7) - 1) & 0xFF
                wb(0xFFB7, v)
                if v == 0xFF:
                    wb(0xFFB8, (rb(0xFFB8) - 1) & 0xFF)
                e = entity_de()
                t = mem[e]
                if t == 0:
                    break                    # jr z $32A0
                if t == 7 or t == 0x13:
                    r = None
                    if t == 7 and mem[e + 1] == 3:
                        # the player's own jump entity is (7, 3): skip it
                        pass
                    elif t == 7:
                        r = (yield from enemy_tick())
                    else:
                        yield from enemy_tick()
                    if r == 'dead':
                        return 'dead'
                    if rb(0xFF8A) & 0x01:
                        cont = True          # jr nz $3261 (A held)
                        break
                    if t == 7 and mem[e + 1] != 3:
                        break
            if cont:
                continue
        else:
            entity_dispatch_scan()
            if rb(0xFF8A) & 0x02:
                continue                     # B held -> the loop
        # $32A0: the end (the FFBC gate)
        if rb(0xFFBC) != 0:
            continue
        wb(0xFFBB, 0)
        return


def entity_dispatch_scan():
    """$32B2: scan the entity table; process enemies (7) and blocks (2/3/6)."""
    wb(0xFFBC, 0)
    e = entity_de()
    t = mem[e]
    if t == 0:
        return
    entity_next()
    wb(0xFFB4, t)
    if (t & 0x0F) == 7:
        enemy_tick()
    elif (t & 0x0F) in (2, 3, 6):
        block_tick()
    return


def enemy_tick():
    """$32DE/$34E6: the enemy state dispatch (generator)."""
    yield from wait_idle()
    st = mem[entity_de() + 1]
    if st == 0xFF:
        enemy_respawn()
        return None
    if st == 0x40:
        return (yield from enemy_kill())
    c = st
    if (c & 0xFE) == 0x1A or (c & 0xFE) == 0x2A or c == 0x28:
        enemy_walk(c)
        return None
    if (c & 0x0E) == 0x02 or (c & 0x0E) == 0x0A or (c & 0x0E) == 0x0E:
        enemy_move_h(c)
        return None
    if (c & 0x0E) == 0x04:
        enemy_climb(c)
        return None
    if (c & 0x0E) == 0x06:
        enemy_move_d(c)
        return None
    if (c & 0x0E) == 0x08:
        enemy_move_u(c)
        return None
    return None


def enemy_respawn():
    """$3652: the enemy died -> the player respawn helper."""
    set_bc_flag()
    # player respawn at the spawn point ($099C)
    wb(0xFFD7, rb(0xFFC2))
    wb(0xFFD8, rb(0xFFC1))
    wb(0xFFBD, 0)
    wb(0xFFBE, 0)
    wb(0xFFBC, 0)
    return


def enemy_kill():
    """$365A: the enemy killed the player -> the death (DA79 fall).

    $3455: [yield; while A1: obj_dac + yield; obj_dac; yield] then $349E.
    """
    a = mem[entity_de() + 2] & 0xF0
    wb(0xDA79, a)
    wb(0xDA5D, (rb(0xDA5D) & 1) | 4)
    while True:
        yield
        if rb(0xFFA1) == 0:
            break
        obj_dac()
    obj_dac()
    yield
    wb(0xFFBC, 0)
    return 'dead'


def enemy_move_h(c):
    """$354F: the horizontal move (de = $FFF0/$10 by bit 0)."""
    de = 0xFFF0
    if not (c & 1):
        de = 0x10
    return enemy_apply_move(c, de)


def enemy_move_u(c):
    """$3560: the up move (de = $F000)."""
    return enemy_apply_move(c, 0xF000)


def enemy_move_d(c):
    """$355B: the down move (de = $1000)."""
    return enemy_apply_move(c, 0x1000)


def enemy_apply_move(c, de):
    """$3565: clear the cell, set the target + state, wait E1.

    The ROM writes the target straight into the D7/D8 (the shared
    current-entity pos) BEFORE the move_done spin.
    """
    e = cur_off()
    mem[0xC100 + e] &= 7                     # the cell-clear
    hl = (cur_hl() + de) & 0xFFFF
    wr_cell(hl, rd_cell(hl) | 0x10)          # the target cell marker
    wb(0xFFD7, hl >> 8)                      # the target pos
    wb(0xFFD8, hl & 0xFF)
    wb(0xFFD5, c)
    return move_done()


def enemy_walk(c):
    """$3528: the enemy hops toward the player."""
    wb(0xFFBC, 1)
    wb(0xFFD5, c & 1)
    jump_cloud()
    wait_frames_b(10)
    c ^= 1
    jump_cloud()
    wait_frames_b(12)
    e = cur_off()
    mem[0xC100 + e] = 4
    enemy_move_h(c)
    return


def jump_cloud():
    """$3732: spawn the hop dust object."""
    slot = find_slot()
    if slot is not None:
        mem[slot] = 4
        mem[slot + 1] = 0
        mem[slot + 2] = (rb(0xFFD5) & 1) | 0x0E
        mem[slot + 3] = rb(0xFFD7)
        mem[slot + 4] = rb(0xFFD8)
    return


def enemy_climb(c):
    """$3582: the enemy climbs (generator: one frame per yield)."""
    set_bc_flag()
    e = cur_off()
    mem[0xC100 + e] &= 7
    wb(0xFFD5, c)
    row = mem[entity_de() + 2] & 0xF0
    while rb(0xFFD7) != row:
        yield
        frame_wait_anim()
        add_pos(0xFF00)
    e = cur_off()
    mem[0xC100 + e] |= 0x10
    wb(0xFFBC, 0)
    return


def move_done():
    """$3673: the E1 wait + the pos update + the state settle (generator).

    The ROM's $3673 loops [call $36D7 (FFBC=1); call $3751 (the object
    update); the step-up checks; the E1 check] with NO yield between the
    update and the check - the E1=$80 set by the update's own tick is seen
    by the check in the same pass (a spin within one task slice).
    """
    while True:
        wb(0xFFBC, 1)
        obj_dac()                            # call $3751
        # $369E: the E1 wait (the step-up completion at FFDB==2/FFDC==1)
        a = rb(0xFFD5) & 0xFE
        if a == 0x2A or a == 0x1A:
            if rb(0xFFDB) == 2 and rb(0xFFDC) == 1:
                c = rb(0xFFD5) & 1
                hl = (rb(0xFFB5) << 8) | rb(0xFFB6)
                row_write_2cf5(hl, c)
        if rb(0xFFE1) != 0:
            break
    if rb(0xFFD5) & 0xFE in (0x2A, 0x1A):    # the step-up settle
        c = (rb(0xFFD5) & 1) ^ 1
        hl = (rb(0xFFB5) << 8) | rb(0xFFB6)
        row_write_2cf5(hl, c)
        state_recalc(rb(0xFFD5))
        if state_cell() == 1:
            mem[0xC100 + cur_off()] |= 0x10
    else:
        # $36BF: state_recalc + the cell marker (the pos is already the target)
        state_recalc(rb(0xFFD5))
        if state_cell() == 1:
            mem[0xC100 + cur_off()] |= 0x10
    wb(0xFFBC, 0)
    e = entity_de()                          # $34A1
    if mem[e] == 7 and mem[e + 1] in (0x40, 0x04):
        return 'rescan'
    return None


def row_write_2cf5(hl, facing):
    """$2CF5: the step-up row writes at the target (h,l)."""
    e = cell_off(hl)
    for i in range(2):
        a = 1 if facing else 0
        mem[0xC100 + e] = (mem[0xC100 + e] & 1) | (2 if facing else 0)
        e += 1
        facing ^= 1


def block_tick():
    """$339C: the block processing (exact; the $2CDD/$2D20 VRAM writes skipped).

    The cell index comes from the state (bit 4: pushed, shifted by the
    facing; bit 5: the state itself) or the type. The slot gets the
    type/$0A-or-cell fields, and the pushed path hands off to $347A.
    """
    e = entity_de()
    t = mem[e]                                  # the type
    a = mem[e + 1]                              # the state
    if a & 0x10:
        a = (a + 1) & 0xFF if not (t & 1) else (a - 1) & 0xFF
    elif not (a & 0x20):
        a = t
    cell = a
    mem[0xC100 + cell] &= 0x10                  # the player-bit clear
    row = 0xC100 + ((cell & 0xF0) | (((cell & 0x0F) << 4) & 0xF0))
    slot = find_slot()                          # $2CC8
    if slot is None:
        return None
    mem[slot] = rb(0xFFB4) & 0x0F               # [0] = the type
    mem[slot + 1] = 0                           # [1] = 0
    if t & 0x10:                                # the pushed block (the type bit 4)
        mem[slot + 2] = mem[row - 1] | 2        # [2] = the cell | 2
        mem[slot + 3] = t & 0xFF
        mem[slot + 4] = 0
        d5 = (mem[row - 1] & 1) | (0x1E if state_cell() == 1 else 0x1C)
        wb(0xFFD5, d5)
        wb(0xFFB5, rb(0xFFD7))
        wb(0xFFB6, rb(0xFFD8))
        return block_move_347a()                # $347A
    if t & 0x20:                                # the type bit 5
        mem[slot + 2] = mem[row - 1] | 4
        mem[slot + 3] = t & 0xFF
        mem[slot + 4] = 0
        mem[slot + 0x18] = 0
        mem[slot + 0x19] = t & 0xFF
        mem[slot + 0x1A] = 0
        wb(0xFFBC, 0)                           # $349E
        return None
    # the settling block ($342C)
    mem[slot + 2] = 0x0A
    mem[slot + 3] = t & 0xFF
    mem[slot + 4] = 0
    mem[slot + 0x1C] = mem[row - 1] & 0xF0
    obj_dac()                                   # $34BE
    wb(0xFFBC, 1)                               # $36D2
    # $3445: the entity-rescan check
    e2 = entity_de()
    a2 = mem[e2]
    if a2 != 0 and a2 != 7 and (a2 & 0xF0) == 0:
        entity_dispatch_scan()                  # $32B2
    while True:                                 # $3455
        yield
        if rb(0xFFA1) == 0:
            break
        obj_dac()
    obj_dac()
    yield
    wb(0xFFBC, 0)                               # $349E
    return None


def block_move_347a():
    """$347A: the ladder-block move: the E1 spin, the pos settle, the rescan."""
    while True:
        wb(0xFFBC, 1)
        obj_dac()
        if rb(0xFFE1) != 0:
            break
    wb(0xFFD7, rb(0xFFB5))                      # the target pos
    wb(0xFFD8, rb(0xFFB6))
    wb(0xFFD5, rb(0xFFD5) & 1)
    if state_cell() == 1:
        wb(0xFFD5, rb(0xFFD5) | 0x10)
    # $349E: FFBC = 0 + the entity rescan check
    wb(0xFFBC, 0)
    e = entity_de()
    if mem[e] == 7 and mem[e + 1] in (0x40, 0x04):
        return 'rescan'
    return None


# --- enemy/entity entry from the action phase ($34C1) ----------------------
def entity_player_tick():
    """$34C1: the action-phase processing (the player + the entities; generator)."""
    wb(0xFFBC, 0)
    e = entity_de()
    if mem[e] == 0:
        return None
    wb(0xFFB4, mem[e])
    if (mem[e] & 0x0F) == 7:
        return (yield from enemy_tick())
    elif (mem[e] & 0x0F) in (2, 3, 6):
        yield from block_tick()
    return None
