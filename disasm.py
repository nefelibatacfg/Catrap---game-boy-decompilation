#!/usr/bin/env python3
"""Full SM83 disassembler for Catrap (USA).gb -> RGBDS source tree.

Emits:
  main.asm             - section + includes
  hardware.inc         - GB hardware register equates
  src/ram.inc          - used RAM/HRAM equates
  src/vectors.asm      - RST + interrupt vectors ($0000-$00FF)
  src/header.asm       - cart header ($0100-$014F)
  src/code.asm         - code in address order, INCLUDEs data files inline
  src/data/data_XXXX.asm - data regions (tables / strings / raw bytes)

Byte-exactness is guaranteed by faithful emission: every region re-emits
exactly the bytes it consumed, verified by the build + full-file compare.
"""
import os, sys

ROM_PATH = "Catrap (USA).gb"
try:
    ROM = open(ROM_PATH, "rb").read()
except FileNotFoundError:
    raise SystemExit(
        f"missing '{ROM_PATH}' - place your own dump of the game next to "
        "this script (the disassembler and the emulator read it directly).")
assert len(ROM) == 0x8000, f"unexpected ROM size {len(ROM)}"

# ---------------------------------------------------------------- opcodes --
# (mnemonic, operand_kind); kinds: "" d8 d16 r8 a8 sp8 rst c
OPS = [
    ("nop",""), ("ld bc,d16","d16"), ("ld [bc],a",""), ("inc bc",""),
    ("inc b",""), ("dec b",""), ("ld b,d8","d8"), ("rlca",""),
    ("ld [d16],sp","d16"), ("add hl,bc",""), ("ld a,[bc]",""), ("dec bc",""),
    ("inc c",""), ("dec c",""), ("ld c,d8","d8"), ("rrca",""),
    ("stop",""), ("ld de,d16","d16"), ("ld [de],a",""), ("inc de",""),
    ("inc d",""), ("dec d",""), ("ld d,d8","d8"), ("rla",""),
    ("jr r8","r8"), ("add hl,de",""), ("ld a,[de]",""), ("dec de",""),
    ("inc e",""), ("dec e",""), ("ld e,d8","d8"), ("rra",""),
    ("jr nz,r8","r8"), ("ld hl,d16","d16"), ("ld [hli],a",""), ("inc hl",""),
    ("inc h",""), ("dec h",""), ("ld h,d8","d8"), ("daa",""),
    ("jr z,r8","r8"), ("add hl,hl",""), ("ld a,[hli]",""), ("dec hl",""),
    ("inc l",""), ("dec l",""), ("ld l,d8","d8"), ("cpl",""),
    ("jr nc,r8","r8"), ("ld sp,d16","d16"), ("ld [hld],a",""), ("inc sp",""),
    ("inc [hl]",""), ("dec [hl]",""), ("ld [hl],d8","d8"), ("scf",""),
    ("jr c,r8","r8"), ("add hl,sp",""), ("ld a,[hld]",""), ("dec sp",""),
    ("inc a",""), ("dec a",""), ("ld a,d8","d8"), ("ccf",""),
]
REG = ["b","c","d","e","h","l","[hl]","a"]
for r1 in range(8):
    for r2 in range(8):
        op = 0x40 + r1*8 + r2
        if op == 0x76:
            OPS.append(("halt",""))
        else:
            OPS.append((f"ld {REG[r1]},{REG[r2]}",""))
ALU = ["add a,","adc a,","sub ","sbc a,","and ","xor ","or ","cp "]
for r1 in range(8):
    for r2 in range(8):
        op = 0x80 + r1*8 + r2
        OPS.append((ALU[r1]+REG[r2],""))
