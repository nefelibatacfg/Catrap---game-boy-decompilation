; ============================================================
; Main code ($0150-$3FFF) - ROM0
; ============================================================

Func_0150:
	di
	xor a
	ldh [$FF02],a
	ldh [$FF07],a
	ldh [$FF0F],a
	ldh [$FFFF],a
	ld bc,Data_2000
	ld hl,wC000

Func_0160:
	xor a
	ld [hli],a
	dec bc
	ld a,c
	or b
	jr nz,Func_0160
	ld sp,wDE7F
	call Func_0237
	ld hl,h8B
	ld bc,$0075
	call Func_026D
	call Func_1D69
	ld a,$01
	ldh [$FFFF],a
	ldh [h91],a
	xor a
	ldh [h8F],a
	call Func_3F31
	ei
	ld a,$00
	call Func_0464

Func_018B:
	call Func_01F1
	call Func_041B
	call Func_4034
	call Func_3F73
	call Func_3FCE
	xor a
	ldh [h8F],a
	halt

Func_019E:
	ldh a,[h8F]
	or a
	jr z,Func_019E
	jr Func_018B

Func_01A5:
	push af
	push bc
	push de
	push hl
	call h80
	ldh a,[h8F]
	or a
	jr nz,Func_01C7
	ld hl,wD3F7
	jr Func_01BB

Func_01B6:
	ld d,a
	ld e,[hl]
	inc hl
	ld a,[hli]
	ld [de],a

Func_01BB:
	ld a,[hli]
	or a
	jr nz,Func_01B6
	ld de,wD3F7
	xor a
	ld [de],a
	call Func_2E2D

Func_01C7:
	ld a,$01
	ldh [h8F],a
	pop hl
	pop de
	pop bc
	pop af
	reti

Func_01D0:
	ldh a,[h8B]
	or a
	jr nz,Func_01DD
	ldh a,[h8A]
	or a
	jr z,Func_01ED
	cp [hl]
	jr z,Func_01E4

Func_01DD:
	ldh a,[h8A]
	ld [hli],a
	ld [hl],$18
	jr Func_01EA

Func_01E4:
	inc hl
	dec [hl]
	jr nz,Func_01ED
	ld [hl],$07

Func_01EA:
	ldh a,[h8A]
	db $26

Func_01ED: ; jump target inside previous instruction
	db $AF
	ldh [h8E],a
	ret

Func_01F1:
	di
	ld a,$20
	ldh [$FF00],a
	ldh a,[$FF00]
	ldh a,[$FF00]
	cpl
	and $0F
	swap a
	ld b,a

Func_0200:
	ld a,$10
	ldh [$FF00],a
	ldh a,[$FF00]
	ldh a,[$FF00]
	ldh a,[$FF00]
	ldh a,[$FF00]
	ldh a,[$FF00]
	ldh a,[$FF00]
	cpl
	and $0F
	or b
	ld c,a
	ldh a,[h8A]
	xor c
	and c
	ldh [h8B],a
	ld a,c
	ldh [h8A],a
	ei
	ld a,$30
	ldh [$FF00],a
	ldh a,[h8A]
	bit 0,a
	jr nz,Func_0236
	bit 3,a
	ret z
	ldh a,[h8B]
	bit 2,a
	ret z
	ld a,$10
	ldh [hA4],a
	ret

Func_0236:
	ret

Func_0237:
	ld c,$80
	ld b,$0A
	ld hl,Data_0245

Func_023E:
	ld a,[hli]
	ld [$ff00+c],a
	inc c
	dec b
	jr nz,Func_023E
	ret

; ---- data $0245-$024E ----
INCLUDE "src/data/data_0245.asm"

Func_024F:
	ldh a,[$FFFF]
	ldh [h90],a
	res 0,a
	ldh [$FFFF],a

Func_0257:
	ldh a,[$FF44]
	cp $91
	jr nz,Func_0257
	ldh a,[$FF40]
	and $7F
	ldh [$FF40],a
	ldh a,[h90]
	ldh [$FFFF],a
	ret

; ---- data $0268-$026C ----
INCLUDE "src/data/data_0268.asm"

Func_026D:
	xor a
	ld [hli],a
	dec bc
	ld a,c
	or b
	jr nz,Func_026D
	ret

; ---- data $0275-$0297 ----
INCLUDE "src/data/data_0275.asm"

Func_0298:
	ld a,c
	add a,a
	rl b
	add a,a
	rl b
	ld a,c
	and $3F
	ld c,a
	jr z,Func_02A8
	inc b
	jr Func_02AA

Func_02A8:
	ld c,$40

Func_02AA:
	push bc
	push de
	push hl
	rst $30
	pop hl
	pop de
	pop bc

Func_02B1:
	ld a,[hli]
	ld [de],a
	inc de
	dec c
	jr nz,Func_02B1
	ld c,$40
	dec b
	jr nz,Func_02AA
	ret

; ---- data $02BD-$02D6 ----
INCLUDE "src/data/data_02BD.asm"

Func_02D7:
	call Func_024F
	call Func_02F1

Func_02DD:
	ld a,$A0
	ld hl,wC000
	ld b,$28

Func_02E4:
	ld [hli],a
	inc hl
	inc hl
	inc hl
	dec b
	jr nz,Func_02E4
	ret

Func_02EC:
	ld hl,$9800
	jr Func_02F7

Func_02F1:
	call Func_02EC
	ld hl,$9C00

Func_02F7:
	ld b,$10

Func_02F9:
	ld a,$FB
	ld c,$40

Func_02FD:
	ld [hli],a
	dec c
	jr nz,Func_02FD
	dec b
	jr nz,Func_02F9
	ret

; ---- data $0305-$0345 ----
INCLUDE "src/data/data_0305.asm"

Func_0346:
	pop de
	call Func_0364
	push de
	ret

Func_034C:
	pop de
	call Func_035B
	call Func_0364
	push de
	ret

; ---- data $0355-$035A ----
INCLUDE "src/data/data_0355.asm"

Func_035B:
	ld a,[de]
	inc de
	ldh [h94],a
	ld a,[de]
	inc de
	ldh [h93],a
	ret

Func_0364:
	ld a,[de]
	inc de
	or a
	ret z
	call Func_036D
	jr Func_0364

Func_036D:
	cp $20
	jr nz,Func_0375
	ld c,$FB
	jr Func_037F

Func_0375:
	sub $30
	ld l,a
	ld h,$00
	ld bc,Data_03CA
	add hl,bc
	ld c,[hl]

Func_037F:
	call Func_0384
	jr Func_03B7

Func_0384:
	push de
	call Func_03A0
	jr Func_038B
	push de

Func_038B:
	call Func_2E26
	di
	ld a,h
	ld [de],a
	inc de
	ld a,l
	ld [de],a
	inc de
	ld a,c
	ld [de],a
	inc de
	xor a
	ld [de],a
	ei
	call Func_2E2D
	pop de
	ret

Func_03A0:
	push de
	ldh a,[h93]
	and $3F
	rlca
	rlca
	ld l,a
	ld h,$00
	add hl,hl
	add hl,hl
	add hl,hl
	ldh a,[h94]
	and $1F
	ld e,a
	ld d,$98
	add hl,de
	pop de
	ret

Func_03B7:
	ld bc,h94
	ld a,[bc]
	inc a
	ld [bc],a
	cp $20
	jr c,Func_03C9
	xor a
	ld [bc],a
	dec bc
	ld a,[bc]
	inc a
	and $3F
	ld [bc],a

Func_03C9:
	ret

; ---- data $03CA-$041A ----
INCLUDE "src/data/data_03CA.asm"

Func_041B:
	xor a

Func_041C:
	ld [wDE14],a
	ld l,a

Func_0420:
	ld h,$DE
	add a,a
	add a,$06
	ld e,a
	ld a,[hl]
	or a
	jr z,Func_0451
	dec a
	jr nz,Func_0450
	ld [wDE12],sp
	ld l,e
	ld a,[hli]
	ld h,[hl]
	ld l,a
	ld sp,hl
	pop hl
	pop de
	pop bc
	ret

Func_0439:
	push af
	ld a,[wDE14]
	ld e,a
	ld d,$DE
	pop af
	ld [de],a
	ld a,e
	add a,a
	add a,$06
	ld e,a
	ld hl,sp+0
	ld a,l
	ld [de],a
	inc de
	ld a,h
	ld [de],a
	jr Func_0451

Func_0450:
	ld [hl],a

Func_0451:
	ld a,[wDE12]
	ld l,a
	ld a,[wDE13]
	ld h,a
	ld sp,hl
	ld a,[wDE14]
	inc a
	cp $06
	jp nz,Func_041C
	ret

Func_0464:
	ld b,a
	ld l,a
	ld h,$DE
	ld [hl],$01
	add a,a
	ld c,a
	add a,$06
	ld l,a
	push hl
	ld hl,wDE7F
	ld de,VBlank_Handler
	inc b

Func_0477:
	add hl,de
	dec b
	jr nz,Func_0477
	push hl
	ld hl,Data_04A0
	ld b,$00
	add hl,bc
	ld e,[hl]
	inc hl
	ld d,[hl]
	pop hl
	ld [hl],d
	dec hl
	ld [hl],e
	ld de,hFA
	add hl,de
	ld d,h
	ld e,l
	pop hl
	ld [hl],e
	inc hl
	ld [hl],d
	ret

Func_0494:
	ld l,a
	ld h,$DE
	ld [hl],$01
	ret

; ---- data $049A-$04A7 ----
INCLUDE "src/data/data_049A.asm"

Func_04A8:
	rst $30
	call Func_02D7
	ld a,$C7
	ldh [$FF40],a
	di
	ld a,$40
	ldh [$FF41],a
	xor a
	ldh [$FF45],a
	ei
	ldh [$FF42],a
	ldh [$FF43],a
	call Func_167F
	call Func_16C1
	call Func_0C50
	ld a,$01
	ldh [hFB],a
	rst $30
	rst $20
	inc b
	dec c
	ld e,h
	ld sp,Data_3939
	jr nc,Func_04D4

Func_04D4:
	rst $30
	ld hl,$9989
	call Func_171B
	rst $30
	rst $20
	nop
	db $10, $4C ; stop (operand preserved)

; ---- data $04E0-$0903 ----
INCLUDE "src/data/data_04E0.asm"

Func_0904:
	rst $30
	ld hl,$FF4A
	ld a,[hl]
	add a,b
	ld [hl],a
	cp c
	jr nz,Func_0904
	ret

; ---- data $090F-$099B ----
INCLUDE "src/data/data_090F.asm"

