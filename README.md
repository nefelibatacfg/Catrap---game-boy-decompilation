# Catrap (USA) — Game Boy Reverse Engineering Project

A byte-exact **disassembly** and **reverse-engineering** kit for *Catrap*
(USA) on the Game Boy (Kemco, 1990).

The repository contains:

- a **full SM83 disassembler** (`disasm.py`) that regenerates the entire
  RGBDS source tree from the original ROM in one pass;
- the **generated RGBDS assembly** (`main.asm` + `src/`) that rebuilds
  `Catrap (USA).gb` **byte-for-byte**;
- **faithful Python ports** of the game's major subsystems (gameplay
  engine, sound engine, music score decoder, screen draw loop, level
  decoder) written from the disassembly;
- reverse-engineering notes on the enemy AI and player state machine.

Since this is a decompilation, *Catrap* is a manual-puzzle platformer:
push blocks, climb ladders, and crush the cats that guard each level.

## Status

- **Build reproduces the original ROM.** `python build.py` assembles the
  checked-in source and compares the result to your own dump of
  `Catrap (USA).gb` — it prints `OK: byte-identical (32768 bytes)` on
  success (see [Build](#build)).
- The 32 KB ROM (ROM0 `$0000-$3FFF`, ROM1 `$4000-$7FFF`) is fully
  decoded and covered; the `src/data/` regions are the raw bytes in
  address order.
- Gameplay, sound, music-command, and draw-vector logic have line-by-line
  Python ports (below), with several verified byte-exact against emulator
  captures.

## Repository layout

| Path | Purpose |
|---|---|
| `disasm.py` | Full SM83 disassembler. Traverses code statically and merges **dynamic execution coverage** captured by `emu.py`, then emits the whole `main.asm`/`src/` tree. |
| `emu.py` | Minimal SM83 interpreter used to trace real code execution (executed-string jumps, task-scheduler `ret` dispatch) so the disassembler marks every reachable byte as code. Not cycle-accurate. |
| `main.asm` | Entry point: ROM sections, hardware/RAM includes, and the two code banks. Also documents the cooperative task-scheduler architecture. |
| `src/` | Generated RGBDS source: `vectors.asm`, `header.asm` (cart header), `code_lo.asm` / `code_hi.asm` (ROM0/ROM1 code + INCLUDEs), `ram.inc`, and `src/data/` (data regions, one file per contiguous run). |
| `src/data/data_4451.asm` | Monolithic ROM1 data region `$4451-$7FFF` (music data/tables, SFX, tile sets, tilemaps, script/level data). |
| `src/data/` (named files) | Standalone, hand-annotated views of the same regions: `music.asm`, `script.asm`, `sfx.asm`, `tiles_*.asm`, `map_*.asm`, `leveldata.asm`, `music_tbl.asm`. Not part of the build — reference material. |
| `build.py` | Invokes RGBDS (`rgbasm`/`rgblink`/`rgbfix`) to produce `catrap.gb` and verify byte-identical output. |
| `game.py` | Byte-exact port of the gameplay engine: map/player/entity/block state, flags, and the task logic (`TaskGame`, `TaskInput`, …). Models the game's observable state; VRAM/OAM drawing is stubbed. |
| `sound.py` | Byte-exact port of the sound engine (`$3F73-$443F`): the music/SFX sequencers and the channel step logic. Documents the music command language. |
| `music.py` | Walks the music command language and prints the score (note names + octaves) for any song/state. |
| `draw.py` | Port of the screen draw loop (`$241F`…): cell buffer → tilemap, including the tile-dispatch and wall/ladder table lookups. Verified 494/494 playfield cells match the emulator capture. |
| `levels.py` | Port of the level decoder (`$27F8-$2865`): 33 bytes per level, 11×8 grid of 3-bit cells. |
| `render_levels.py` | Renders all levels to PNG using the game's real tiles (needs Pillow). |
| `enemy_ai.txt`, `player_machine.txt` | Reverse-engineering notes for the entity/enemy AI and the player state machine. |

## Requirements

- **Python 3** with:
  - [Pillow](https://pypi.org/project/Pillow/) — only needed for
    `render_levels.py`.
- **[RGBDS](https://github.com/gbdev/rgbds)** — only needed for
  `build.py`. Put the binaries in `tools/` or on `PATH` (`build.py`
  auto-detects, including the `.exe` names on Windows).
- **Your own dump of the original game**, saved as `Catrap (USA).gb` in
  the repo root.

> The original ROM is copyrighted and is **not** committed, and the
> checked-in source will not build without it (the disassembler,
> emulator, and all Python ports read it directly). Provide your own
> dump. See [Legal](#legal).

## Build

```bash
python build.py
```

Produces `catrap.gb` and, when `Catrap (USA).gb` is present, verifies it
is byte-identical to the original.

## Re-generating the disassembly

```bash
python disasm.py
```

Re-emits `main.asm` and the entire `src/` tree from `Catrap (USA).gb`
(static traversal + `emu.py` dynamic coverage). Byte-exactness is
guaranteed by faithful re-emission: each emitted region re-emits exactly
the bytes it consumed, verified by the build's full-file compare.

## Rendering the levels

```bash
python render_levels.py              # contact sheet of all levels -> catrap_levels_rendered.png
python render_levels.py 3 4          # a single level      -> level_03.png
python render_levels.py 0 110        # any range
```

Uses the game's actual tile set and draws the tilemap exactly like the
game's draw routine.

## Decoding the music

```bash
python music.py                       # title theme (state 1)
python music.py 7 1                   # song 7, state 1
```

Prints note names + octaves using the decoded music command language from
`sound.py`.

## How the disassembly pipeline works

1. `emu.py` runs the game under input scripts and records every executed
   PC (including code reached through executed-string jumps and the task
   scheduler's `ret`-dispatch into task frames).
2. `disasm.py` decodes the ROM with a full SM83 opcode table, walks code
   statically, merges the dynamic trace into its code set, and labels
   entry points (functions, RST handlers, task entries, data regions).
3. Output is ordinary RGBDS source with the code and data INCLUDE'd in
   address order, so the build reproduces the ROM exactly.

## Ports & verification

Each Python port was transcribed directly from the labeled disassembly and
annotated with the original addresses/ROM offsets, so it can be checked
against the hardware at every step. Notable verifications recorded in the
source:

- `draw.py`: tilemap port matches the emulator byte-for-byte (494/494
  playfield cells; only leftover uninitialized RAM columns differ).
- `build.py`: output ROM byte-identical to the original dump.
- Walls/ladders are drawn from 7×7 pattern tables indexed by
  `7*cell + above`, discovered while porting `draw.py`.

## Legal

*Catrap* © 1990 Kemco (original Game Boy release). All assets and code
belong to their respective rights holders. This project is for
preservation, education, and interoperability research. It contains no
copyrighted ROM data; you must supply your own dump to build or run
anything.