OPS += [
    ("ret nz",""), ("pop bc",""), ("jp nz,d16","d16"), ("jp d16","d16"),
    ("call nz,d16","d16"), ("push bc",""), ("add a,d8","d8"), ("rst $00","rst"),
    ("ret z",""), ("ret",""), ("jp z,d16","d16"), ("PREFIX",""),
    ("call z,d16","d16"), ("call d16","d16"), ("adc a,d8","d8"), ("rst $08","rst"),
    ("ret nc",""), ("pop de",""), ("jp nc,d16","d16"), ("INVALID",""),
    ("call nc,d16","d16"), ("push de",""), ("sub d8","d8"), ("rst $10","rst"),
    ("ret c",""), ("reti",""), ("jp c,d16","d16"), ("INVALID",""),
    ("call c,d16","d16"), ("INVALID",""), ("sbc a,d8","d8"), ("rst $18","rst"),
    ("ldh [a8],a","a8"), ("pop hl",""), ("ld [$ff00+c],a","c"), ("INVALID",""),
    ("INVALID",""), ("push hl",""), ("and d8","d8"), ("rst $20","rst"),
    ("add sp,r8","sp8"), ("jp [hl]",""), ("ld [d16],a","d16"), ("INVALID",""),
    ("INVALID",""), ("INVALID",""), ("xor d8","d8"), ("rst $28","rst"),
    ("ldh a,[a8]","a8"), ("pop af",""), ("ld a,[$ff00+c]","c"), ("di",""),
    ("INVALID",""), ("push af",""), ("or d8","d8"), ("rst $30","rst"),
    ("ld hl,sp+r8","sp8"), ("ld sp,hl",""), ("ld a,[d16]","d16"), ("ei",""),
    ("INVALID",""), ("INVALID",""), ("cp d8","d8"), ("rst $38","rst"),
]
assert len(OPS) == 256, len(OPS)

CBROT = ["rlc ","rrc ","rl ","rr ","sla ","sra ","swap ","srl "]
CBOPS = []
for r1 in range(8):
    for r2 in range(8):
        CBOPS.append((CBROT[r1]+REG[r2],""))
for b in range(8):
    for r2 in range(8):
        CBOPS.append((f"bit {b},{REG[r2]}",""))
for b in range(8):
    for r2 in range(8):
        CBOPS.append((f"res {b},{REG[r2]}",""))
for b in range(8):
    for r2 in range(8):
        CBOPS.append((f"set {b},{REG[r2]}",""))
assert len(CBOPS) == 256, len(CBOPS)

LEN = {"":1,"d8":2,"d16":3,"r8":2,"a8":2,"sp8":2,"rst":1,"c":1}

def oplen(mnem, arg):
    if mnem == "stop":
        return 2   # 0x10 0x00
    return LEN[arg]

def s8(b):
    return b-256 if b >= 0x80 else b

# ---------------------------------------------------------------- traversal
code = {}          # addr -> (mnem, arg, operand)
cbcode = {}        # addr -> (mnem, arg, operand)
warn = []

def decode(a, cb=False):
    if cb:
        mnem, arg = CBOPS[ROM[a+1]]
        return mnem, arg, None
    mnem, arg = OPS[ROM[a]]
    if arg == "d16":
        return mnem, arg, ROM[a+1] | (ROM[a+2] << 8)
    if arg == "r8":
        return mnem, arg, a + 2 + s8(ROM[a+1])
    if arg == "d8" or arg == "a8" or arg == "sp8":
        return mnem, arg, ROM[a+1]
    if arg == "rst":
        return mnem, arg, ROM[a] & 0x38
    return mnem, arg, None

def is_valid_target(t):
    return 0 <= t < 0x8000 and not (0x100 <= t < 0x150)

todo = list(range(0, 0x40, 8))       # 8 RST vectors
todo += [0x40, 0x48, 0x50, 0x58, 0x60]  # VBlank/LCD/Timer/Serial/Joypad
todo += [ROM[0x102] | (ROM[0x103] << 8)]  # entry point (jp operand at $0102)

# Unreferenced helper routine (dead code or reached via data-driven dispatch)
todo.append(0x27EB)

# Dynamic trace: addresses actually executed by the emulator (emu.py).
# These catch indirect entries (task scheduler ret-dispatch, ROM-stack jumps).
if os.path.exists("trace.txt"):
    with open("trace.txt") as f:
        for line in f:
            line = line.strip()
            if line:
                todo.append(int(line, 16))