Func_099C:
	ldh a,[hD7]
	ldh [hC2],a
	ld c,a
	ld a,[wDA5F]
	call Func_09F5
	ld a,l
	ldh [hBF],a
	ld a,h
	ldh [hC0],a
	ldh a,[hD8]
	ldh [hC1],a
	ld c,a
	ld a,[wDA60]
	call Func_09F5
	ld a,l
	ldh [hBD],a
	ld a,h
	ldh [hBE],a
	ld hl,wDA7B
	call Func_0A15
	ld a,$FF
	ld [wDA9B],a
	ld [wDABB],a
	call Func_0AC8
	ld b,$06
	call Func_0A3A
	ld hl,wDA9B
	call Func_0A15
	ld b,$06
	call Func_0A3A
	ld hl,wDABB
	call Func_0A15
	ld b,$06
	call Func_0A3A
	ld hl,wDA7B
	call Func_0A15
	ld b,$0E
	jp Func_0A3A

Func_09F5:
	sub c
	ld l,a
	ld h,$00
	jr nc,Func_09FC
	dec h

Func_09FC:
	ld e,l
	ld d,h
	add hl,hl
	add hl,hl
	add hl,de
	add hl,hl
	add hl,hl
	add hl,de
	add hl,hl
	add hl,hl
	add hl,de
	add hl,hl
	sra h
	rr l
	sra h
	rr l
	sra h
	rr l
	ret

Func_0A15:
	ld b,$00
	ld c,$2C
	ldh a,[hC2]
	ld d,a
	ldh a,[hC1]
	ld e,a
	xor a
	ld [hl],b
	inc hl
	ld [hl],$FF
	inc hl
	ld [hl],c
	inc hl
	inc hl
	ld [hl],d
	inc hl
	ld [hl],e
	inc hl
	ld bc,$0016
	add hl,bc
	ld [hli],a
	ld [hl],$80
	inc hl
	ld [hl],$80
	inc hl
	ld [hl],$0C
	ret

Func_0A3A:
	push bc
	call Func_1D69
	call Func_0ADC
	ld b,$03
	ld hl,wDA7B

Func_0A46:
	push bc
	call Func_0A74
	ld bc,Rst_20
	add hl,bc
	pop bc
	dec b
	jr nz,Func_0A46
	rst $30
	call Func_1D69
	call Func_0ADC
	ld b,$03
	ld hl,wDA7B

Func_0A5E:
	push bc
	push hl
	ld a,$00
	call Func_2E37
	ld bc,Rst_20
	pop hl
	add hl,bc
	pop bc
	dec b
	jr nz,Func_0A5E
	rst $30
	pop bc
	dec b
	jr nz,Func_0A3A
	ret

Func_0A74:
	ld a,[hl]
	inc a
	ret z
	push hl
	ld bc,$0004
	add hl,bc
	ld e,l
	ld d,h
	ld bc,Rst_18
	add hl,bc
	ld a,[hli]
	or a
	push af
	jr nz,Func_0A8F
	ldh a,[hBF]
	ld c,a
	ldh a,[hC0]
	ld b,a
	jr Func_0A98

Func_0A8F:
	ldh a,[hBF]
	cpl
	ld c,a
	ldh a,[hC0]
	cpl
	ld b,a
	inc bc

Func_0A98:
	ld a,c
	add a,[hl]
	ld [hli],a
	ld a,[de]
	adc a,b
	ld [de],a
	inc de
	pop af
	jr nz,Func_0AAA
	ldh a,[hBD]
	ld c,a
	ldh a,[hBE]
	ld b,a
	jr Func_0AB3

Func_0AAA:
	ldh a,[hBD]
	cpl
	ld c,a
	ldh a,[hBE]
	cpl
	ld b,a
	inc bc

Func_0AB3:
	ld a,c
	add a,[hl]
	ld [hli],a
	ld a,[de]
	adc a,b
	ld [de],a
	dec [hl]
	jr nz,Func_0AC0
	pop hl
	ld [hl],$FF
	ret

Func_0AC0:
	pop hl
	push hl
	xor a
	call Func_2E37
	pop hl
	ret

Func_0AC8:
	xor a
	ldh [hEF],a
	ld a,$17
	ld [wDA77],a
	ld a,[Data_0B2C]
	ldh [hEE],a
	ld a,[Data_0B43]
	ld [wDA76],a
	ret

Func_0ADC:
	ld de,hEE
	ld hl,hD3
	call Func_0AEB
	ld de,wDA76
	ld hl,wDA5B

Func_0AEB:
	ld a,[de]
	push af
	push de
	push hl
	bit 7,a
	ld a,$00
	call z,Func_2E37
	pop hl
	pop de
	pop af
	dec a
	ld [de],a
	and $3F
	ret nz
	inc de
	ld a,[de]
	inc a
	ld [de],a
	push de
	push hl
	ld hl,Data_0B2C
	ld e,a
	ld d,$00
	add hl,de
	ld a,[hl]
	pop hl
	pop de
	dec de
	ld [de],a
	bit 6,a
	ret z
	ld hl,hD3
	ld de,wDA5B
	ld b,$06

Func_0B1B:
	ld a,[de]
	ld c,[hl]
	ld [hli],a
	ld a,c
	ld [de],a
	inc de
	dec b
	jr nz,Func_0B1B
	ld a,$FF
	ld [wDA5E],a
	ldh [hD6],a
	ret

; ---- data $0B2C-$0C4F ----
INCLUDE "src/data/data_0B2C.asm"

Func_0C50:
	ld a,$E4
	jr Func_0C55
	xor a

Func_0C55:
	ldh [$FF47],a
	ldh [$FF48],a
	ldh [$FF49],a
	ret

; ---- data $0C5C-$167E ----
INCLUDE "src/data/data_0C5C.asm"

Func_167F:
	ld de,Data_5EA2
	ld hl,wC2A2
	ld c,$2D

Func_1687:
	ld b,$08

Func_1689:
	ld a,[de]
	inc de
	ld [hli],a
	ld [hli],a
	dec b
	jr nz,Func_1689
	dec c
	jr nz,Func_1687
	ld hl,wC2A2
	ld de,$9460
	ld bc,Data_02D0
	call Func_0298
	ret

; ---- data $16A0-$16C0 ----
INCLUDE "src/data/data_16A0.asm"

Func_16C1:
	ld hl,Data_778A
	ld de,$8800
	ld bc,Func_0420
	call Func_0298
	ld de,Data_7BAA
	ld hl,wC7F7
	ld c,$78

Func_16D5:
	ld b,$08

Func_16D7:
	ld a,[de]
	inc de
	ld [hli],a
	ld [hli],a
	dec b
	jr nz,Func_16D7
	dec c
	jr nz,Func_16D5
	ld hl,wC7F7
	ld de,$8CF0
	ld bc,EntryPoint
	call Func_0298
	ld hl,wC2A2
	push hl
	ld de,Data_174A
	ld c,$06

Func_16F6:
	ld a,$FB
	ld [hli],a
	ld [hli],a
	ld b,$12

Func_16FC:
	ld a,[de]
	inc de
	or $80
	ld [hli],a
	dec b
	jr nz,Func_16FC
	ld a,$FB
	ld [hli],a
	ld [hli],a
	push bc
	ld bc,Func_000A
	add hl,bc
	pop bc
	dec c
	jr nz,Func_16F6
	pop hl
	ld de,$9820
	ld bc,$00C0
	jp Func_0298

Func_171B:
	rst $30
	ld de,Data_1735
	ld c,$03

Func_1721:
	ld b,$07

Func_1723:
	ld a,[de]
	inc de
	or $80
	ld [hli],a
	dec b
	jr nz,Func_1723
	push bc
	ld bc,$0019
	add hl,bc
	pop bc
	dec c
	jr nz,Func_1721
	ret

; ---- data $1735-$1D68 ----
INCLUDE "src/data/data_1735.asm"

Func_1D69:
	call Func_02DD
	ld de,wC000
	jp Func_2F7D

; ---- data $1D72-$2482 ----
INCLUDE "src/data/data_1D72.asm"

Func_2483:
	cp $01
	jp c,Func_24BE
	jr z,Func_24A1
	cp $03
	jp c,Func_26B9
	ld a,[hl]
	and $07
	ld d,a
	push hl
	ld a,l
	add a,$10
	ld l,a
	ld a,[hl]
	and $07
	ld e,a
	ld bc,Data_3E7B
	jr Func_24B1

Func_24A1:
	ld a,[hl]
	and $07
	ld d,a
	push hl
	ld a,l
	sub $10
	ld l,a
	ld a,[hl]
	and $07
	ld e,a
	ld bc,Data_3E4A

Func_24B1:
	ld a,d
	add a,a
	add a,d
	add a,a
	add a,d
	add a,e
	ld l,a
	ld h,$00
	add hl,bc
	ld a,[hl]
	pop hl
	ret

Func_24BE:
	push hl
	ld a,l
	sub $11
	ld l,a
	ld a,[hli]
	and $07
	ld b,a
	ld a,[hl]
	and $07
	ld c,a
	pop hl
	ld a,[hl]
	and $07
	cp $01
	jr c,Func_24E8
	jr z,Func_2509
	cp $03
	jp c,Func_253A
	jp z,Func_259C
	cp $05
	jp c,Func_25A4
	jp z,Func_2618
	jp Func_256B

Func_24E8:
	dec hl
	ld a,[hli]
	and $07
	cp $04
	jr z,Func_24FD
	cp $05
	jr z,Func_2502
	ld a,c
	cp $03
	ld a,$FB
	ret nz
	ld a,$0B
	ret

Func_24FD:
	ld de,Data_3EAC
	jr Func_2505

Func_2502:
	ld de,Data_3EB3

Func_2505:
	ld a,b
	jp Func_26B1

Func_2509:
	ld a,c
	cp $01
	jr z,Func_251E
	cp $02
	jr z,Func_2526
	cp $03
	jr z,Func_2526
	ld c,$1C
	ld de,Data_3EBA
	jp Func_26A2

Func_251E:
	ld c,$29
	ld de,Data_3EC1
	jp Func_26A2

Func_2526:
	dec hl
	ld a,[hli]
	and $07
	call Func_27E5
	ld a,$3D
	ret nz
	ld a,b
	call Func_27E5
	ld a,$3E
	ret nz
	ld a,$21
	ret

Func_253A:
	ld a,c
	cp $02
	jr z,Func_2557
	cp $03
	jr z,Func_2557
	dec hl
	ld a,[hli]
	and $07
	call Func_27E5
	ld a,$F4
	ret nz
	ld a,b
	call Func_27E5
	ld a,$EA
	ret nz
	ld a,$E8
	ret

