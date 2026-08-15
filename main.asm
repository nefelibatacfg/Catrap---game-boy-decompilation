; ============================================================
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
INCLUDE "hardware.inc"
INCLUDE "src/ram.inc"

SECTION "ROM0", ROM0[$0000]
INCLUDE "src/vectors.asm"
INCLUDE "src/header.asm"
INCLUDE "src/code_lo.asm"

SECTION "ROM1", ROMX[$4000]
INCLUDE "src/code_hi.asm"