while todo:
    a = todo.pop()
    while 0 <= a < 0x8000:
        if a in code or a in cbcode:
            break
        mnem, arg, opv = decode(a)
        if mnem == "INVALID":
            pass
        code[a] = (mnem, arg, opv)
        if mnem == "PREFIX":
            m2, a2, o2 = decode(a, cb=True)
            cbcode[a] = (m2, a2, o2)
            ln = 2
        else:
            ln = oplen(mnem, arg)
        # follow control flow
        if mnem == "ret" or mnem == "reti":
            break
        if mnem == "jp [hl]":
            break
        if mnem == "stop":
            break
        if mnem == "jp d16":
            if is_valid_target(opv):
                todo.append(opv)
            break
        if mnem.startswith("jp "):
            if is_valid_target(opv):
                todo.append(opv)
        if mnem.startswith("call"):
            if is_valid_target(opv):
                todo.append(opv)
        if mnem.startswith("jr"):
            if is_valid_target(opv):
                todo.append(opv)
        if mnem.startswith("rst"):
            todo.append(opv)
        a += ln

# ---------------------------------------------------------------- jump tables
tables = {}   # table_addr -> (entry_size, targets_list)
# Scheduler task table: Func_0464 reads word at $04A0 + n*2 as task entry.
sched_tables = [(0x4A0, 4)]
for taddr, count in sched_tables:
    targets = []
    for i in range(count):
        t = ROM[taddr + i*2] | (ROM[taddr + i*2 + 1] << 8)
        targets.append(t)
    tables[taddr] = (2, targets)
    for t in targets:
        if is_valid_target(t) and t not in code and t not in cbcode:
            mnem, arg, opv = decode(t)
            if mnem != "INVALID":
                todo.append(t)

for a in sorted(code):
    if code[a][0] != "jp [hl]":
        continue
    # walk back over consecutive code looking for `ld hl,d16` with ROM imm
    p = a - 1
    found = None
    steps = 0
    while p >= 0 and steps < 16:
        if p not in code:
            break
        mnem, arg, opv = code[p]
        if mnem == "ld hl,d16" and 0 <= opv < 0x8000 and opv not in code \
           and not (0x100 <= opv < 0x150):
            found = (p, opv)
            break
        if mnem in ("ret", "reti", "jp d16") or mnem.startswith("ret "):
            break
        steps += 1
        p -= 1
    if found is None:
        continue
    p, taddr = found
    # entry size: count doubling ops between ld hl and jp [hl]
    doubles = 0
    for q in range(p+1, a):
        if q in code and code[q][0] in ("add a,a", "rlca", "add hl,hl",
                                        "sla a", "sll a", "add a,a"):
            doubles += 1
    esize = 2 << min(doubles, 3)
    # gather entries
    targets = []
    i = 0
    while True:
        w = taddr + i*esize
        if w + 2 > 0x8000:
            break
        t = ROM[w] | (ROM[w+1] << 8)
        if not (0 <= t < 0x8000):
            break
        targets.append(t)
        i += 1
        if i > 512:
            break
    if len(targets) >= 3:
        tables[taddr] = (esize, targets)

table_addrs = set(tables)
# queue table targets as code roots
for taddr, (esize, targets) in tables.items():
    for t in targets:
        if is_valid_target(t) and t not in code and t not in cbcode:
            # only accept if first byte decodes to a valid (non-INVALID) op
            mnem, arg, opv = decode(t)
            if mnem != "INVALID":
                todo.append(t)
        elif t in code:
            pass
        else:
            warn.append(f"table ${taddr:04X} target ${t:04X} rejected")

while todo:
    a = todo.pop()
    while 0 <= a < 0x8000:
        if a in code or a in cbcode:
            break
        mnem, arg, opv = decode(a)
        if mnem == "INVALID":
            pass
        code[a] = (mnem, arg, opv)
        if mnem == "PREFIX":
            m2, a2, o2 = decode(a, cb=True)
            cbcode[a] = (m2, a2, o2)
            ln = 2
        else:
            ln = oplen(mnem, arg)
        if mnem == "ret" or mnem == "reti":
            break
        if mnem == "jp [hl]":
            break
        if mnem == "stop":
            break
        if mnem == "jp d16":
            if is_valid_target(opv):
                todo.append(opv)
            break
        if mnem.startswith("jp ") or mnem.startswith("call") or mnem.startswith("jr"):
            if is_valid_target(opv):
                todo.append(opv)
        if mnem.startswith("rst"):
            todo.append(opv)
        a += ln

# ---------------------------------------------------------------- references
code_refs = set()   # addresses in code referenced as d16 (for labels)
data_refs = set()   # addresses in data referenced from code
ram_refs = set()
hram_refs = set()
# data regions first, so data_refs can be filtered by membership
occupied = set(code) | set(cbcode)
instr_end = {}
for a in code:
    ln = oplen(*code[a][:2])
    instr_end[a] = a + ln