Func_2557:
	dec hl
	ld a,[hli]
	and $07
	call Func_27E5
	ld a,$EC
	ret nz
	ld a,b
	call Func_27E5
	ld a,$E2
	ret nz
	ld a,$E3
	ret

Func_256B:
	ld a,c
	cp $02
	jr z,Func_2588
	cp $03
	jr z,Func_2588
	dec hl
	ld a,[hli]
	and $07
	call Func_27E5
	ld a,$D8
	ret nz
	ld a,b
	call Func_27E5
	ld a,$CE
	ret nz
	ld a,$CC
	ret

Func_2588:
	dec hl
	ld a,[hli]
	and $07
	call Func_27E5
	ld a,$D0
	ret nz
	ld a,b
	call Func_27E5
	ld a,$C6
	ret nz
	ld a,$C7
	ret

Func_259C:
	ld c,$FC
	ld de,Data_3EC8
	jp Func_26A2

Func_25A4:
	ld a,c
	cp $02
	jr c,Func_25B7
	jr z,Func_25D4
	cp $04
	jr c,Func_25D4
	jp z,Func_25F3
	cp $05
	jp z,Func_25F3

Func_25B7:
	dec hl
	ld a,[hli]
	and $07
	cp $04
	jr z,Func_25C6
	cp $05
	jr z,Func_25CD
	ld a,$06
	ret

Func_25C6:
	ld a,b
	ld de,Data_3ECF
	jp Func_26B1

Func_25CD:
	ld a,b
	ld de,Data_3EE4
	jp Func_26B1

Func_25D4:
	ld a,b
	call Func_27E5
	jr z,Func_25E6
	dec hl
	ld a,[hli]
	and $07
	cp $04
	ld a,$3C
	ret z
	ld a,$35
	ret

Func_25E6:
	dec hl
	ld a,[hli]
	and $07
	call Func_27E5
	ld a,$35
	ret nz
	ld a,$38
	ret

Func_25F3:
	dec hl
	ld a,[hli]
	and $07
	ld c,a
	ld a,b
	cp $04
	jr z,Func_260A
	cp $05
	jr z,Func_2611
	ld a,c
	cp $04
	ld a,$07
	ret nz
	ld a,$10
	ret

Func_260A:
	ld a,c
	ld de,Data_3ED6
	jp Func_26B1

Func_2611:
	ld a,c
	ld de,Data_3EDD
	jp Func_26B1

Func_2618:
	ld a,c
	cp $02
	jr c,Func_2633
	jp z,Func_2650
	cp $04
	jr c,Func_2650
	jp z,Func_266F
	cp $05
	jp z,Func_2690
	cp $06
	jr z,Func_2633
	jp Func_2745

Func_2633:
	dec hl
	ld a,[hli]
	and $07
	cp $04
	jr z,Func_2642
	cp $05
	jr z,Func_2649
	ld a,$00
	ret

Func_2642:
	ld a,b
	ld de,Data_3EEB
	jp Func_26B1

Func_2649:
	ld a,b
	ld de,Data_3EF2
	jp Func_26B1

Func_2650:
	ld a,b
	call Func_27E5
	jr z,Func_2662
	dec hl
	ld a,[hli]
	and $07
	cp $05
	ld a,$34
	ret nz
	ld a,$2A
	ret

Func_2662:
	dec hl
	ld a,[hli]
	and $07
	call Func_27E5
	ld a,$34
	ret nz
	ld a,$33
	ret

Func_266F:
	dec hl
	ld a,[hli]
	and $07
	cp $04
	jr z,Func_267E
	cp $05
	jr z,Func_2687
	ld a,$18
	ret

Func_267E:
	ld a,b
	cp $04
	ld a,$18
	ret nz
	ld a,$1A
	ret

Func_2687:
	ld a,b
	cp $04
	ld a,$18
	ret nz
	ld a,$1A
	ret

Func_2690:
	dec hl
	ld a,[hli]
	and $07
	cp $05
	ld a,$01
	ret nz
	ld a,b
	cp $05
	ld a,$03
	ret z
	ld a,$0C
	ret

Func_26A2:
	dec hl
	ld a,[hli]
	and $07
	cp $04
	jr z,Func_26B0
	cp $05
	jr z,Func_26B0
	ld a,c
	ret

Func_26B0:
	ld a,b

Func_26B1:
	push hl
	ld l,a
	ld h,$00
	add hl,de
	ld a,[hl]
	pop hl
	ret

Func_26B9:
	push hl
	ld a,l
	add a,$0F
	ld l,a
	ld a,[hli]
	and $07
	ld b,a
	ld a,[hli]
	and $07
	ld c,a
	pop hl
	ld a,[hl]
	and $07
	cp $01
	jr c,Func_26E3
	jr z,Func_2703
	cp $03
	jp c,Func_271A
	jp z,Func_2742
	cp $05
	jp c,Func_2748
	jp z,Func_2796
	jp Func_272E

Func_26E3:
	dec hl
	ld a,[hli]
	and $07
	cp $04
	jr z,Func_26F2
	cp $05
	jr z,Func_26FC
	ld a,$FB
	ret

Func_26F2:
	ld a,b
	call Func_27E5
	ld a,$24
	ret nz
	ld a,$05
	ret

Func_26FC:
	ld a,b
	ld de,Data_3EF9
	jp Func_26B1

Func_2703:
	dec hl
	ld a,[hli]
	and $07
	call Func_27E5
	jr z,Func_2713
	ld a,$1D
	dec c
	ret nz
	ld a,$29
	ret

Func_2713:
	ld a,$30
	dec c
	ret nz
	ld a,$2F
	ret

Func_271A:
	dec hl
	ld a,[hli]
	and $07
	call Func_27E5
	ld a,$F5
	ret nz
	ld a,b
	call Func_27E5
	ld a,$E9
	ret nz
	ld a,$EB
	ret

Func_272E:
	dec hl
	ld a,[hli]
	and $07
	call Func_27E5
	ld a,$D9
	ret nz
	ld a,b
	call Func_27E5
	ld a,$CD
	ret nz
	ld a,$CF
	ret

Func_2742:
	ld a,$FD
	ret

Func_2745:
	ld a,$FB
	ret

Func_2748:
	dec hl
	ld a,[hli]
	and $07
	cp $04
	jr z,Func_275B
	cp $05
	jr z,Func_2772
	ld a,c
	ld de,Data_3F00
	jp Func_26B1

Func_275B:
	ld a,b
	call Func_27E5
	jr z,Func_2768
	ld a,c
	ld de,Data_3F07
	jp Func_26B1

Func_2768:
	ld a,c
	call Func_27E5
	ld a,$09
	ret z
	ld a,$13
	ret

Func_2772:
	ld a,b
	cp $04
	jr z,Func_2782
	cp $05
	jr z,Func_278C
	ld a,c
	ld de,Data_3F0E
	jp Func_26B1

Func_2782:
	ld a,c
	call Func_27E5
	ld a,$27
	ret z
	ld a,$13
	ret

Func_278C:
	ld a,c
	call Func_27E5
	ld a,$07
	ret z
	ld a,$13
	ret

Func_2796:
	dec hl
	ld a,[hli]
	and $07
	cp $04
	jr z,Func_27A9
	cp $05
	jr z,Func_27C3
	ld a,c
	ld de,Data_3F15
	jp Func_26B1

Func_27A9:
	ld a,c
	cp $04
	jr z,Func_27B9
	cp $05
	jr z,Func_27C0
	ld a,b
	ld de,Data_3F1C
	jp Func_26B1

Func_27B9:
	ld a,b
	ld de,Data_3F23
	jp Func_26B1

Func_27C0:
	ld a,$01
	ret

Func_27C3:
	ld a,c
	cp $04
	jr z,Func_27D3
	cp $05
	jr z,Func_27DC
	ld a,b
	ld de,Data_3F2A
	jp Func_26B1

Func_27D3:
	ld a,b
	cp $04
	ld a,$3B
	ret nz
	ld a,$1B
	ret

Func_27DC:
	ld a,b
	cp $05
	ld a,$0D
	ret nz
	ld a,$03
	ret

Func_27E5:
	cp $04
	ret z
	cp $05
	ret
	dec hl
	ld a,[hli]
	and $07
	cp $04
	ret z
	cp $05
	ret

; ---- data $27F5-$2875 ----
INCLUDE "src/data/data_27F5.asm"

Func_2876:
	ld a,$FF
	ldh [hD3],a
	ldh [hD4],a
	ld [wDA5B],a
	ld [wDA5C],a
	xor a
	ldh [hD5],a
	ldh [hE3],a
	ldh [hA1],a
	ld b,$D0
	ld de,$FFFF
	ld hl,wC100

Func_2891:
	ld a,[hli]
	cp $10
	jr nz,Func_28A1
	dec hl
	ld a,d
	inc a
	jr nz,Func_289F
	ld d,l
	inc hl
	jr Func_28A1

Func_289F:
	ld e,l
	inc hl

Func_28A1:
	dec b
	jr nz,Func_2891
	ldh a,[hCC]
	ldh [hD3],a
	ld a,e
	inc a
	jr z,Func_28AF
	ld a,d
	ld d,e
	ld e,a

Func_28AF:
	ld a,d
	and $0F
	swap a
	ldh [hD8],a
	ld a,d
	and $F0
	ldh [hD7],a
	ld a,e
	inc a
	jr z,Func_28D8
	ldh a,[hCC]
	xor $01
	ld [wDA5B],a
	ld a,e
	and $0F
	swap a
	ld [wDA60],a
	ld a,e
	and $F0
	ld [wDA5F],a
	xor a
	ld [wDA5D],a

Func_28D8:
	rst $30
	call Func_2948
	call Func_2C06
	rst $30
	call Func_293A
	ldh [hB7],a
	ldh [hB8],a
	ld [wC7F7],a

Func_28EA:
	call Func_293A
	ldh a,[hD5]
	and $FE
	and $0E
	jp z,Func_2928
	ldh a,[hE1]
	or a
	jr z,Func_28EA
	ldh a,[hD5]
	ld c,a
	and $0E
	cp $06
	jr z,Func_2914
	cp $08
	jr z,Func_2919
	ld de,hF0
	bit 0,c
	jr z,Func_291C
	ld de,Rst_10
	jr Func_291C

Func_2914:
	ld de,$F000
	jr Func_291C

Func_2919:
	ld de,Data_1000

Func_291C:
	call Func_2E1B
	call Func_2B82

Func_2922:
	call Func_2948
	call Func_2C06

Func_2928:
	ldh a,[hA1]
	or a
	call nz,Func_293A
	call Func_2965
	ld hl,wDA5D
	call Func_376F
	jp Func_28EA

