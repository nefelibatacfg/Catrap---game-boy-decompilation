; ============================================================
; RST vectors and interrupt vectors ($0000-$00FF)
; ============================================================

Rst_00:
	ld hl,h8C
	jp Func_01D0
	db $00 ; $0006
	db $00 ; $0007

Rst_08:
	nop
	nop

Func_000A:
	nop

Func_000B:
	nop

Func_000C:
	nop
	nop

Func_000E:
	nop
	nop

Rst_10:
	push bc
	push de
	push hl
	jp Func_0439
	db $00 ; $0016
	db $00 ; $0017

Rst_18:
	jp Func_0346
	db $00 ; $001B
	db $00 ; $001C
	db $00 ; $001D
	db $00 ; $001E
	db $00 ; $001F

Rst_20:
	jp Func_034C
	db $FF ; $0023
	db $FF ; $0024
	db $FF ; $0025
	db $FF ; $0026
	db $FF ; $0027

Rst_28:
	jp Func_0904
	db $FF ; $002B
	db $FF ; $002C
	db $FF ; $002D
	db $FF ; $002E
	db $FF ; $002F

Rst_30:
	push bc
	push de
	push hl

Func_0033:
	ld a,$01
	jp Func_0439

Rst_38:
	rst $38

Func_0039:
	rst $38
	rst $38

Func_003B:
	rst $38
	rst $38
	rst $38

Func_003E:
	rst $38

Func_003F:
	rst $38

VBlank_Handler:
	jp Func_01A5
	db $00 ; $0043
	db $00 ; $0044
	db $00 ; $0045
	db $00 ; $0046
	db $00 ; $0047

LCDC_Handler:
	reti
	db $00 ; $0049
	db $00 ; $004A
	db $00 ; $004B
	db $00 ; $004C
	db $00 ; $004D
	db $00 ; $004E
	db $00 ; $004F

Timer_Handler:
	reti
	db $00 ; $0051
	db $00 ; $0052
	db $00 ; $0053
	db $00 ; $0054
	db $00 ; $0055
	db $00 ; $0056
	db $00 ; $0057

Serial_Handler:
	reti
	db $00 ; $0059
	db $00 ; $005A
	db $00 ; $005B
	db $00 ; $005C
	db $00 ; $005D
	db $00 ; $005E
	db $00 ; $005F

Joypad_Handler:
	reti
	db $FB ; $0061
	db $C4 ; $0062
	db $FB ; $0063
	db $C6 ; $0064
	db $C0 ; $0065
	db $C2 ; $0066
	db $C8 ; $0067
	db $CA ; $0068
	db $CC ; $0069
	db $CE ; $006A
	db $D0 ; $006B
	db $D2 ; $006C
	db $FB ; $006D
	db $D6 ; $006E
	db $D8 ; $006F
	db $DA ; $0070
	db $FB ; $0071
	db $D4 ; $0072
	db $FB ; $0073
	db $FB ; $0074
	db $C0 ; $0075
	db $DC ; $0076
	db $DE ; $0077
	db $C1 ; $0078
	db $CC ; $0079
	db $CE ; $007A
	db $D0 ; $007B
	db $D2 ; $007C
	db $FB ; $007D
	db $D6 ; $007E
	db $D8 ; $007F
	db $DA ; $0080
	db $FB ; $0081
	db $FB ; $0082
	db $FB ; $0083
	db $FB ; $0084
	db $C0 ; $0085
	db $C3 ; $0086
	db $C5 ; $0087
	db $C7 ; $0088
	db $CC ; $0089
	db $CE ; $008A
	db $D0 ; $008B
	db $D2 ; $008C
	db $FB ; $008D
	db $D6 ; $008E
	db $D8 ; $008F
	db $DA ; $0090
	db $FB ; $0091
	db $C4 ; $0092
	db $FB ; $0093
	db $C6 ; $0094
	db $FB ; $0095
	db $C9 ; $0096
	db $D3 ; $0097
	db $D5 ; $0098
	db $CB ; $0099
	db $CD ; $009A
	db $CF ; $009B
	db $D1 ; $009C
	db $D7 ; $009D
	db $D9 ; $009E
	db $D8 ; $009F
	db $DB ; $00A0
	db $FB ; $00A1
	db $D4 ; $00A2
	db $FB ; $00A3
	db $FB ; $00A4
	db $FB ; $00A5
	db $C9 ; $00A6
	db $D3 ; $00A7
	db $DD ; $00A8
	db $CB ; $00A9
	db $CD ; $00AA
	db $CF ; $00AB
	db $D1 ; $00AC
	db $D7 ; $00AD
	db $D9 ; $00AE
	db $D8 ; $00AF
	db $DB ; $00B0
	db $FB ; $00B1
	db $FB ; $00B2
	db $FB ; $00B3
	db $FB ; $00B4
	db $FB ; $00B5
	db $DF ; $00B6
	db $E0 ; $00B7
	db $E1 ; $00B8
	db $CB ; $00B9
	db $CD ; $00BA
	db $CF ; $00BB
	db $D1 ; $00BC
	db $D7 ; $00BD
	db $D9 ; $00BE
	db $D8 ; $00BF
	db $DB ; $00C0
	db $00 ; $00C1
	db $00 ; $00C2
	db $00 ; $00C3
	db $00 ; $00C4
	db $00 ; $00C5
	db $00 ; $00C6
	db $00 ; $00C7
	db $00 ; $00C8
	db $00 ; $00C9
	db $00 ; $00CA
	db $00 ; $00CB
	db $00 ; $00CC
	db $00 ; $00CD
	db $00 ; $00CE
	db $00 ; $00CF
	db $00 ; $00D0
	db $00 ; $00D1
	db $00 ; $00D2
	db $00 ; $00D3
	db $00 ; $00D4
	db $00 ; $00D5
	db $00 ; $00D6
	db $00 ; $00D7
	db $00 ; $00D8
	db $00 ; $00D9
	db $00 ; $00DA
	db $00 ; $00DB
	db $00 ; $00DC
	db $00 ; $00DD
	db $00 ; $00DE
	db $00 ; $00DF
	db $FF ; $00E0
	db $FF ; $00E1
	db $FF ; $00E2
	db $FF ; $00E3
	db $FF ; $00E4
	db $FF ; $00E5
	db $FF ; $00E6
	db $FF ; $00E7
	db $FF ; $00E8
	db $FF ; $00E9
	db $FF ; $00EA
	db $FF ; $00EB
	db $FF ; $00EC
	db $FF ; $00ED
	db $FF ; $00EE
	db $FF ; $00EF
	db $FF ; $00F0
	db $FF ; $00F1
	db $FF ; $00F2
	db $FF ; $00F3
	db $FF ; $00F4
	db $FF ; $00F5
	db $FF ; $00F6
	db $FF ; $00F7
	db $FF ; $00F8
	db $FF ; $00F9
	db $FF ; $00FA
	db $FF ; $00FB
	db $FF ; $00FC
	db $FF ; $00FD
	db $FF ; $00FE
	db $FF ; $00FF