for a in cbcode:
    instr_end[a] = a + 2
for a in (set(code) | set(cbcode)):
    for x in range(a, instr_end[a]):
        occupied.add(x)

data_regions = []
start = None
for a in range(0x150, 0x8000):   # $0100-$014F handled by header.asm
    if a in occupied:
        if start is not None:
            data_regions.append((start, a))
            start = None
    else:
        if start is None:
            start = a
if start is not None:
    data_regions.append((start, 0x8000))

def in_data_region(v):
    for s, e in data_regions:
        if s <= v < e:
            return True
    return False

for a in sorted(code):
    mnem, arg, opv = code[a]
    if opv is not None and (arg == "d16" or arg == "r8"):
        if 0 <= opv < 0x8000:
            if opv in code or opv in cbcode:
                code_refs.add(opv)
            elif in_data_region(opv):
                data_refs.add(opv)
        elif 0xC000 <= opv <= 0xDFFF:
            ram_refs.add(opv)
        elif 0xFF80 <= opv <= 0xFFFE:
            hram_refs.add(opv)
    elif arg == "a8" and opv is not None and 0xFF80 <= (0xFF00 | opv) <= 0xFFFE:
        hram_refs.add(0xFF00 | opv)
for taddr, (esize, targets) in tables.items():
    for t in targets:
        if t in code or t in cbcode:
            code_refs.add(t)
        else:
            data_refs.add(t)

# ---------------------------------------------------------------- data regions
# label every referenced data address
def data_label(a):
    return f"Data_{a:04X}"

# ---------------------------------------------------------------- emission
os.makedirs("src/data", exist_ok=True)

def esc_string(bs):
    out = []
    for b in bs:
        c = chr(b)
        if c == '"':
            out.append('\\"')
        elif c == "\\":
            out.append("\\\\")
        elif c == "{":
            out.append("\\{")
        elif c == "}":
            out.append("\\}")
        else:
            out.append(c)
    return "".join(out)

def fmt_d8(b):
    return f"${b:02X}"


VECTOR_NAMES = {0x00:"Rst_00",0x08:"Rst_08",0x10:"Rst_10",0x18:"Rst_18",
                0x20:"Rst_20",0x28:"Rst_28",0x30:"Rst_30",0x38:"Rst_38",
                0x40:"VBlank_Handler",0x48:"LCDC_Handler",0x50:"Timer_Handler",
                0x58:"Serial_Handler",0x60:"Joypad_Handler"}

def label_for(v):
    if v in VECTOR_NAMES:
        return VECTOR_NAMES[v]
    if v == 0x100:
        return "EntryPoint"
    if v in code or v in cbcode:
        return f"Func_{v:04X}"
    return data_label(v)

def fmt_d16(v):
    if 0 <= v < 0x8000:
        if v in code or v in cbcode or v in VECTOR_NAMES or v == 0x100:
            return label_for(v)
        if v in data_refs or v in table_addrs:
            return data_label(v)
    if 0xC000 <= v <= 0xDFFF:
        return f"w{v:04X}"
    if 0xFF80 <= v <= 0xFFFE:
        return f"h{v & 0xFF:02X}"
    return f"${v:04X}"

def fmt_a8(v):
    a = 0xFF00 | v
    if a in hram_refs:
        return f"h{v:02X}"
    return f"${a:04X}"

def fmt_r8(v):
    if v in code or v in cbcode or v in VECTOR_NAMES or v == 0x100:
        return label_for(v)
    return f"${v:04X}"

def fmt_sp8(v):
    return f"{v}" if v >= 0 else f"-{-v}"

def fmt_operand(mnem, arg, opv):
    if arg == "d8":
        return fmt_d8(opv)
    if arg == "d16":
        return fmt_d16(opv)
    if arg == "a8":
        return fmt_a8(opv)
    if arg == "r8":
        return fmt_r8(opv)
    if arg == "sp8":
        return fmt_sp8(opv)
    return ""