Func_293A:
	ld b,$01
	call Func_2D98
	ldh a,[hA1]
	or a
	ret z
	call Func_2C06
	jr Func_293A

Func_2948:
	call Func_2D88
	or a
	ret nz
	call Func_2D7C
	ld a,[de]
	and $07
	ret nz
	ld [de],a
	ld b,$04
	call Func_2BFD
	call Func_2BA8
	call Func_2D7C
	call Func_29C2
	scf
	ret

Func_2965:
	xor a
	ldh [hE3],a
	call Func_2E14
	ldh a,[h8A]
	bit 5,a
	jr nz,Func_2985
	bit 4,a
	jr nz,Func_298B
	bit 7,a
	jp nz,Func_2B4D
	bit 6,a
	jp nz,Func_2B32
	ldh a,[hD5]
	ld c,a
	jp Func_2B82

Func_2985:
	ld a,$F0
	ld c,$02
	jr Func_298F

Func_298B:
	ld a,$10
	ld c,$03

Func_298F:
	add a,l
	ld l,a
	call Func_2D8F
	cp $01
	jr c,Func_29B2
	jp z,Func_2B20
	cp $03
	jp c,Func_2AA1
	jp z,Func_2A3D
	cp $05
	jr c,Func_29C6
	jp z,Func_2B82
	cp $07
	jp c,Func_2AA1
	jp Func_2B82

Func_29B2:
	call Func_2D72
	dec a
	jr nz,Func_29BE
	ld a,c
	and $01
	or $0E
	ld c,a

Func_29BE:
	call Func_2D5B
	ld a,[de]

Func_29C2:
	or $10
	ld [de],a
	ret

Func_29C6:
	call Func_2D72
	dec a
	jr nz,Func_29D3
	ld a,c
	and $01
	or $2A
	jr Func_29D8

Func_29D3:
	ld a,c
	and $01
	or $1A

Func_29D8:
	ld c,a
	call Func_2D5B
	ld a,$10
	ld [de],a

Func_29DF:
	ld a,l
	ldh [hE4],a
	ld a,h
	ldh [hE5],a
	ld a,c
	and $01
	or $80
	ldh [hE3],a
	xor $81
	ld c,a
	push hl
	push hl
	call Func_2CF5
	ld b,$02
	call Func_2D98
	ld a,$06
	ldh [hFD],a
	call Func_2CC8
	pop de
	ld [hl],$04
	inc hl
	ld [hl],$00
	inc hl
	ldh a,[hD5]
	and $01
	xor $01
	or $0C
	ld [hli],a
	inc hl
	ld [hl],d
	inc hl
	ld [hl],e
	ld b,$0A
	call Func_2D98
	ldh a,[hE3]
	and $01
	ld c,a
	ldh a,[hE4]
	ld l,a
	ldh a,[hE5]
	ld h,a
	call Func_2CF5
	call Func_2CC8
	pop de
	ld [hl],$04
	inc hl
	ld [hl],$00
	inc hl
	ldh a,[hD5]
	and $01
	or $0C
	ld [hli],a
	inc hl
	ld [hl],d
	inc hl
	ld [hl],e
	ret

Func_2A3D:
	call Func_2D72
	dec a
	jr nz,Func_2A4A
	ld a,c
	and $01
	or $1E
	jr Func_2A4F

Func_2A4A:
	ld a,c
	and $01
	or $1C

Func_2A4F:
	ldh [hD5],a
	push de
	inc de
	bit 0,c
	jr nz,Func_2A59
	dec de
	dec de

Func_2A59:
	pop bc
	ld a,[de]
	or a
	jp nz,Func_2B7F
	ld [bc],a
	push de
	ld a,$03
	ld [de],a
	push hl
	call Func_2CDD
	pop hl
	call Func_2C99
	pop bc
	ld b,$13
	ldh a,[hD5]
	and $01
	call Func_2DBE

Func_2A76:
	ld b,$01
	call Func_2D98
	ldh a,[hA1]
	or a
	jr nz,Func_2A76

Func_2A80:
	ld b,$01
	call Func_2D98
	call Func_2C06
	ldh a,[hA1]
	or a
	jr nz,Func_2A80
	ld de,hD5
	ld b,$00
	ld a,[de]
	and $FE
	cp $1E
	jr nz,Func_2A9B
	ld b,$10

Func_2A9B:
	ld a,[de]
	and $01
	or b
	ld [de],a
	ret

Func_2AA1:
	or $20
	ldh [h9D],a
	push bc
	push hl
	xor a
	ld [de],a
	call Func_2D72
	dec a
	jr nz,Func_2AB5
	ld a,c
	and $01
	or $28
	ld c,a

Func_2AB5:
	ld a,c
	or $20
	ld c,a
	call Func_2D5B
	xor a
	call Func_29C2

Func_2AC0:
	ld b,$01
	call Func_2DA2
	ldh a,[hDB]
	cp $04
	jr nz,Func_2ACF
	ld a,$02
	ldh [hFD],a

Func_2ACF:
	ldh a,[hE1]
	or a
	jr z,Func_2AC0
	pop hl
	push hl
	ld a,l
	ldh [hD8],a
	call Func_2BFB
	pop hl
	pop bc
	push bc
	push hl
	call Func_2CDD
	call Func_2CC8
	pop de
	pop bc
	push bc
	push de
	ldh a,[h9D]
	and $0F
	ld [hl],a
	inc hl
	ld [hl],$00
	inc hl
	ld a,c
	and $01
	or $04
	ld [hl],a
	inc hl
	inc hl
	ld [hl],d
	inc hl
	ld [hl],e
	ld bc,Rst_18
	add hl,bc
	ld [hl],$00
	inc hl
	ld [hl],d
	inc hl
	ld [hl],$00
	pop hl
	pop bc
	ld a,e
	swap a
	or d
	push af
	pop af
	ld b,a
	ld a,c
	ld c,b
	push af
	ldh a,[h9D]
	ld b,a
	pop af
	call Func_2DBE
	pop af
	jp Func_2922

Func_2B20:
	ld b,$0A
	call Func_2D72
	dec a
	jr nz,Func_2B2A
	ld b,$12

Func_2B2A:
	ld a,c
	and $01
	or b
	ld c,a
	jp Func_29BE

Func_2B32:
	ld a,h
	cp $10
	jr z,Func_2B7F
	call Func_2D81
	cp $02
	jr nc,Func_2B7F
	ld b,$06
	dec a
	jr z,Func_2B45
	ld b,$16

Func_2B45:
	call Func_2D72
	dec a
	jr nz,Func_2B7F
	jr Func_2B66

Func_2B4D:
	call Func_2D72
	dec a
	jr z,Func_2B5D
	ld b,$18
	call Func_2D88
	dec a
	jr z,Func_2B66
	jr Func_2B7F

Func_2B5D:
	ld b,$08
	call Func_2D88
	cp $02
	jr nc,Func_2B7F

Func_2B66:
	ld a,c
	and $01
	or b
	ldh [hD5],a
	push de
	call Func_2DC7
	pop de
	push de
	call Func_2D7C
	pop hl
	ld a,[de]
	and $07
	ld [de],a
	ld a,[hl]
	or $10
	ld [hl],a
	ret

Func_2B7F:
	ldh a,[hD5]
	ld c,a

Func_2B82:
	call Func_2D72
	dec a
	jr z,Func_2BA0
	call Func_2D81
	and $07
	dec a
	dec a
	dec a
	jr nz,Func_2B9A
	ld a,c
	and $01
	or $20
	ldh [hD5],a
	ret

Func_2B9A:
	ld a,c
	and $01
	ldh [hD5],a
	ret

Func_2BA0:
	ld a,c
	and $01
	or $10
	ldh [hD5],a
	ret

Func_2BA8:
	call Func_2D7C
	ld b,$07
	ld c,e
	ldh a,[hD5]
	and $01
	or $04
	call Func_2DBE
	jr Func_2BBF

Func_2BB9:
	ld b,$01
	call Func_2D98
	rst $30

Func_2BBF:
	call Func_2DAC
	ldh a,[h8A]
	ld c,a
	ldh a,[hD5]
	bit 5,c
	jr nz,Func_2BD3
	bit 4,c
	jr z,Func_2BD7
	or $01
	jr Func_2BD5

Func_2BD3:
	and $FE

Func_2BD5:
	ldh [hD5],a

Func_2BD7:
	ld de,Func_0200
	call Func_2E1B
	ld a,h
	and $0F
	jr nz,Func_2BB9
	call Func_2D8B
	or a
	jr z,Func_2BB9
	ld a,$01
	ldh [hFD],a
	ld b,$14
	call Func_2BFD

Func_2BF1:
	ld b,$01
	call Func_2D98
	ldh a,[hE1]
	or a
	jr z,Func_2BF1

Func_2BFB:
	ld b,$00

Func_2BFD:
	ld de,hD5
	ld a,[de]
	and $01
	or b
	ld [de],a
	ret

Func_2C06:
	ld b,$80
	ld hl,wC17F

Func_2C0B:
	ld a,[hl]
	cp $02
	jr z,Func_2C54
	cp $03
	jr z,Func_2C54
	cp $10
	jr nz,Func_2C93
	ld c,a
	ld a,l
	and $F0
	ld d,a
	ldh a,[hD7]
	cp d
	jr nz,Func_2C2D
	ld a,l
	and $0F
	swap a
	ld d,a
	ldh a,[hD8]
	cp d
	jr z,Func_2C93

Func_2C2D:
	push hl
	ld a,l
	add a,$10
	ld l,a
	ld a,[hl]
	pop hl
	or a
	jr nz,Func_2C93
	ld [hl],$00
	ld a,[wDA5D]
	and $01
	or $04
	ld [wDA5D],a
	ld a,$01
	ldh [hA1],a
	push bc
	push hl
	ld c,l
	ld b,$07
	ld a,$40
	call Func_2DBE
	pop hl
	pop bc
	ret

Func_2C54:
	ld c,a
	push hl
	ld a,l
	add a,$10
	ld l,a
	ld a,[hl]
	pop hl
	or a
	jr nz,Func_2C93
	push bc
	push hl
	call Func_2CC8
	pop hl
	pop bc
	jr c,Func_2C8E
	push bc
	push hl
	push bc
	ld [hl],$00
	ld a,l
	and $F0
	ld h,a
	ld a,l
	and $0F
	swap a
	ld l,a
	call Func_2CDD
	ld a,$01
	pop bc
	push bc
	ld b,c
	call Func_2CA1
	pop bc
	pop hl
	push hl
	ld b,c
	ld a,l
	ld c,$00
	call Func_2DBE
	pop hl
	pop bc

