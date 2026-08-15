#!/usr/bin/env python3
"""Minimal SM83 interpreter to trace actual code execution in Catrap (USA).gb.

Purpose: find every executed address (including code reached through
executed-string jumps and the task scheduler's ret-dispatch), so the static
disassembler can merge dynamic coverage into its code set.

Not cycle-accurate; enough for control-flow tracing.
"""
import sys
from disasm import ROM, OPS, CBOPS, oplen, s8

class CPU:
    def __init__(self):
        self.a = self.f = self.b = self.c = self.d = self.e = self.h = self.l = 0
        self.sp = 0
        self.pc = 0x100
        self.ime = 0
        self.halted = False
        self.ram = bytearray(0x8000)      # $C000-$DFFF + $E000-$FDFF alias
        self.vram = bytearray(0x2000)     # $8000-$9FFF
        self.hram = bytearray(0x80)       # $FF80-$FFFF
        self.io = bytearray(0x80)         # $FF00-$FF7F
        self.ie = 0
        self.cycles = 0
        self.trace = set()
        self.dbg = False                # executed pcs
        self.log = []                     # ordered pc log
        self.scan_cycles = 0
        self.ly = 0
        self.buttons = 0x0F   # 0 = pressed (bit0 Start, bit1 Select, bit2 B, bit3 A)
        self.dpad = 0x0F     # 0 = pressed (bit0 Right, bit1 Left, bit2 Up, bit3 Down)
        self.input_script = []
        self.pz = []
        self.ed = []
        self.notelog = []
        self.step_limit = 0

    def rb(self, a):
        a &= 0xFFFF
        if a < 0x8000:
            return ROM[a]
        if 0x8000 <= a < 0xA000:
            return self.vram[a - 0x8000]
        if 0xA000 <= a < 0xC000:
            return 0
        if 0xC000 <= a < 0xE000:
            return self.ram[a - 0xC000]
        if 0xE000 <= a < 0xFE00:
            return self.ram[a - 0xE000]
        if 0xFE00 <= a < 0xFEA0:         # OAM
            return 0
        if 0xFF00 <= a < 0xFF80:
            if a == 0xFF00:
                sel = self.io[0x00] & 0x30
                if sel & 0x20:
                    return sel | self.dpad      # P14 low: d-pad row
                if sel & 0x10:
                    return sel | self.buttons   # P15 low: button row
                return sel | (self.dpad & self.buttons)
            return self.io[a - 0xFF00]
        if 0xFF80 <= a:
            return self.hram[a - 0xFF80]
        return 0

    def wb(self, a, v):
        v &= 0xFF
        a &= 0xFFFF
        if a < 0x8000:
            pass                          # ROM: writes ignored (no MBC)
        elif 0x8000 <= a < 0xA000:
            self.vram[a - 0x8000] = v
        elif 0xA000 <= a < 0xC000:
            pass
        elif 0xC000 <= a < 0xE000:
            self.ram[a - 0xC000] = v
        elif 0xE000 <= a < 0xFE00:
            self.ram[a - 0xE000] = v
        elif 0xFF00 <= a < 0xFF80:
            if a == 0xFF00:
                self.io[0x00] = (v & 0x30) | 0x0F
            else:
                self.io[a - 0xFF00] = v
        elif 0xFF80 <= a:
            if a == 0xFFE1 and self.cycles > 16000000 and len(self.notelog) < 30:
                self.notelog.append((self.cycles, 0xE5, self.pc, v))
            self.hram[a - 0xFF80] = v

    def rw(self, a):
        return self.rb(a) | (self.rb(a + 1) << 8)

    def ww(self, a, v):
        self.wb(a, v & 0xFF)
        self.wb(a + 1, (v >> 8) & 0xFF)

    # flags: bit7 Z, bit6 N, bit5 H, bit4 C
    def getf(self):
        return self.f & 0xF0

    def setf(self, z=None, n=None, h=None, c=None):
        if z is not None: self.f = (self.f & 0x7F) | (0x80 if z else 0)
        if n is not None: self.f = (self.f & 0xBF) | (0x40 if n else 0)
        if h is not None: self.f = (self.f & 0xDF) | (0x20 if h else 0)
        if c is not None: self.f = (self.f & 0xEF) | (0x10 if c else 0)

    def push(self, v):
        self.sp = (self.sp - 2) & 0xFFFF
        self.ww(self.sp, v)

    def pop(self):
        v = self.rw(self.sp)
        self.sp = (self.sp + 2) & 0xFFFF
        return v

    def int_check(self):
        if self.ime and self.halted:
            self.halted = False
        if self.ime:
            req = self.io[0x0F] & self.hram[0x7F] & 0x1F
            if req:
                self.ime = 0
                self.halted = False
                if req & 1:
                    self.push(self.pc); self.pc = 0x40
                elif req & 2:
                    self.push(self.pc); self.pc = 0x48
                elif req & 4:
                    self.push(self.pc); self.pc = 0x50
                elif req & 8:
                    self.push(self.pc); self.pc = 0x58
                elif req & 0x10:
                    self.push(self.pc); self.pc = 0x60
                self.io[0x0F] &= ~req

    def run(self, limit):
        while self.cycles < limit:
            # alternating button presses: guarantees edges whenever the game polls
            # scripted input: A presses (menu confirm) + Right presses (level clear)
            if 16500000 < self.cycles < 16550000:
                self.buttons = 0x07      # Start tap
            if self.cycles > 16540000 and self.cycles - getattr(self, 'last_pz', 0) > 50000 and len(getattr(self, 'pz', [])) < 40:
                self.pz.append((self.cycles, self.hram[0x12], self.hram[0x3B], self.rb(0xDDA1), self.hram[0xD5-0x80]))
                self.last_pz = self.cycles
            phase = (self.cycles // 80000) % 4
            if self.cycles > 16200000:
                self.buttons = 0x0E   # hold A (jump right)
                self.dpad = 0x0E      # hold dpad right
            else:
                if phase == 0 or phase == 2:
                    self.buttons = 0x0E
                elif phase == 1:
                    self.buttons = 0x0B
                else:
                    self.buttons = 0x0F
                self.dpad = 0x0F
            self.scan_cycles += 1
            if self.scan_cycles >= 456:
                self.scan_cycles = 0
                self.ly = (self.ly + 1) % 154
                if self.ly == 144:
                    self.io[0x0F] |= 0x01   # VBlank request
                self.io[0x44] = self.ly
            if self.halted:
                self.cycles += 4
                self.int_check()
                continue
            self.int_check()
            self.trace.add(self.pc)

            if self.pc == 0x613 and hasattr(self, 'dumped') and not hasattr(self, 'drawn'):
                self.drawn = True
                with open('level_vram.txt', 'w') as f:
                    for r in range(18):
                        row = [self.vram[0x1800 + r*32 + c] for c in range(20)]
                        f.write(' '.join(f'{v:02X}' for v in row) + '\n')
                with open('level_tiles.bin', 'wb') as f:
                    f.write(bytes(self.vram[0x0000:0x1800]))
                with open('level_mapc2.txt', 'w') as f:
                    for r in range(24):
                        row = [self.rb(0xC2C2 + r*32 + c) for c in range(32)]
                        f.write(' '.join(f'{v:02X}' for v in row) + '\n')
            if len(self.log) < 400000:
                self.log.append(self.pc)
            self.step()
            self.cycles += 1
            if self.pc == 0x150 and len(self.trace) > 1000:
                pass

    def step(self):
        pc = self.pc
        op = self.rb(pc)
        self.pc = (pc + 1) & 0xFFFF
        # ---- 8-bit helpers ----
        def r8(i):
            return [self.b, self.c, self.d, self.e, self.h, self.l, self.rb(hl_val()), self.a][i]
        def w8(i, v):
            v &= 0xFF
            regs = [self.b, self.c, self.d, self.e, self.h, self.l, None, self.a]
            if i == 6:
                self.wb(hl_val(), v)
            else:
                regs[i] = v
            if i == 0: self.b = v
            elif i == 1: self.c = v
            elif i == 2: self.d = v
            elif i == 3: self.e = v
            elif i == 4: self.h = v
            elif i == 5: self.l = v
            elif i == 7: self.a = v
        def hl():
            return (self.h << 8) | self.l
        def hl_val():
            return (self.h << 8) | self.l
        def set_hl(v):
            v &= 0xFFFF
            self.h = v >> 8; self.l = v & 0xFF
        def bc():
            return (self.b << 8) | self.c
        def de():
            return (self.d << 8) | self.e
        def imm8():
            v = self.rb(self.pc); self.pc = (self.pc + 1) & 0xFFFF; return v
        def imm16():
            v = self.rb(self.pc) | (self.rb(self.pc + 1) << 8)
            self.pc = (self.pc + 2) & 0xFFFF
            return v
        def flags():
            return self.getf()
        def setf4(z, n, h, c):
            self.setf(z=z, n=n, h=h, c=c)
        # ---- decode ----
        if op == 0xCB:
            cop = self.rb(self.pc)
            self.pc = (self.pc + 1) & 0xFFFF
            self.cb(cop, r8, w8, set_hl)
            return
        mnem, arg = OPS[op]
        v = None
        if arg == "d8": v = imm8()
        elif arg == "d16": v = imm16()
        elif arg == "r8": v = s8(self.rb(self.pc)); self.pc = (self.pc + 1) & 0xFFFF
        elif arg == "a8": v = imm8()
        elif arg == "sp8": v = s8(self.rb(self.pc)); self.pc = (self.pc + 1) & 0xFFFF
        self.exec_op(op, mnem, arg, v, r8, w8, hl, set_hl, bc, de, imm8, imm16)

    def cb(self, cop, r8, w8, set_hl):
        reg = cop & 7
        bit = (cop >> 3) & 7
        opc = cop >> 6
        val = r8(reg)
        if opc == 0:  # rotate/shift group (with [hl])
            if bit == 0:  # rlc
                c = val >> 7
                val = ((val << 1) | c) & 0xFF
                w8(reg, val)
                self.setf(z=val == 0, n=False, h=False, c=c)
            elif bit == 1:  # rrc
                c = val & 1
                val = ((val >> 1) | (c << 7)) & 0xFF
                w8(reg, val)
                self.setf(z=val == 0, n=False, h=False, c=c)
            elif bit == 2:  # rl
                c = val >> 7
                val = ((val << 1) | (1 if self.f & 0x10 else 0)) & 0xFF
                w8(reg, val)
                self.setf(z=val == 0, n=False, h=False, c=c)
            elif bit == 3:  # rr
                c = val & 1
                val = ((val >> 1) | (0x80 if self.f & 0x10 else 0)) & 0xFF
                w8(reg, val)
                self.setf(z=val == 0, n=False, h=False, c=c)
            elif bit == 4:  # sla
                c = val >> 7
                val = (val << 1) & 0xFF
                w8(reg, val)
                self.setf(z=val == 0, n=False, h=False, c=c)
            elif bit == 5:  # sra
                c = val & 1
                val = ((val >> 1) | (val & 0x80)) & 0xFF
                w8(reg, val)
                self.setf(z=val == 0, n=False, h=False, c=c)
            elif bit == 6:  # swap
                val = ((val << 4) | (val >> 4)) & 0xFF
                w8(reg, val)
                self.setf(z=val == 0, n=False, h=False, c=False)
            else:  # srl
                c = val & 1
                val = val >> 1
                w8(reg, val)
                self.setf(z=val == 0, n=False, h=False, c=c)
        elif opc == 1:  # bit
            self.setf(z=(val >> bit) & 1 == 0, n=False, h=True)
        elif opc == 2:  # res
            w8(reg, val & ~(1 << bit))
        else:  # set
            w8(reg, val | (1 << bit))

    def exec_op(self, op, mnem, arg, v, r8, w8, hl, set_hl, bc, de, imm8, imm16):
        f = self.getf()
        zf = bool(f & 0x80); cf = bool(f & 0x10)
        # LD r,r / ALU r handled by opcode ranges
        if 0x40 <= op <= 0x7F and op != 0x76:
            w8(op >> 3 & 7, r8(op & 7)); return
        if 0x80 <= op <= 0xBF:
            self.alu((op - 0x80) >> 3, r8(op & 7)); return
        if op == 0x00: return  # nop
        if op == 0x76: self.halted = True; return  # halt
        if op == 0x01: setattr(self, ['b','c'][0], v >> 8); self.c = v & 0xFF; return
        if op == 0x02: self.wb(bc(), self.a); return
        if op == 0x03: self.set_bc(bc() + 1); return
        if op == 0x04: self.inc('b'); return
        if op == 0x05: self.dec('b'); return
        if op == 0x06: self.b = v; return
        if op == 0x07:  # rlca
            c = self.a >> 7
            self.a = ((self.a << 1) | c) & 0xFF
            self.setf(z=False, n=False, h=False, c=c); return
        if op == 0x08: self.ww(v, self.sp); return
        if op == 0x09: self.add_hl(bc()); return
        if op == 0x0A: self.a = self.rb(bc()); return
        if op == 0x0B: self.set_bc(bc() - 1); return
        if op == 0x0C: self.inc('c'); return
        if op == 0x0D: self.dec('c'); return
        if op == 0x0E: self.c = v; return
        if op == 0x0F:  # rrca
            c = self.a & 1
            self.a = ((self.a >> 1) | (c << 7)) & 0xFF
            self.setf(z=False, n=False, h=False, c=c); return
        if op == 0x10: self.halted = True; self.pc = (self.pc + 1) & 0xFFFF; return
        if op == 0x11: self.d = v >> 8; self.e = v & 0xFF; return
        if op == 0x12: self.wb(de(), self.a); return
        if op == 0x13: self.set_de(de() + 1); return
        if op == 0x14: self.inc('d'); return
        if op == 0x15: self.dec('d'); return
        if op == 0x16: self.d = v; return
        if op == 0x17:  # rla
            c = self.a >> 7
            self.a = ((self.a << 1) | (1 if cf else 0)) & 0xFF
            self.setf(z=False, n=False, h=False, c=c); return
        if op == 0x18: self.pc = (self.pc + v) & 0xFFFF; return
        if op == 0x19: self.add_hl(de()); return
        if op == 0x1A: self.a = self.rb(de()); return
        if op == 0x1B: self.set_de(de() - 1); return
        if op == 0x1C: self.inc('e'); return
        if op == 0x1D: self.dec('e'); return
        if op == 0x1E: self.e = v; return
        if op == 0x1F:  # rra
            c = self.a & 1
            self.a = ((self.a >> 1) | (0x80 if cf else 0)) & 0xFF
            self.setf(z=False, n=False, h=False, c=c); return
        if op == 0x20:  # jr nz
            if not zf: self.pc = (self.pc + v) & 0xFFFF
            return
        if op == 0x21: set_hl(v); return
        if op == 0x22: self.wb(hl(), self.a); set_hl(hl() + 1); return
        if op == 0x23: set_hl(hl() + 1); return
        if op == 0x24: self.inc('h'); return
        if op == 0x25: self.dec('h'); return
        if op == 0x26: self.h = v; return
        if op == 0x27:  # daa
            a = self.a
            if not cf and (a & 0x0F) <= 9 and not (f & 0x20):
                pass
            adj = 0
            if (f & 0x20) or (a & 0x0F) > 9:
                adj |= 0x06
            if cf or a > 0x99:
                adj |= 0x60
                self.setf(c=True)
            if f & 0x40:
                self.a = (a - adj) & 0xFF
            else:
                self.a = (a + adj) & 0xFF
            self.setf(z=self.a == 0, h=False)
            return
        if op == 0x28:
            if zf: self.pc = (self.pc + v) & 0xFFFF
            return
        if op == 0x29: self.add_hl(hl()); return
        if op == 0x2A: self.a = self.rb(hl()); set_hl(hl() + 1); return
        if op == 0x2B: set_hl(hl() - 1); return
        if op == 0x2C: self.inc('l'); return
        if op == 0x2D: self.dec('l'); return
        if op == 0x2E: self.l = v; return
        if op == 0x2F: self.a ^= 0xFF; self.setf(n=True, h=True); return
        if op == 0x30:
            if not cf: self.pc = (self.pc + v) & 0xFFFF
            return
        if op == 0x31: self.sp = v; return
        if op == 0x32: self.wb(hl(), self.a); set_hl(hl() - 1); return
        if op == 0x33: self.sp = (self.sp + 1) & 0xFFFF; return
        if op == 0x34:  # inc [hl]
            x = self.rb(hl()); x = (x + 1) & 0xFF
            self.wb(hl(), x)
            self.setf(z=x == 0, n=False, h=(x & 0x0F) == 0); return
        if op == 0x35:
            x = self.rb(hl()); x = (x - 1) & 0xFF
            self.wb(hl(), x)
            self.setf(z=x == 0, n=True, h=(x & 0x0F) == 0x0F); return
        if op == 0x36: self.wb(hl(), v); return
        if op == 0x37: self.setf(n=False, h=False, c=True); return
        if op == 0x38:
            if cf: self.pc = (self.pc + v) & 0xFFFF
            return
        if op == 0x39: self.add_hl(self.sp); return
        if op == 0x3A: self.a = self.rb(hl()); set_hl(hl() - 1); return
        if op == 0x3B: self.sp = (self.sp - 1) & 0xFFFF; return
        if op == 0x3C: self.inc('a'); return
        if op == 0x3D: self.dec('a'); return
        if op == 0x3E: self.a = v; return
        if op == 0x3F: self.setf(n=False, h=False, c=not cf); return
        if op == 0xC0:
            if not zf: self.pc = self.pop()
            return
        if op == 0xC1: self.set_bc(self.pop()); return
        if op == 0xC2:
            if not zf: self.pc = v
            return
        if op == 0xC3: self.pc = v; return
        if op == 0xC4:
            if not zf: self.push(self.pc); self.pc = v
            return
        if op == 0xC5: self.push(bc()); return
        if op == 0xC6: self.alu(0, v); return
        if op == 0xC7: self.push(self.pc); self.pc = 0x00; return
        if op == 0xC8:
            if zf: self.pc = self.pop()
            return
        if op == 0xC9: self.pc = self.pop(); return
        if op == 0xCA:
            if zf: self.pc = v
            return
        if op == 0xCC:
            if zf: self.push(self.pc); self.pc = v
            return
        if op == 0xCD: self.push(self.pc); self.pc = v; return
        if op == 0xCE: self.alu(1, v); return
        if op == 0xCF: self.push(self.pc); self.pc = 0x08; return
        if op == 0xD0:
            if not cf: self.pc = self.pop()
            return
        if op == 0xD1: self.set_de(self.pop()); return
        if op == 0xD2:
            if not cf: self.pc = v
            return
        if op == 0xD4:
            if not cf: self.push(self.pc); self.pc = v
            return
        if op == 0xD5: self.push(de()); return
        if op == 0xD6: self.alu(2, v); return
        if op == 0xD7: self.push(self.pc); self.pc = 0x10; return
        if op == 0xD8:
            if cf: self.pc = self.pop()
            return
        if op == 0xD9: self.pc = self.pop(); self.ime = 1; return
        if op == 0xDA:
            if cf: self.pc = v
            return
        if op == 0xDC:
            if cf: self.push(self.pc); self.pc = v
            return
        if op == 0xDE: self.alu(3, v); return
        if op == 0xDF: self.push(self.pc); self.pc = 0x18; return
        if op == 0xE0: self.wb(0xFF00 | v, self.a); return
        if op == 0xE1: set_hl(self.pop()); return
        if op == 0xE2: self.wb(0xFF00 | self.c, self.a); return
        if op == 0xE5: self.push(hl()); return
        if op == 0xE6: self.alu(4, v); return
        if op == 0xE7: self.push(self.pc); self.pc = 0x20; return
        if op == 0xE8:  # add sp,r8
            r = self.sp + v
            self.sp = r & 0xFFFF
            self.setf(z=False, n=False, h=(self.sp & 0xF) < (v & 0xF) if v >= 0 else ((self.sp & 0xF) > ((self.sp - (-v)) & 0xF)), c=False)
            return
        if op == 0xE9: self.pc = hl(); return
        if op == 0xEA: self.wb(v, self.a); return
        if op == 0xEE: self.alu(5, v); return
        if op == 0xEF: self.push(self.pc); self.pc = 0x28; return
        if op == 0xF0: self.a = self.rb(0xFF00 | v); return
        if op == 0xF1: vv = self.pop(); self.a = vv >> 8; self.f = vv & 0xF0; return
        if op == 0xF2: self.a = self.rb(0xFF00 | self.c); return
        if op == 0xF3: self.ime = 0; return
        if op == 0xF5: self.push((self.a << 8) | self.f); return
        if op == 0xF6: self.alu(6, v); return
        if op == 0xF7: self.push(self.pc); self.pc = 0x30; return
        if op == 0xF8:  # ld hl, sp+r8
            set_hl((self.sp + v) & 0xFFFF)
            self.setf(z=False, n=False, h=False, c=False); return
        if op == 0xF9: self.sp = hl(); return
        if op == 0xFA: self.a = self.rb(v); return
        if op == 0xFB: self.ime = 1; return
        if op == 0xFE: self.alu(7, v); return
        if op == 0xFF: self.push(self.pc); self.pc = 0x38; return
        raise SystemExit(f"unhandled op {op:02X}")

    # helpers
    def set_bc(self, v):
        v &= 0xFFFF; self.b = v >> 8; self.c = v & 0xFF
    def set_de(self, v):
        v &= 0xFFFF; self.d = v >> 8; self.e = v & 0xFF
    def add_hl(self, v):
        hl = (self.h << 8) | self.l
        r = hl + v
        self.setf(n=False, h=(hl & 0xFFF) + (v & 0xFFF) > 0xFFF, c=r > 0xFFFF)
        self.h = (r >> 8) & 0xFF; self.l = r & 0xFF
    def inc(self, r):
        v = getattr(self, r)
        nv = (v + 1) & 0xFF
        setattr(self, r, nv)
        self.setf(z=nv == 0, n=False, h=(v & 0xF) == 0xF)
    def dec(self, r):
        v = getattr(self, r)
        nv = (v - 1) & 0xFF
        setattr(self, r, nv)
        self.setf(z=nv == 0, n=True, h=(v & 0xF) == 0)
    def alu(self, kind, v):
        a = self.a
        if kind == 0:  # add
            r = a + v
            self.setf(z=(r & 0xFF) == 0, n=False, h=(a & 0xF) + (v & 0xF) > 0xF, c=r > 0xFF)
            self.a = r & 0xFF
        elif kind == 1:  # adc
            c = 1 if self.f & 0x10 else 0
            r = a + v + c
            self.setf(z=(r & 0xFF) == 0, n=False, h=(a & 0xF) + (v & 0xF) + c > 0xF, c=r > 0xFF)
            self.a = r & 0xFF
        elif kind == 2:  # sub
            r = a - v
            self.setf(z=(r & 0xFF) == 0, n=True, h=(a & 0xF) < (v & 0xF), c=a < v)
            self.a = r & 0xFF
        elif kind == 3:  # sbc
            c = 1 if self.f & 0x10 else 0
            r = a - v - c
            self.setf(z=(r & 0xFF) == 0, n=True, h=(a & 0xF) < (v & 0xF) + c, c=a < v + c)
            self.a = r & 0xFF
        elif kind == 4:  # and
            self.a &= v
            self.setf(z=self.a == 0, n=False, h=True, c=False)
        elif kind == 5:  # xor
            self.a ^= v
            self.setf(z=self.a == 0, n=False, h=False, c=False)
        elif kind == 6:  # or
            self.a |= v
            self.setf(z=self.a == 0, n=False, h=False, c=False)
        elif kind == 7:  # cp
            r = a - v
            self.setf(z=(r & 0xFF) == 0, n=True, h=(a & 0xF) < (v & 0xF), c=a < v)

def main():
    cpu = CPU()
    cpu.input_script = []  # hardcoded phase input drives the game
    # boot: entry at 0x100
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 300000
    frames = 0
    cpu.run(limit)
    out = sorted(cpu.trace)
    print(f"cycles {cpu.cycles}, executed addresses: {len(out)}")
    print(f"pc={cpu.pc:04X} sp={cpu.sp:04X} a={cpu.a:02X}")
    for row in cpu.pz:
        print(f"PAUSE cyc={row[0]} FF92={row[1]:02X} FF8B={row[2]:02X} DDA1={row[3]:02X} D5={row[4]:02X}")
    with open("trace.txt", "w") as f:
        for a in out:
            f.write(f"{a:04X}\n")
    with open("notelog.txt", "w") as f:
        for row in cpu.notelog:
            if len(row) == 3:
                cyc, c, a = row
                f.write(f"{cyc} {c:02X} {a:02X}\n")
            else:
                cyc, c, a, m = row
                f.write(f"{cyc} {c:02X} {a:02X} {m}\n")
    # dump $C100-$C3FF and $C2A2-$C3E2 raw
    with open("buffers.txt", "w") as f:
        f.write("C0E0-C100:\n")
        for a in range(0xC0E0, 0xC100, 16):
            f.write(f"{a:04X}: " + " ".join(f"{cpu.rb(a+i):02X}" for i in range(16)) + "\n")
        f.write("C100-C1FF:\n")
        for a in range(0xC100, 0xC200, 16):
            f.write(f"{a:04X}: " + " ".join(f"{cpu.rb(a+i):02X}" for i in range(16)) + "\n")
        f.write("\nC2A2-C3E2 (draw output):\n")
        for a in range(0xC2A2, 0xC3E2, 16):
            f.write(f"{a:04X}: " + " ".join(f"{cpu.rb(a+i):02X}" for i in range(16)) + "\n")
    # final state dump: BG map + C2C2 + C110
    with open("final_state.txt", "w") as f:
        f.write("BG map $9800 (20x18):\n")
        for r in range(18):
            row = [cpu.rb(0x9800 + r*32 + c) for c in range(20)]
            f.write(" ".join(f"{v:02X}" for v in row) + "\n")
        f.write("\nC2C2 tilemap (first 13 rows):\n")
        for r in range(13):
            row = [cpu.rb(0xC2C2 + r*32 + c) for c in range(32)]
            f.write(" ".join(f"{v:02X}" for v in row) + "\n")
        f.write("\nC110 screen buffer:\n")
        for r in range(8):
            row = [cpu.rb(0xC110 + r*16 + c) for c in range(13)]
            f.write(" ".join(f"{v:02X}" for v in row) + "\n")
    with open("trace_ordered.txt", "w") as f:
        for a in cpu.log:
            f.write(f"{a:04X}\n")

if __name__ == "__main__":
    main()