def fmt_mnem(mnem, arg, opv):
    """Clean RGBDS mnemonic with operand substituted."""
    if arg == "" or arg == "rst" or arg == "c":
        return mnem
    op = fmt_operand(mnem, arg, opv)
    if arg == "a8":
        return mnem.replace("a8", op)
    if arg == "sp8":
        if "sp+r8" in mnem:
            return mnem.replace("sp+r8", "sp+" + op)
        return mnem.replace("r8", op)
    tok = arg  # d8 / d16 / r8
    return mnem.replace(tok, op)

def emit_code_line(a):
    mnem, arg, opv = code.get(a, (None, None, None))
    if mnem is None:  # CB-prefixed instruction recorded in cbcode
        mnem, arg, opv = cbcode[a]
        s = f"\t{mnem} {fmt_operand(mnem, arg, opv)}".rstrip()
        return f"\tcb ; ${ROM[a]:02X}\n{s}"  # not used; see below
    s = f"\t{mnem} {fmt_operand(mnem, arg, opv)}".rstrip()
    return s

def ascii_gutter(bs):
    return "".join(chr(b) if 0x20 <= b <= 0x7E else "." for b in bs)

# ---- ram.inc
used_ram = sorted(ram_refs)
used_hram = sorted(hram_refs)
with open("src/ram.inc", "w", encoding="utf-8", newline="\n") as f:
    f.write("; Used RAM / HRAM addresses (auto-collected)\n")
    for a in used_ram:
        f.write(f"DEF w{a:04X} EQU ${a:04X}\n")
    for a in used_hram:
        f.write(f"DEF h{a & 0xFF:02X} EQU ${a:04X}\n")

# ---- vectors.asm ($0000-$00FF)
with open("src/vectors.asm", "w", encoding="utf-8", newline="\n") as f:
    f.write("; ============================================================\n")
    f.write("; RST vectors and interrupt vectors ($0000-$00FF)\n")
    f.write("; ============================================================\n")
    a = 0
    while a < 0x100:
        if a in code or a in cbcode:
            if a in code:
                mnem, arg, opv = code[a]
                ln = 2 if mnem == "PREFIX" else oplen(mnem, arg)
            else:
                mnem, arg, opv = cbcode[a]
                ln = 2
            name = {0x00:"Rst_00",0x08:"Rst_08",0x10:"Rst_10",0x18:"Rst_18",
                    0x20:"Rst_20",0x28:"Rst_28",0x30:"Rst_30",0x38:"Rst_38",
                    0x40:"VBlank_Handler",0x48:"LCDC_Handler",0x50:"Timer_Handler",
                    0x58:"Serial_Handler",0x60:"Joypad_Handler"}.get(a)
            if name:
                f.write(f"\n{name}:\n")
            elif a in code_refs:
                f.write(f"\nFunc_{a:04X}:\n")
            elif a in data_refs:
                f.write(f"\n{data_label(a)}:\n")
            if mnem == "PREFIX":
                f.write("\t" + fmt_mnem(*cbcode[a]).rstrip() + "\n")
            elif mnem == "INVALID":
                f.write(f"\tdb ${ROM[a]:02X} ; invalid opcode (executes as NOP on DMG)\n")
            else:
                f.write("\t" + fmt_mnem(mnem, arg, opv).rstrip() + "\n")
            a += ln
        else:
            # unused vector slot: raw bytes
            if a in data_refs:
                f.write(f"\n{data_label(a)}:\n")
            f.write(f"\tdb ${ROM[a]:02X} ; ${a:04X}\n")
            a += 1
    f.write("\n")

# ---- header.asm ($0100-$014F)
with open("src/header.asm", "w", encoding="utf-8", newline="\n") as f:
    f.write("; ============================================================\n")
    f.write("; Cartridge header ($0100-$014F)\n")
    f.write("; ============================================================\n")
    f.write("\nEntryPoint:\n")
    f.write(f"\tnop\n\tjp Func_{ROM[0x102] | (ROM[0x103] << 8):04X}\n")
    f.write("\nNintendoLogo:\n")
    logo = ROM[0x104:0x134]
    for i in range(0, len(logo), 16):
        row = logo[i:i+16]
        f.write("\tdb " + ",".join(fmt_d8(b) for b in row) + "\n")
    f.write(f'\tdb "{esc_string(ROM[0x134:0x13A])}" ; title "CATRAP"\n')
    f.write("\tdb " + ",".join(fmt_d8(b) for b in ROM[0x13A:0x144]) + "\n")
    f.write("\tdb " + ",".join(fmt_d8(b) for b in ROM[0x144:0x14D]) + "\n")
    f.write("; $14D: header checksum, $14E-$14F: global checksum (rgbfix)\n")
    f.write("\tdb $00, $00, $00\n")