Func_2C8E:
	ld a,$01
	ldh [hA1],a
	ret

Func_2C93:
	dec hl
	dec b
	jp nz,Func_2C0B
	ret

Func_2C99:
	ld b,$03
	ldh a,[hD5]
	and $01
	or $02

Func_2CA1:
	push hl
	push af
	push bc
	call Func_2CC8
	pop bc
	pop af
	ld [hl],b
	inc hl
	ld [hl],$00
	inc hl
	ld [hli],a
	inc hl
	pop de
	ld [hl],d
	inc hl
	ld [hl],e
	ld de,$0016
	add hl,de
	push de
	call Func_2DFF
	ld a,e
	ld [hli],a
	ld a,d
	ld [hl],a
	dec hl
	dec hl
	ld [hl],$0B
	inc hl
	inc hl
	pop de
	ret

Func_2CC8:
	push de
	ld d,$0A
	ld hl,wDABD
	ld bc,Rst_20
	xor a

Func_2CD2:
	dec d
	add hl,bc
	cp [hl]
	jr nz,Func_2CD2
	ld a,d
	cp $80
	ccf
	pop de
	ret

Func_2CDD:
	push hl
	call Func_2D8F
	ld l,e
	ld h,d
	ld bc,Func_0200

Func_2CE6:
	push hl
	ld a,c
	call Func_2D20
	call Func_2D15
	pop hl
	inc c
	dec b
	jr nz,Func_2CE6
	pop hl
	ret

Func_2CF5:
	ld a,l
	swap a
	or h
	sub $10
	ld l,a
	ld h,$C1
	bit 0,c
	jr z,Func_2D0A
	push hl
	ld c,$01
	call Func_2D0C
	pop hl
	inc l

Func_2D0A:
	ld c,$00

Func_2D0C:
	ld b,$02

Func_2D0E:
	call Func_2D15
	dec b
	jr nz,Func_2D0E
	ret

Func_2D15:
	ld a,c
	or $02
	call Func_2D20
	ld a,l
	add a,$10
	ld l,a
	ld a,c

Func_2D20:
	push bc
	ld [wC6A1],a
	call Func_2483

Func_2D27:
	push af
	push hl
	ld a,l
	and $F0
	ld c,a
	ld b,$00
	ld h,b
	add hl,bc
	add hl,hl
	ld c,b
	ld a,[wC6A1]
	bit 1,a
	jr nz,Func_2D3D
	ld bc,hE0

Func_2D3D:
	bit 0,a
	jr z,Func_2D42
	inc bc

Func_2D42:
	add hl,bc
	call Func_2E26
	di
	ld a,h
	add a,$98
	ld [de],a
	inc de
	ld a,l
	ld [de],a
	inc de
	pop hl
	pop af
	ld [de],a
	inc de
	xor a
	ld [de],a
	ei
	call Func_2E2D
	pop bc
	ret

Func_2D5B:
	ld a,c
	ldh [hD5],a
	call Func_2DC7
	ldh a,[hD8]
	swap a
	ld e,a
	ldh a,[hD7]
	or e
	ld e,a
	ld d,$C1
	ld a,[de]
	and $07
	ld [de],a
	jr Func_2D8F

Func_2D72:
	push de
	push hl
	call Func_2D7C
	pop hl
	pop de
	and $07
	ret

Func_2D7C:
	call Func_2E14
	jr Func_2D8F

Func_2D81:
	call Func_2E14
	ld a,$F0
	jr Func_2D8D

Func_2D88:
	call Func_2E14

Func_2D8B:
	ld a,$10

Func_2D8D:
	add a,h
	ld h,a

Func_2D8F:
	ld a,l
	swap a
	or h
	ld e,a
	ld d,$C1
	ld a,[de]
	ret

Func_2D98:
	push bc
	rst $30
	call Func_2DAC
	pop bc
	dec b
	jr nz,Func_2D98
	ret

Func_2DA2:
	push bc
	call Func_2DAC
	rst $30
	pop bc
	dec b
	jr nz,Func_2D98
	ret

Func_2DAC:
	ld hl,hD3
	xor a
	call Func_2E37
	ld hl,wDA5B
	ld a,[hl]
	inc a
	ld a,$10
	jp nz,Func_2E37
	ret

Func_2DBE:
	push bc
	push af
	call Func_2DFF
	ld a,b
	ld [de],a
	jr Func_2DD1

Func_2DC7:
	push bc
	push af
	call Func_2DFF
	ld a,$07
	ld [de],a
	ld c,$00

Func_2DD1:
	inc de
	pop af
	ld [de],a
	inc de
	ld a,c
	ld [de],a
	inc de
	pop bc
	call Func_2DF5
	xor a
	ld [de],a
	ret

Func_2DDF:
	ld hl,hB7
	ld a,[hli]
	or [hl]
	dec hl
	jr z,Func_2DF3
	dec [hl]
	ld a,[hli]
	cp $FF
	jr nz,Func_2DEE
	dec [hl]

Func_2DEE:
	call Func_2DFF
	or a
	ret

Func_2DF3:
	scf
	ret

Func_2DF5:
	push hl
	ld hl,hB7
	inc [hl]
	inc hl
	jr nz,Func_2DFE
	inc [hl]

Func_2DFE:
	pop hl

Func_2DFF:
	push hl
	ld hl,hB8
	ld a,[hld]
	ld l,[hl]
	and $03
	ld h,a
	ld e,l
	ld d,h
	add hl,hl
	add hl,de
	ld de,wC7F7
	add hl,de
	ld e,l
	ld d,h
	pop hl
	ret

Func_2E14:
	ld hl,hD7
	ld a,[hli]
	ld l,[hl]
	ld h,a
	ret

Func_2E1B:
	call Func_2E14
	add hl,de
	ld a,h
	ldh [hD7],a
	ld a,l
	ldh [hD8],a
	ret

Func_2E26:
	ldh a,[hF8]
	ld e,a
	ldh a,[hF9]
	ld d,a
	ret

Func_2E2D:
	ld a,e
	ldh [hF8],a
	ld a,d
	ldh [hF9],a
	cp $D4
	ret z
	ret

Func_2E37:
	ldh [hF3],a
	ld d,h
	ld e,l
	push hl
	ld bc,Func_000E
	add hl,bc
	ld [hl],$00
	pop hl
	ld a,[hli]
	ldh [hCB],a
	cp $FF
	ret z
	ld c,a
	ld a,[hli]
	cp c
	jr z,Func_2E57
	dec hl
	ld a,c
	ld [hli],a
	ld a,[hli]
	ldh [hCA],a
	ld c,a
	jr Func_2E61

Func_2E57:
	ld a,[hli]
	ldh [hCA],a
	ld c,a
	ld a,[hli]
	cp c
	jr z,Func_2E85
	dec hl
	ld a,c

Func_2E61:
	ld [hli],a
	ld a,[de]
	push hl
	add a,a
	ld l,a
	ld h,$00
	ld a,c
	ld bc,Data_384B
	add hl,bc
	ld c,[hl]
	inc hl
	ld b,[hl]
	and $FE
	ld l,a
	ld h,$00
	add hl,bc
	ld c,[hl]
	inc hl
	ld b,[hl]
	pop hl
	inc hl
	inc hl
	ld [hl],c
	inc hl
	ld [hl],b
	inc hl
	ld a,$FF
	ld [hli],a
	ld [hl],$01

Func_2E85:
	ld l,e
	ld h,d
	ld bc,$0004
	add hl,bc
	ld a,[hli]
	sub $04
	ldh [hC8],a
	ldh a,[$FF43]
	ld c,a
	ld a,[hl]
	sub c
	add a,$08
	ldh [hC9],a
	ld bc,$0004
	add hl,bc
	ld a,[hl]
	inc a
	jr z,Func_2EE4
	dec [hl]
	jr nz,Func_2EC9

Func_2EA4:
	push hl
	dec hl
	inc [hl]
	ld a,[hld]
	call Func_2F86
	or a
	jr z,Func_2EB8
	cp $FF
	jr z,Func_2EBE
	cp $F0
	jr c,Func_2EBE
	and $0F

Func_2EB8:
	pop hl
	dec a
	dec hl
	ld [hli],a
	jr Func_2EA4

Func_2EBE:
	pop de
	push de
	ld b,$05

Func_2EC2:
	ld a,[hli]
	ld [de],a
	inc de
	dec b
	jr nz,Func_2EC2
	pop hl

Func_2EC9:
	ld a,[hl]
	dec a
	jr nz,Func_2EE4
	push hl
	dec hl
	ld a,[hld]
	inc a
	call Func_2F86
	or a
	jr z,Func_2EDB
	cp $F0
	jr c,Func_2EE3

Func_2EDB:
	pop hl
	push hl
	ld bc,$0005
	add hl,bc
	ld [hl],$80

Func_2EE3:
	pop hl

Func_2EE4:
	inc hl
	ldh a,[hC8]
	add a,[hl]
	ldh [hC8],a
	inc hl
	ldh a,[hCA]
	ld b,a
	ld c,[hl]
	inc hl
	ld e,[hl]
	inc hl
	ld d,[hl]
	bit 7,d
	jr z,Func_2F00
	bit 6,d
	jr z,Func_2EFD
	ld b,$00

Func_2EFD:
	xor a
	ldh [hCA],a

Func_2F00:
	ld a,b
	and $01
	jr z,Func_2F0A
	ldh a,[hC9]
	sub c
	jr Func_2F0D

Func_2F0A:
	ldh a,[hC9]
	add a,c

Func_2F0D:
	ldh [hC9],a
	ld l,e
	ld a,d
	and $3F
	ld h,a
	ld a,[hli]
	ld b,a
	or a
	ret z
	ld a,[wDADB]
	ld e,a
	ld a,[wDADC]
	ld d,a

Func_2F20:
	ldh a,[hC8]
	add a,[hl]
	inc hl
	ld [de],a
	inc de
	ldh a,[hCA]
	and $01
	jr z,Func_2F33
	ldh a,[hC9]
	add a,$08
	sub [hl]
	jr Func_2F36

Func_2F33:
	ldh a,[hC9]
	add a,[hl]

Func_2F36:
	inc hl
	ld [de],a
	inc de
	ldh a,[hCB]
	or a
	jr z,Func_2F47
	cp $06
	jr nz,Func_2F65
	ld a,[hli]
	sub $1C
	jr Func_2F66

Func_2F47:
	ld a,[hl]
	cp $B4
	jr z,Func_2F65
	cp $B6
	jr z,Func_2F65
	cp $BC
	jr z,Func_2F65
	cp $BE
	jr z,Func_2F65
	cp $58
	jr c,Func_2F60
	cp $60
	jr c,Func_2F65

Func_2F60:
	ld a,[hli]
	add a,$60
	jr Func_2F66

Func_2F65:
	ld a,[hli]

Func_2F66:
	ld [de],a
	inc de
	ldh a,[hCA]
	and $01
	jr z,Func_2F73
	ld a,[hli]
	xor $20
	jr Func_2F74

Func_2F73:
	ld a,[hli]

Func_2F74:
	ld c,a
	ldh a,[hF3]
	add a,c
	ld [de],a
	inc de
	dec b
	jr nz,Func_2F20

Func_2F7D:
	ld a,e
	ld [wDADB],a
	ld a,d
	ld [wDADC],a
	ret

Func_2F86:
	ld c,a
	add a,a
	add a,a
	add a,c
	ld c,a
	ld b,$00
	ld a,[hld]
	ld l,[hl]
	ld h,a
	ld e,l
	ld d,h
	add hl,bc
	ld a,[hl]
	ret

Func_2F95:
	call Func_31C8

Func_2F98:
	rst $30
	xor a
	ldh [hA2],a
	ldh [hA1],a
	ld b,$0E
	ld hl,wDADD

Func_2FA3:
	push bc
	push hl
	call Func_303E
	pop hl
	pop bc
	ld de,Rst_20
	add hl,de
	dec b
	jr nz,Func_2FA3
	ldh a,[hB2]
	inc a
	cp $10
	jr c,Func_2FC1
	ldh a,[hB3]
	xor $01
	ldh [hB3],a
	xor a
	ldh [hB1],a

Func_2FC1:
	ldh [hB2],a
	ld b,$07

Func_2FC5:
	push bc
	call Func_31D7
	pop bc
	dec b
	jr nz,Func_2FC5
	ld a,[wDA5B]
	inc a
	jp z,Func_2F98
	ld a,[wDA5D]
	and $FE
	cp $04
	call z,Func_2FE1
	jp Func_2F98

Func_2FE1:
	ldh a,[hBB]
	dec a
	jr z,Func_3016
	ld hl,hA1
	inc [hl]
	ld hl,wDA5F
	inc [hl]
	inc [hl]
	ld a,[hl]
	and $0F
	ret nz
	ld a,[hli]
	ld l,[hl]
	add a,$10
	ld h,a
	call Func_2D8F
	or a
	ret z
	ld a,[wDA5D]
	and $01
	ld [wDA5D],a
	ld hl,hA1
	dec [hl]
	ld hl,wDA5F
	ld a,[hli]
	ld l,[hl]
	ld h,a
	call Func_2D8F
	ld a,$10
	ld [de],a
	ret

Func_3016:
	ld hl,hA1
	inc [hl]
	ld hl,wDA5F
	dec [hl]
	dec [hl]
	ld a,[wDA79]
	cp [hl]
	ret nz
	ld a,[wDA5D]
	and $01
	ld [wDA5D],a
	ld hl,hA1
	dec [hl]
	ld hl,wDA5F
	ld a,[hli]
	ld l,[hl]
	ld h,a
	call Func_2D8F
	ld a,[de]
	or $10
	ld [de],a
	ret

Func_303E:
	ld a,[hl]
	or a
	ret z
	push hl
	inc hl
	inc hl
	ld a,[hld]
	dec hl
	and $FE
	cp $0E
	push af
	ld a,$00
	call nz,Func_2E37
	pop af
	ld a,$00
	call z,Func_379F
	pop de
	ld hl,hA1
	inc [hl]
	push de
	inc de
	inc de
	ld a,[de]
	ld c,a
	inc de
	inc de
	ld a,[de]
	ld h,a
	inc de
	ld a,[de]
	ld l,a
	ld a,c
	and $FE
	cp $0E
	jp z,Func_3197
	cp $0C
	jp z,Func_3197
	cp $08
	jp z,Func_30E9
	cp $06
	jp z,Func_316F
	cp $04
	jp z,Func_3118
	cp $02
	jr nz,Func_30A7
	push hl
	ld hl,$0015
	add hl,de
	ld a,[hl]
	or a
	jr z,Func_3094
	dec [hl]
	pop hl
	pop de
	ret

Func_3094:
	pop hl
	dec l
	dec l
	bit 0,c
	jr z,Func_309F
	inc l
	inc l
	inc l
	inc l

Func_309F:
	ld a,l
	ld [de],a
	pop de
	and $0F
	ret nz
	jr Func_30D8

Func_30A7:
	inc h
	inc h
	ld a,h
	dec de
	ld [de],a
	pop de
	and $0F
	ret nz
	push de
	push hl
	ld a,h
	add a,$10
	ld h,a
	call Func_2D8F
	ld b,e
	pop hl
	pop de
	or a
	ret z
	ld a,c
	cp $0A
	jr z,Func_30D8
	push de
	push hl
	ld hl,$001B
	add hl,de
	ld e,[hl]
	inc hl
	ld d,[hl]
	inc de
	inc de
	ld a,b
	sub $10
	ld [de],a
	pop hl
	pop de
	ld a,$03
	ldh [hFD],a

Func_30D8:
	ld a,[de]
	ld c,a
	xor a
	ld [de],a
	push hl
	call Func_2D8F
	ld a,c
	ld [de],a
	pop hl
	call Func_2CDD
	jp Func_3166

Func_30E9:
	ld b,l
	ld hl,Rst_18
	add hl,de
	ld a,[hl]
	dec [hl]
	bit 7,a
	jr nz,Func_30F6
	jr Func_311F

Func_30F6:
	pop hl
	ld c,[hl]
	ld [hl],$00
	inc hl
	inc hl
	inc hl
	inc hl
	ld a,[hli]
	add a,$08
	and $F0
	ld d,a
	ld a,[hl]
	add a,$04
	and $F0
	ld e,a
	swap a
	or d
	ld l,a
	ld h,$C1
	ld [hl],c
	ld l,e
	ld h,d
	call Func_2CDD
	jr Func_316A

Func_3118:
	ld b,l
	ld hl,Rst_18
	add hl,de
	ld a,[hl]
	inc [hl]

Func_311F:
	inc hl
	srl a
	jr c,Func_315B
	push hl
	ld l,a
	ld h,$00
	ld de,Data_31A8
	add hl,de
	ld a,[hl]
	ld d,a
	cp $80
	jr z,Func_3162
	pop hl
	ld a,[hli]
	add a,d
	ld d,a
	ld a,[hl]
	bit 0,c
	jr nz,Func_314C
	sub $C0
	ld [hl],a
	pop hl
	push hl
	inc hl
	inc hl
	inc hl
	inc hl
	ld [hl],d
	inc hl
	ld a,[hl]
	sbc a,$00
	ld [hl],a
	jr Func_315B

Func_314C:
	add a,$C0
	ld [hl],a
	pop hl
	push hl
	inc hl
	inc hl
	inc hl
	inc hl
	ld [hl],d
	inc hl
	ld a,[hl]
	adc a,$00
	ld [hl],a

Func_315B:
	pop hl

Func_315C:
	ld hl,hA2
	inc [hl]
	jr Func_316A

Func_3162:
	pop hl
	pop hl
	ld [hl],$00

Func_3166:
	ld hl,hA2
	dec [hl]

Func_316A:
	ld hl,hA1
	dec [hl]
	ret

Func_316F:
	pop hl
	push hl
	ld bc,$001E
	add hl,bc
	ld c,[hl]
	pop hl
	push hl
	ld de,$0004
	add hl,de
	dec [hl]
	ld d,[hl]
	inc hl
	ld e,[hl]
	pop hl
	ld a,c
	and $F0
	cp d
	ret nz
	ld b,[hl]
	ld [hl],$00
	ld l,e
	ld h,d
	push hl
	call Func_2D8F
	ld a,b
	ld [de],a
	pop hl
	call Func_2CDD
	jr Func_3166

Func_3197:
	pop hl
	push hl
	ld bc,Func_000E
	add hl,bc
	ld a,[hl]
	pop hl
	or a
	jr z,Func_315C
	ld [hl],$00
	jp Func_3166

; ---- data $31A7-$31C7 ----
INCLUDE "src/data/data_31A7.asm"

Func_31C8:
	ld b,$0E
	ld hl,wDADD
	ld de,Rst_20

Func_31D0:
	ld [hl],$00
	add hl,de
	dec b
	jr nz,Func_31D0
	ret

Func_31D7:
	ldh a,[hB1]
	ld l,a
	ld h,$C1

Func_31DC:
	ld a,l
	cp $FF
	jr z,Func_31FC
	ld a,[hli]
	cp $06
	jr z,Func_31EA
	cp $02
	jr nz,Func_31DC

Func_31EA:
	call Func_31FC
	dec hl
	xor a

Func_31EF:
	push af
	push hl
	call Func_3200
	pop hl
	pop af
	inc a
	cp $04
	jr nz,Func_31EF
	ret

Func_31FC:
	ld a,l
	ldh [hB1],a
	ret

Func_3200:
	push bc
	ld [wC6A1],a
	call Func_2483
	ld e,a
	ldh a,[hB3]
	or a
	jr z,Func_3227
	push hl
	ld a,[hl]
	cp $06
	jr z,Func_321B
	ld a,e
	sub $E0
	ld hl,Data_322B
	jr Func_3221

Func_321B:
	ld a,e
	sub $C4
	ld hl,Data_3243

Func_3221:
	ld e,a
	ld d,$00
	add hl,de
	ld e,[hl]
	pop hl

Func_3227:
	ld a,e
	jp Func_2D27

; ---- data $322B-$325A ----
INCLUDE "src/data/data_322B.asm"

Func_325B:
	call Func_36D7
	call Func_34BE

Func_3261:
	rst $30
	ldh a,[hBB]
	dec a
	jr z,Func_3272
	call Func_32B2
	ldh a,[h8A]
	bit 1,a
	jr nz,Func_3261
	jr Func_32A0

Func_3272:
	ld hl,hB8
	ld a,[hld]
	ld l,[hl]
	ld h,a

Func_3278:
	ld a,h
	or l
	jr z,Func_32A0
	dec hl
	push hl
	ld a,h
	and $03
	ld h,a
	ld e,l
	ld d,h
	add hl,hl
	add hl,de
	ld de,wC7F7
	add hl,de
	ld a,[hl]
	pop hl
	or a
	jr z,Func_32A0
	cp $07
	jr z,Func_3297
	cp $13
	jr nz,Func_3278

Func_3297:
	call Func_34C1
	ldh a,[h8A]
	bit 0,a
	jr nz,Func_3261