# ---- data region files
def emit_data_region(f, start, end, table_info=None, indent=""):
    """Emit bytes [start,end) as db/dw; returns list of (addr,label) emitted."""
    a = start
    labels_out = []
    refs_in_region = sorted(r for r in data_refs if start <= r < end)
    while a < end:
        # label?
        if a in data_refs or (table_info and a == table_info[0]):
            f.write(f"{data_label(a)}:\n")
            labels_out.append(a)
        if table_info and a >= table_info[0] and a < table_info[0] + table_info[1]*len(table_info[2]):
            esize, targets = table_info[1], table_info[2]
            idx = (a - table_info[0]) // esize
            if (a - table_info[0]) % esize == 0 and idx < len(targets):
                t = targets[idx]
                f.write(f"\tdw {fmt_d16(t)}\n")
                a += 2
                continue
        # string? (stop at referenced addresses so labels can be emitted)
        if a + 3 <= end:
            run = []
            p = a
            while p < end and 0x20 <= ROM[p] <= 0x7E and p not in data_refs:
                run.append(ROM[p]); p += 1
            if len(run) >= 3:
                # swallow one trailing NUL as terminator
                term = ""
                if p < end and ROM[p] == 0:
                    term = ", 0"
                    p += 1
                f.write(f'\tdb "{esc_string(bytes(run))}"{term}\n')
                a = p
                continue
        # raw row of up to 16 (break at referenced addresses for labels)
        row_end = min(a+16, end)
        for r in sorted(refs_in_region):
            if a < r < row_end:
                row_end = r
                break
        row = ROM[a:row_end]
        f.write(f"\tdb {','.join(fmt_d8(b) for b in row)} ; {ascii_gutter(row)}\n")
        a += len(row)
    return labels_out

for (start, end) in data_regions:
    fname = f"src/data/data_{start:04X}.asm"
    with open(fname, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"; Data region ${start:04X}-${end-1:04X}\n")
        tbl = tables.get(start)
        emit_data_region(f, start, end, (start, tbl[0], tbl[1]) if tbl else None)
    # fix labels emitted inside for referenced addrs (they were handled above)

# ---- code.asm ($0150..)
lo = open("src/code_lo.asm", "w", encoding="utf-8", newline="\n")
hi = open("src/code_hi.asm", "w", encoding="utf-8", newline="\n")
lo.write("; ============================================================\n")
lo.write("; Main code ($0150-$3FFF) - ROM0\n")
lo.write("; ============================================================\n")
hi.write("; ============================================================\n")
hi.write("; Main code ($4000-$7FFF) - ROMX bank 1\n")
hi.write("; ============================================================\n")

def emit_line(f, s):
    f.write(s + "\n")

a = 0x150
data_idx = 0
dr = iter(data_regions)
next_region = next(dr, None)
emitted_until = 0x150
while a < 0x8000:
    f = lo if a < 0x4000 else hi
    if next_region and a >= next_region[0]:
        start, end = next_region
        emit_line(f, f"\n; ---- data ${start:04X}-${end-1:04X} ----")
        emit_line(f, f'INCLUDE "src/data/data_{start:04X}.asm"')
        a = end
        emitted_until = end
        next_region = next(dr, None)
        continue
    if a in code or a in cbcode:
        if a < emitted_until:
            # byte already emitted as an operand of a previous instruction
            # (the game jumps into instruction operands)
            if a in code_refs:
                emit_line(f, f"\nFunc_{a:04X}: ; jump target inside previous instruction")
            emit_line(f, f"\t; overlaps previous instruction")
            a += 1
            continue
        if a in code_refs or a == 0x150:
            emit_line(f, f"\nFunc_{a:04X}:")
        if a in code:
            mnem, arg, opv = code[a]
            ln = 2 if mnem == "PREFIX" else oplen(mnem, arg)
            inside = [x for x in range(a + 1, a + ln) if x in code_refs]
            if inside:
                # instruction with jump targets inside its operand bytes:
                # emit as raw bytes split at the labels
                pos = a
                for x in inside:
                    if x > pos:
                        emit_line(f, "\tdb " + ",".join(fmt_d8(b) for b in ROM[pos:x]))
                    emit_line(f, f"\nFunc_{x:04X}: ; jump target inside previous instruction")
                    pos = x
                if pos < a + ln:
                    emit_line(f, "\tdb " + ",".join(fmt_d8(b) for b in ROM[pos:a+ln]))
            elif mnem == "PREFIX":
                emit_line(f, "\t" + fmt_mnem(*cbcode[a]).rstrip())
            elif mnem == "INVALID":
                emit_line(f, f"\tdb ${ROM[a]:02X} ; invalid opcode (NOP on DMG)")
            elif mnem == "stop":
                emit_line(f, f"\tdb ${ROM[a]:02X}, ${ROM[a+1]:02X} ; stop (operand preserved)")
            else:
                emit_line(f, "\t" + fmt_mnem(mnem, arg, opv).rstrip())
        else:
            mnem, arg, opv = cbcode[a]
            emit_line(f, "\t" + fmt_mnem(mnem, arg, opv).rstrip())
            ln = 2
        a += ln
        emitted_until = a
    else:
        emit_line(f, f"\t; gap: ${a:04X} unreachable (data)")
        a += 1