Func_32A0:
	ldh a,[hBC]
	or a
	jr nz,Func_3261
	xor a
	ldh [hBB],a
	ld a,$01
	call Func_0494
	ld a,$00
	rst $10
	jr Func_3261

Func_32B2:
	xor a
	ldh [hBC],a
	call Func_2DFF
	ld l,e
	ld h,d
	ld a,[hl]
	or a
	jp z,Func_36D4
	push hl
	call Func_2DF5
	pop hl
	ld a,[hli]
	ldh [hB4],a
	ld b,a
	and $0F
	cp $07
	jr z,Func_32DE
	cp $02
	jp z,Func_339C
	cp $03
	jp z,Func_339C
	cp $06
	jp z,Func_339C
	ret

Func_32DE:
	call Func_36DF
	ld a,[hli]
	cp $FF
	jr z,Func_3317
	cp $40
	jp z,Func_3467
	ld c,a
	and $FE
	cp $1A
	jp z,Func_3320
	cp $2A
	jp z,Func_3320
	cp $28
	jr z,Func_3320
	and $0E
	cp $02
	jr z,Func_3320
	cp $04
	jr z,Func_3368
	cp $06
	jr z,Func_332C
	cp $08
	jr z,Func_3331
	cp $0A
	jr z,Func_3320
	cp $0E
	jr z,Func_3320
	ret

Func_3317:
	call Func_36D7
	call Func_099C
	jp Func_36CE

Func_3320:
	ld de,hF0
	bit 0,c
	jr z,Func_3334
	ld de,Rst_10
	jr Func_3334

Func_332C:
	ld de,$F000
	jr Func_3334

Func_3331:
	ld de,Data_1000

Func_3334:
	push de
	call Func_2D7C
	ld a,[de]
	and $07
	ld [de],a
	pop de
	add hl,de
	call Func_2D8F
	cp $02
	jr z,Func_3349
	cp $04
	jr nz,Func_334A

Func_3349:
	xor a

Func_334A:
	ld b,a
	or $10
	ld [de],a
	ld a,h
	ldh [hB5],a
	ld a,l
	ldh [hB6],a
	ld a,c
	ldh [hD5],a
	and $FE
	cp $2A
	jr z,Func_3362
	cp $1A
	jp nz,Func_347A

Func_3362:
	call Func_29DF
	jp Func_347A

Func_3368:
	call Func_36D7
	push hl
	call Func_2D7C
	ld a,[de]
	and $07
	ld [de],a
	pop hl
	ld a,c
	ldh [hD5],a
	ld a,[hli]
	and $F0
	ld c,a

Func_337B:
	push bc
	rst $30
	call Func_34BE
	ld de,EntryPoint
	call Func_2E1B
	pop bc
	ld a,h
	and $0F
	jr nz,Func_337B
	call Func_2D88
	or a
	jr z,Func_337B
	call Func_2D7C
	ld a,[de]
	or $10
	ld [de],a
	jp Func_348D

Func_339C:
	call Func_36D7
	inc hl
	ld a,[hl]
	bit 4,b
	jr nz,Func_33AD
	bit 5,b
	jr nz,Func_33B8
	dec hl
	ld a,[hli]
	jr Func_33B8

Func_33AD:
	dec hl
	bit 0,[hl]
	jr nz,Func_33B6
	inc a
	inc hl
	jr Func_33B8

Func_33B6:
	dec a
	inc hl

Func_33B8:
	push hl
	ld l,a
	ld h,$C1
	ld a,[hl]
	and $10
	ld [hl],a
	ld a,l
	and $F0
	ld h,a
	ld a,l
	and $0F
	swap a
	ld l,a
	push hl
	push bc
	call Func_2CDD
	call Func_2CC8
	pop bc
	ldh a,[hB4]
	and $0F
	ld [hli],a
	ld [hl],$00
	inc hl
	bit 4,b
	jr nz,Func_33E7
	bit 5,b
	jp nz,Func_3411
	jp Func_342C

Func_33E7:
	pop bc
	pop de
	dec de
	ld a,[de]
	or $02
	ld [hli],a
	inc hl
	ld [hl],b
	inc hl
	ld [hl],c
	call Func_2D72
	dec a
	jr z,Func_33FF
	ld a,[de]
	and $01
	or $1C
	jr Func_3404

Func_33FF:
	ld a,[de]
	and $01
	or $1E

Func_3404:
	ldh [hD5],a
	ldh a,[hD7]
	ldh [hB5],a
	ldh a,[hD8]
	ldh [hB6],a
	jp Func_347A

Func_3411:
	pop bc
	pop de
	dec de
	ld a,[de]
	and $01
	or $04
	ld [hli],a
	inc hl
	ld [hl],b
	inc hl
	ld [hl],c
	ld de,Rst_18
	add hl,de
	ld [hl],$00
	inc hl
	ld [hl],b
	inc hl
	ld [hl],$00
	jp Func_349E

Func_342C:
	ld [hl],$0A
	inc hl
	inc hl
	pop bc
	ld [hl],b
	inc hl
	ld [hl],c
	ld bc,$0019
	add hl,bc
	pop de
	dec de
	ld a,[de]
	and $F0
	ld [hl],a
	call Func_34BE
	call Func_36D2
	rst $30
	call Func_2DFF
	ld a,[de]
	cp $07
	jr z,Func_345B
	or a
	jr z,Func_345B
	and $F0
	jp z,Func_32B2

Func_3455:
	rst $30
	ldh a,[hA1]
	or a
	jr z,Func_3460

Func_345B:
	call Func_34BE
	jr Func_3455

Func_3460:
	call Func_34BE
	rst $30
	jp Func_349E

Func_3467:
	ld a,[wDA5D]
	and $01
	or $04
	ld [wDA5D],a
	call Func_378C
	xor a
	ld [de],a
	jp Func_3455

Func_3479:
	rst $30

Func_347A:
	call Func_36D7
	call Func_34BE
	ldh a,[hE1]
	or a
	jr z,Func_3479
	ldh a,[hB5]
	ldh [hD7],a
	ldh a,[hB6]
	ldh [hD8],a

Func_348D:
	ld de,hD5
	ld a,[de]
	and $01
	ld [de],a
	call Func_2D72
	dec a
	jr nz,Func_349E
	ld a,[de]
	or $10
	ld [de],a

Func_349E:
	xor a
	ldh [hBC],a
	call Func_2DFF
	ld a,[de]
	inc de
	cp $07
	jr nz,Func_34B8
	ld a,[de]
	cp $40
	jp z,Func_32B2
	and $0E
	cp $04
	jp z,Func_32B2
	ret

Func_34B8:
	bit 4,a
	ret nz
	jp Func_32B2

Func_34BE:
	jp Func_2DAC

Func_34C1:
	xor a
	ldh [hBC],a
	call Func_2DDF
	jp c,Func_36D4
	ld l,e
	ld h,d
	ld a,[hli]
	ldh [hB4],a
	ld b,a
	and $0F
	cp $07
	jr z,Func_34E6
	cp $02
	jp z,Func_35AF
	cp $03
	jp z,Func_35AF
	cp $06
	jp z,Func_35AF
	ret

Func_34E6:
	call Func_36DF
	ldh a,[hD7]
	ldh [hB5],a
	ldh a,[hD8]
	ldh [hB6],a
	ld a,[hli]
	cp $FF
	jp z,Func_3652
	cp $40
	jp z,Func_365A
	ld c,a
	and $FE
	cp $1A
	jp z,Func_3528
	cp $2A
	jp z,Func_3528
	cp $28
	jr z,Func_354F
	and $0E
	cp $02
	jr z,Func_354F
	cp $04
	jr z,Func_3582
	cp $06
	jr z,Func_355B
	cp $08
	jr z,Func_3560
	cp $0A
	jr z,Func_354F
	cp $0E
	jr z,Func_354F
	ret

Func_3528:
	push bc
	push hl
	ldh [hBC],a
	push bc
	ld a,c
	and $01
	ldh [hD5],a
	call Func_3732
	ld b,$0A
	call Func_36E8
	pop bc
	ld a,c
	xor $01
	ld c,a
	call Func_3732
	ld b,$0C
	call Func_36E8
	call Func_2D7C
	ld a,$04
	ld [de],a
	pop hl
	pop bc

Func_354F:
	ld de,hF0
	bit 0,c
	jr nz,Func_3565
	ld de,Rst_10
	jr Func_3565

Func_355B:
	ld de,Data_1000
	jr Func_3565

Func_3560:
	ld de,$F000
	jr Func_3565

Func_3565:
	push de
	call Func_2D7C
	ld a,[de]
	and $07
	ld [de],a
	pop de
	add hl,de
	call Func_2D8F
	ld a,[de]
	or $10
	ld [de],a
	ld a,h
	ldh [hD7],a
	ld a,l
	ldh [hD8],a
	ld a,c
	ldh [hD5],a
	jp Func_3673

Func_3582:
	call Func_36D7
	push hl
	call Func_2D7C
	ld a,[de]
	and $07
	ld [de],a
	pop hl
	ld a,c
	ldh [hD5],a
	ld a,[hli]
	and $F0
	ld c,a

Func_3595:
	push bc
	rst $30
	call Func_3751
	ld de,$FF00
	call Func_2E1B
	pop bc
	ld a,h
	cp c
	jr nz,Func_3595
	call Func_2D7C
	ld a,[de]
	or $10
	ld [de],a
	jp Func_34C1

Func_35AF:
	bit 5,b
	call z,Func_36F4
	inc hl
	ld a,[hl]
	push hl
	ld l,a
	ld h,$C1
	ld [hl],$00
	ld a,l
	and $F0
	ld h,a
	ld a,l
	and $0F
	swap a
	ld l,a
	push hl
	push bc
	call Func_2CDD
	call Func_2CC8
	pop bc
	ldh a,[hB4]
	and $0F
	ld [hli],a
	ld [hl],$00
	inc hl
	bit 4,b
	jr nz,Func_35FC
	bit 5,b
	jp nz,Func_3620
	ld [hl],$06
	inc hl
	inc hl
	pop bc
	ld [hl],b
	inc hl
	ld [hl],c
	ld bc,$0019
	add hl,bc
	pop de
	dec de
	ld a,[de]
	and $F0
	ld [hl],a

Func_35F2:
	call Func_3751
	call Func_36D2
	rst $30
	jp Func_34C1

Func_35FC:
	pop bc
	pop de
	dec de
	ld a,[de]
	xor $01
	or $02
	ld [hli],a
	inc hl
	ld [hl],b
	inc hl
	ld [hl],c
	call Func_2D72
	dec a
	jr z,Func_3616
	ld a,[de]
	and $01
	or $1C
	jr Func_361B

Func_3616:
	ld a,[de]
	and $01
	or $1E

Func_361B:
	ldh [hD5],a
	jp Func_3673

Func_3620:
	pop bc
	pop de
	dec de
	ld a,[de]
	and $01
	xor $01
	or $08
	ld [hli],a
	inc hl
	ld [hl],b
	inc hl
	bit 0,a
	jr z,Func_3638
	ld a,c
	sub $17
	ld [hl],a
	jr Func_363C

Func_3638:
	ld a,c
	add a,$17
	ld [hl],a

Func_363C:
	ld de,Rst_18
	add hl,de
	ld [hl],$3C
	inc hl
	ld [hl],b
	inc hl
	ld [hl],$00
	ld b,$3C

Func_3649:
	call Func_36FF
	dec b
	jr nz,Func_3649
	jp Func_34C1

Func_3652:
	call Func_36D7
	call Func_099C
	jr Func_36CE

Func_365A:
	ld a,[hl]
	and $F0
	ld [wDA79],a
	ld a,[wDA5D]
	and $01
	or $04
	ld [wDA5D],a
	call Func_378C
	xor a
	ld [de],a
	jp Func_35F2

Func_3672:
	rst $30

Func_3673:
	call Func_36D7
	call Func_3751
	ldh a,[hD5]
	and $FE
	cp $2A
	jr z,Func_3685
	cp $1A
	jr nz,Func_369E

Func_3685:
	ldh a,[hDB]
	cp $02
	jr nz,Func_369E
	ldh a,[hDC]
	dec a
	jr nz,Func_369E
	ldh a,[hD5]
	and $01
	ld c,a
	ldh a,[hB5]
	ld h,a
	ldh a,[hB6]
	ld l,a
	call Func_2CF5

Func_369E:
	ldh a,[hE1]
	or a
	jr z,Func_3672
	ldh a,[hD5]
	and $FE
	cp $2A
	jr z,Func_36AF
	cp $1A
	jr nz,Func_36BF

Func_36AF:
	ldh a,[hD5]
	and $01
	xor $01
	ld c,a
	ldh a,[hB5]
	ld h,a
	ldh a,[hB6]
	ld l,a
	call Func_2CF5

Func_36BF:
	call Func_2B82
	call Func_2D7C
	and $07
	dec a
	jr nz,Func_36CE
	ld a,[de]
	or $10
	ld [de],a

Func_36CE:
	xor a
	ldh [hBC],a
	ret

Func_36D2:
	jr Func_36D7

Func_36D4:
	jp Func_2DAC

Func_36D7:
	ld a,$01
	ldh [hBC],a
	ret

Func_36DC:
	call Func_36FF

Func_36DF:
	ldh a,[hA1]
	or a
	jr nz,Func_36DC
	ret

Func_36E5:
	push bc
	rst $30
	pop bc

Func_36E8:
	push bc
	call Func_36D4
	pop bc
	dec b
	jr nz,Func_36E5
	ret

Func_36F1:
	call Func_36FF

Func_36F4:
	ldh a,[hA1]
	or a
	jr nz,Func_36F1
	ldh a,[hA2]
	or a
	jr nz,Func_36F1
	ret

Func_36FF:
	push bc
	push hl
	call Func_36D2
	ld hl,hD3
	ldh a,[hBB]
	dec a
	push af
	ld a,$00
	call z,Func_379F
	pop af
	dec a
	ld a,$00
	call z,Func_2E37
	ld hl,wDA5B
	ld a,[hl]
	inc a
	jr z,Func_372E
	ldh a,[hBB]
	dec a
	push af
	ld a,$10
	call z,Func_379F
	pop af
	dec a
	ld a,$10
	call z,Func_2E37

Func_372E:
	rst $30
	pop hl
	pop bc
	ret

Func_3732:
	push bc
	call Func_2CC8
	pop bc
	ld [hl],$04
	inc hl
	ld [hl],$00
	inc hl
	ld a,c
	and $01
	or $0E
	ld [hli],a
	inc hl
	ldh a,[hD7]
	ld [hli],a
	ldh a,[hD8]
	bit 0,c
	jr z,Func_374F
	add a,$08

Func_374F:
	ld [hli],a
	ret

Func_3751:
	ld hl,hD5
	call Func_376F
	ld hl,wDA5D
	call Func_376F
	ld hl,hD3
	xor a
	call Func_379F
	ld hl,wDA5B
	ld a,[hl]
	inc a
	ld a,$10
	call nz,Func_379F
	ret

Func_376F:
	ld a,[hl]
	and $1E
	ret nz
	push hl
	inc hl
	ld a,[hli]
	ld l,[hl]
	sub $10
	ld h,a
	call Func_2D8F
	pop hl
	ld b,$00
	cp $03
	jr nz,Func_3786
	ld b,$20

Func_3786:
	ld a,[hl]
	and $01
	or b
	ld [hl],a
	ret

Func_378C:
	ld a,[wDA5F]
	and $F0
	ld e,a
	ld a,[wDA60]
	and $F0
	swap a
	or e
	ld e,a
	ld d,$C1
	ld a,[de]
	ret

Func_379F:
	ldh [hF3],a
	ld d,h
	ld e,l
	push hl
	ld bc,Func_000E
	add hl,bc
	ld [hl],$00
	pop hl
	ld a,[hli]
	ldh [hCB],a
	inc hl
	ld a,[hli]
	ldh [hCA],a
	ld c,a
	ld a,[hli]
	cp c
	jr z,Func_37FA
	dec hl
	ld a,c
	ld [hli],a
	ld a,[de]
	push hl
	add a,a
	ld l,a
	ld h,$00
	ld a,c
	ld bc,Data_384B
	add hl,bc
	ld c,[hl]
	inc hl
	ld b,[hl]
	and $FE
	ld l,a
	ld h,$00
	add hl,bc
	ld c,[hl]
	inc hl
	ld b,[hl]
	pop hl
	inc hl
	inc hl
	ld [hl],c
	inc hl
	ld [hl],b
	inc hl
	push hl
	ld h,$FF

Func_37DB:
	inc h
	ld a,[bc]
	or a
	jr z,Func_37EF
	cp $F0
	jr nc,Func_37EB
	inc bc
	inc bc
	inc bc
	inc bc
	inc bc
	jr Func_37DB

Func_37EB:
	inc a
	jr nz,Func_37EF
	inc h

Func_37EF:
	ld a,h
	pop hl
	dec a
	ld [hli],a
	ld [hl],$01
	ld bc,Func_000B
	add hl,bc
	ld [hl],a

Func_37FA:
	ld l,e
	ld h,d
	ld bc,$0004
	add hl,bc
	ld a,[hli]
	sub $04
	ldh [hC8],a
	ldh a,[$FF43]
	ld c,a
	ld a,[hl]
	sub c
	add a,$08
	ldh [hC9],a
	ld bc,$0004
	add hl,bc
	ld a,[hl]
	inc a
	jr z,Func_3848
	dec [hl]
	jr nz,Func_3837
	push hl
	dec hl
	ld a,[hl]
	dec [hl]
	or a
	jr nz,Func_3828
	push hl
	ld bc,Func_000C
	add hl,bc
	ld a,[hl]
	pop hl
	ld [hl],a

Func_3828:
	dec hl
	call Func_2F86
	pop de
	push de
	ld b,$05

Func_3830:
	ld a,[hli]
	ld [de],a
	inc de
	dec b
	jr nz,Func_3830
	pop hl

Func_3837:
	ld a,[hl]
	dec a
	jr nz,Func_3848
	dec hl
	ld a,[hli]
	or a
	jr nz,Func_3848
	push hl
	ld bc,$0005
	add hl,bc
	ld [hl],$80
	pop hl

Func_3848:
	jp Func_2EE4

; ---- data $384B-$3F30 ----
INCLUDE "src/data/data_384B.asm"

Func_3F31:
	ld a,$10
	ldh [hFA],a
	ld hl,Data_3F5A

Func_3F38:
	ld a,[hli]
	or a
	jr z,Func_3F41
	ld c,a
	ld a,[hli]
	ld [$ff00+c],a
	jr Func_3F38

Func_3F41:
	ld b,$08
	ld hl,wD55C

Func_3F46:
	ld [hl],$01
	ld de,$0006
	add hl,de
	ld [hl],$00
	ld e,$19
	add hl,de
	ld [hl],$00
	ld e,$61
	add hl,de
	dec b
	jr nz,Func_3F46
	ret

; ---- data $3F5A-$3F72 ----
INCLUDE "src/data/data_3F5A.asm"

Func_3F73:
	ld hl,hFB
	ld a,[hli]
	cp [hl]
	jr z,Func_3F9F
	ld [hl],a
	add a,a
	add a,a
	ld l,a
	ld h,$00
	add hl,hl
	ld de,Data_44F4
	add hl,de
	ld bc,Data_0412
	ld de,wD55C

Func_3F8B:
	push bc
	call Func_3FA0
	pop bc
	push hl
	ld hl,$0080
	add hl,de
	ld e,l
	ld d,h
	pop hl
	ld a,c
	add a,$05
	ld c,a
	dec b
	jr nz,Func_3F8B

Func_3F9F:
	ret

Func_3FA0:
	ld a,[hli]
	or [hl]
	jr z,Func_3FC1
	push de
	ld a,[de]
	res 0,a
	ld [de],a
	inc de
	xor a
	ld [de],a
	inc de
	dec hl
	inc de
	ld a,[hli]
	ld [de],a
	inc de
	ld a,[hli]
	ld [de],a
	xor a
	inc de
	inc de
	ld [de],a
	push hl
	ld hl,$0019
	add hl,de
	ld [hl],a
	pop hl
	pop de
	ret

Func_3FC1:
	inc hl
	ld a,[de]
	set 0,a
	ld [de],a
	and $FE
	ldh [hCD],a
	dec c
	jp Func_440A

Func_3FCE:
	ld hl,hFD
	ld a,[hli]
	cp [hl]
	jr z,Func_3FFA
	ld [hl],a
	add a,a
	add a,a
	ld l,a
	ld h,$00
	ld de,Data_454C
	add hl,hl
	add hl,de
	ld bc,Data_0412
	ld de,wD75C

Func_3FE6:
	push bc
	call Func_3FFB
	pop bc
	push hl
	ld hl,$0080
	add hl,de
	ld e,l
	ld d,h
	pop hl
	ld a,c
	add a,$05
	ld c,a
	dec b
	jr nz,Func_3FE6

Func_3FFA:
	ret

Func_3FFB:
	ld a,[hli]
	or [hl]
	jr z,Func_401B
	ld a,[de]