lo.close()
hi.close()

# ---- main.asm
DOC = """; ============================================================
; CATRAP (USA) - Game Boy (Kemco, 1990)
; Complete disassembly
; Build: python build.py   (reproduces "Catrap (USA).gb" byte-for-byte)
; ============================================================
;
; ARCHITECTURE
; ------------
; Catrap runs a cooperative task scheduler:
;
;   TaskDispatcher - round-robins up to 6 task slots ($DE00-$DE05 hold
;   task states).  A task's saved stack pointer lives at $DE00 + n*2 + 6,
;   pointing at its register frame; the dispatcher restores hl/de/bc and
;   returns into the task.  Entry points come from the table at $04A0:
;   task 0 = TaskTitle, task 1 = TaskGame, task 2 = TaskHud,
;   task 3 = TaskInput.  RegisterTask sets up a slot: entry pointer at
;   base-1/base, initial SP at base-7.
;
;   TaskYield - Rst_10/Rst_30 handler.  Saves the task's state (A) and
;   stack pointer, restores the main loop's SP and dispatches the next
;   task; after task 6 wraps, control returns to the main loop.
;
; RST API (used by tasks):
;   Rst_00 - JoypadReadRst00 (debounced joypad read)
;   Rst_10 - yield with state = A        Rst_30 - yield with state = 1
;   Rst_18 - read a byte from table at de (Z if zero)
;   Rst_20 - read a word from table at de into $FF93/$FF94
;   Rst_28 - DelayLoop
;
; Main loop: read joypad, TaskDispatcher, SoundChannelsUpdate,
; MusicUpdate, MusicUpdate2, wait for VBlank.  The VBlank handler runs
; the OAM DMA routine from HRAM, copies the pending text string, and
; signals via $FF8F.
;
; Sound: state-driven sequencers MusicUpdate ($FFFB state -> $44F4
; table) and MusicUpdate2 ($FFFD -> $454C), feeding SoundChannelsUpdate
; which drives the NRxx registers.
;
; ------------------------------------------------------------
"""
with open("main.asm", "w", encoding="utf-8", newline="\n") as f:
    f.write(DOC)
    f.write('INCLUDE "hardware.inc"\n')
    f.write('INCLUDE "src/ram.inc"\n')
    f.write('\nSECTION "ROM0", ROM0[$0000]\n')
    f.write('INCLUDE "src/vectors.asm"\n')
    f.write('INCLUDE "src/header.asm"\n')
    f.write('INCLUDE "src/code_lo.asm"\n')
    f.write('\nSECTION "ROM1", ROMX[$4000]\n')
    f.write('INCLUDE "src/code_hi.asm"\n')

print(f"code instrs: {len(code)}")
print(f"cb instrs: {len(cbcode)}")
print(f"data regions: {len(data_regions)}")
print(f"jump tables: {len(tables)} -> {[(hex(k), v[0], len(v[1])) for k, v in tables.items()]}")
print(f"warnings: {len(warn)}")
for w in warn[:40]:
    print("  ", w)
