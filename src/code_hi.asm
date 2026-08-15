; ============================================================
; Main code ($4000-$7FFF) - ROMX bank 1
; ============================================================
	res 0,a
	ld [de],a
	push hl
	ld hl,$FE00
	add hl,de
	set 1,[hl]
	pop hl
	inc de
	inc de
	dec hl
	xor a
	ld [de],a
	inc de
	ld a,[hli]
	ld [de],a
	inc de
	ld a,[hli]
	ld [de],a
	dec de
	dec de
	dec de
	dec de
	ret

Func_401B:
	inc hl
	ld a,[de]
	set 0,a
	ld [de],a
	and $FE
	ldh [hCD],a
	dec c
	push hl
	ld hl,$FE00
	add hl,de
	res 1,[hl]
	bit 0,[hl]
	call nz,Func_440A
	inc c
	pop hl
	ret

Func_4034:
	xor a
	ldh [$FFFF],a
	ld c,$11
	ld hl,wD55C
	call Func_4078
	ld c,$16
	ld hl,wD5DC
	call Func_4078
	ld c,$1B
	ld hl,wD65C
	call Func_4078
	ld c,$20
	ld hl,wD6DC
	call Func_4078
	ld a,$01
	ldh [$FFFF],a
	ld c,$11
	ld hl,wD75C
	call Func_4078
	ld c,$16
	ld hl,wD7DC
	call Func_4078
	ld c,$1B
	ld hl,wD85C
	call Func_4078
	ld c,$20
	ld hl,wD8DC

Func_4078:
	ld a,[hli]
	bit 0,a
	jp nz,Func_442A
	and $FE
	ldh [hCD],a
	ld a,[hl]
	or a
	jr z,Func_40FB
	ld a,c
	cp $1B
	jr nz,Func_409E
	ld a,[hl]
	cp $05
	jr nc,Func_409E
	cp $03
	jr nc,Func_4097
	ld a,$60
	db $11

Func_4097: ; jump target inside previous instruction
	db $3E,$40
	inc c
	call Func_4434
	dec c

Func_409E:
	dec [hl]
	ld de,Func_003B
	add hl,de
	ld a,[hli]
	or a
	ret z
	ld a,c
	cp $20
	ret z
	ld a,[hl]
	ld b,a
	or a
	jr z,Func_40E7
	push hl
	inc hl
	ld e,[hl]
	inc hl
	ld d,[hl]
	inc hl
	push hl
	xor a
	bit 7,b
	jr z,Func_40C8
	ld a,e
	cpl
	ld e,a
	ld a,d
	cpl
	ld d,a
	inc de
	ld a,b
	cpl
	ld b,a
	inc b
	ld a,$FF

Func_40C8:
	ld hl,Rst_00

Func_40CB:
	add hl,de
	dec b
	jr nz,Func_40CB
	ld b,a
	pop de
	ld a,[de]
	add a,l
	ld [de],a
	inc de
	ld a,[de]
	adc a,h
	ld [de],a
	inc de
	inc c
	inc c
	call Func_4434
	ld a,[de]
	adc a,b
	ld [de],a
	inc de
	inc c
	call Func_4434
	pop hl

Func_40E7:
	dec hl
	dec [hl]
	ret nz
	dec hl
	dec hl
	ld e,[hl]
	inc hl
	ld d,[hl]
	inc hl
	ld a,[de]
	inc de
	ld [hli],a
	ld a,[de]
	inc de
	ld [hld],a
	dec hl
	ld [hl],d
	dec hl
	ld [hl],e
	ret

Func_40FB:
	inc hl
	inc hl
	ld e,[hl]
	inc hl
	ld d,[hl]

Func_4100:
	ld a,[de]
	or a
	jr z,Func_413F
	and $F0
	cp $F0
	jp nz,Func_4329
	ld a,[de]
	cp $F1
	jp c,Func_41AE
	jp z,Func_41B6
	cp $F3
	jp c,Func_41FA
	jp z,Func_420C
	cp $F5
	jp c,Func_4240
	jp z,Func_424A
	cp $F7
	jp c,Func_426E
	jp z,Func_427C
	cp $F9
	jp c,Func_4299
	jp z,Func_42B8
	cp $FB
	jp c,Func_42CB
	jp z,Func_431B
	jp Func_442A

Func_413F:
	ld [hl],d
	dec hl
	ld [hl],e
	ldh a,[$FFFF]
	or a
	jp z,Func_440A
	ld de,hFD
	add hl,de
	ld a,[hl]
	bit 0,[hl]
	ret nz
	set 0,[hl]
	ld de,$FE00
	add hl,de
	res 1,[hl]
	push bc
	push hl
	ld bc,Data_0400
	ld hl,wD75C
	ld de,$0080
	ld a,$01

Func_4165:
	and [hl]
	add hl,de
	dec b
	jr nz,Func_4165
	bit 0,a
	jr z,Func_4174
	ld a,$FF
	ldh [hFD],a
	ldh [hFE],a

Func_4174:
	pop hl
	pop bc
	ld de,$0044
	add hl,de
	ld a,c
	cp $11
	jr nz,Func_4185
	ld a,[hl]
	dec c
	call Func_4434
	inc c

Func_4185:
	ld a,c
	cp $1B
	jr nz,Func_41A3
	xor a
	ldh [$FF1A],a
	push de
	push hl
	ld b,$10
	ld hl,wD95C
	ld de,$FF30

Func_4197:
	ld a,[hli]
	ld [de],a
	inc de
	dec b
	jr nz,Func_4197
	pop hl
	pop de
	ld a,$80
	ldh [$FF1A],a

Func_41A3:
	inc hl
	ldh a,[$FF25]
	and [hl]
	inc hl
	or [hl]
	ldh [$FF25],a
	jp Func_440A

Func_41AE:
	call Func_442B
	inc hl
	ld [hld],a
	jp Func_4100

Func_41B6:
	call Func_442B
	ld a,c
	cp $1B
	jr nz,Func_41F7
	push de
	push hl
	ld a,b
	add a,a
	add a,a
	ld l,a
	ld h,$00
	add hl,hl
	add hl,hl
	ld de,Data_464F
	add hl,de
	ldh a,[hCD]
	or a
	jr nz,Func_41E1
	xor a
	ldh [$FF1A],a
	push hl
	ld b,$10
	ld de,$FF30

Func_41DA:
	ld a,[hli]
	ld [de],a
	inc de
	dec b
	jr nz,Func_41DA
	pop hl

Func_41E1:
	ldh a,[$FFFF]
	or a
	jr nz,Func_41F1
	ld b,$10
	ld de,wD95C

Func_41EB:
	ld a,[hli]
	ld [de],a
	inc de
	dec b
	jr nz,Func_41EB

Func_41F1:
	pop hl
	pop de
	ld a,$80
	ldh [$FF1A],a

Func_41F7:
	jp Func_4100

Func_41FA:
	call Func_442B
	push de
	push hl
	inc hl
	inc hl
	ld a,[hl]
	cp $08
	call nz,Func_443F
	pop hl
	pop de
	jp Func_4100

Func_420C:
	push de
	push hl
	inc hl
	inc hl
	ld a,l
	ldh [hD1],a
	ld a,h
	ldh [hD2],a
	ld a,[hl]
	or a
	jr z,Func_423B

Func_421A:
	dec a
	ld b,a
	add a,a
	add a,b
	inc a
	ld e,a
	ld d,$00
	add hl,de
	dec [hl]
	jr z,Func_422F
	inc hl
	ld a,[hli]
	ld b,[hl]
	pop hl
	pop de
	ld e,a
	ld d,b
	jr Func_423D

Func_422F:
	ldh a,[hD1]
	ld l,a
	ldh a,[hD2]
	ld h,a
	dec [hl]
	pop hl
	pop de
	inc de
	jr Func_423D

Func_423B:
	pop hl
	pop de

Func_423D:
	jp Func_4100

Func_4240:
	inc de
	ld a,[de]
	inc de
	ld b,a
	ld a,[de]
	inc de
	ld e,b
	ld d,a
	jr Func_423D

Func_424A:
	push bc
	push hl
	inc de
	ld a,[de]
	inc de
	ld c,a
	ld a,[de]
	inc de
	ld b,a
	push bc
	ld bc,$001B
	add hl,bc
	ld a,[hl]
	cp $08
	jr z,Func_4268
	ld b,$03
	call Func_443F
	pop de
	pop hl
	pop bc
	jp Func_4100

Func_4268:
	pop bc
	pop hl
	pop bc
	jp Func_4100

Func_426E:
	push de
	push hl
	ld de,$001B
	add hl,de
	ld a,[hl]
	or a
	jr z,Func_423B
	dec [hl]
	jp Func_421A

Func_427C:
	call Func_442B
	push de
	push hl
	ld de,$0034
	add hl,de
	push hl
	ld l,b
	ld h,$00
	add hl,hl
	ld de,Data_46EF
	add hl,de
	pop de
	ld a,[hli]
	ld [de],a
	inc de
	ld a,[hl]
	ld [de],a
	pop hl
	pop de
	jp Func_4100

Func_4299:
	call Func_442B
	ld a,c
	cp $11
	jr nz,Func_42B5
	ldh a,[hCD]
	or a
	jr nz,Func_42AC
	ld a,b
	dec c
	call Func_4434
	inc c

Func_42AC:
	push de
	push hl
	ld de,VBlank_Handler
	add hl,de
	ld [hl],b
	pop hl
	pop de

Func_42B5:
	jp Func_4100

Func_42B8:
	call Func_442B
	ld a,c
	cp $20
	jr nz,Func_42B5
	push de
	push hl
	ld de,Func_003F
	add hl,de
	ld [hl],b
	pop hl
	pop de
	jr Func_42B5

Func_42CB:
	call Func_442B
	push af
	ld a,c
	cp $11
	jr z,Func_42E0
	cp $16
	jr z,Func_42E4
	cp $20
	jr z,Func_42E8
	ld b,$44
	jr Func_42EA

Func_42E0:
	ld b,$11
	jr Func_42EA

Func_42E4:
	ld b,$22
	jr Func_42EA

Func_42E8:
	ld b,$88

Func_42EA:
	pop af
	cp $01
	jr c,Func_42F9
	jr z,Func_42FC
	cp $03
	jr c,Func_4300
	ld a,$FF
	jr Func_4302

Func_42F9:
	xor a
	jr Func_4302

Func_42FC:
	ld a,$F0
	jr Func_4302

Func_4300:
	ld a,$0F

Func_4302:
	and b
	push de
	push hl
	ld de,$0041
	add hl,de
	push af
	ld a,b
	cpl
	ld [hli],a
	ld d,a
	pop af
	ld [hl],a
	ld e,a
	ldh a,[$FF25]
	and d
	or e
	ldh [$FF25],a
	pop hl
	pop de

Func_4319:
	jr Func_42B5

Func_431B:
	call Func_442B
	push de
	push hl
	ld de,$0043
	add hl,de
	ld [hl],a
	pop hl
	pop de
	jr Func_4319

Func_4329:
	xor a
	ldh [hCF],a
	ld a,[de]
	ldh [hCE],a
	cp $50
	jr c,Func_434B
	cp $A0
	jr c,Func_4349
	sub $A0
	dec hl
	dec hl
	ld [hld],a
	ld b,a
	inc de
	push de
	push hl
	ld de,$0046
	add hl,de
	ld a,[hl]
	pop hl
	pop de
	jr Func_4352

Func_4349:
	sub $50

Func_434B:
	dec hl
	dec hl
	ld [hld],a
	ld b,a
	inc de
	ld a,[de]
	inc de

Func_4352:
	dec a
	ld [hli],a
	inc hl
	ldh a,[hCE]
	cp $50
	jr c,Func_4363
	cp $A0
	jr nc,Func_4363
	ld a,[de]
	inc de
	ldh [hCF],a

Func_4363:
	ld [hl],e
	inc hl
	ld [hl],d
	inc hl
	ldh a,[hCD]
	or a
	ret nz
	ld a,b
	cp $49
	jp z,Func_440A
	push bc
	push hl
	ld de,Func_0033
	add hl,de
	ld e,[hl]
	inc hl
	ld d,[hl]
	inc hl
	ld a,[de]
	ld c,a
	inc de
	ld a,[de]
	ld b,a
	inc de
	ld [hl],e
	inc hl
	ld [hl],d
	inc hl
	ld [hl],c
	inc hl
	ld [hl],b
	pop hl
	pop bc
	ld a,[hl]
	inc c
	call Func_4434
	inc c
	ld a,c
	cp $20
	jr nc,Func_43FA
	ld de,Func_0039
	add hl,de
	push bc
	ld d,h
	ld e,l
	ld a,b
	dec a
	add a,a
	ld l,a
	ld h,$00
	ld bc,Data_4460
	add hl,bc
	ld c,[hl]
	inc hl
	ld b,[hl]
	inc hl
	ld a,[hli]
	ld h,[hl]
	ld l,a
	push hl
	ld a,l
	sub c
	ld l,a
	ld a,h
	sbc a,b
	ld h,a
	add hl,hl
	add hl,hl
	ld a,l
	ld [de],a
	inc de
	ld a,h
	ld [de],a
	inc de
	pop hl
	ldh a,[hCF]
	ld c,a
	ld b,$00
	bit 7,a
	jr z,Func_43C7
	dec b

Func_43C7:
	add hl,bc
	pop bc
	xor a
	ld [de],a
	inc de
	ld a,l
	ld [de],a
	inc de
	ld a,h
	ld [de],a
	ld a,c
	cp $1D
	jr nz,Func_43EC
	ld c,$1A
	xor a
	call Func_4434
	ld c,$1A
	ld a,$80
	call Func_4434
	ld c,$1C
	ld a,$20
	call Func_4434
	ld c,$1D

Func_43EC:
	ld a,l
	call Func_4434
	inc c
	ld a,$80
	or h
	call Func_4434
	jp Func_442A

Func_43FA:
	ldh a,[hCD]
	or a
	jr nz,Func_4409
	ld de,Func_003E
	add hl,de
	ld a,[hl]
	ld [$ff00+c],a
	ld a,$80
	inc c
	ld [$ff00+c],a

Func_4409:
	ret

Func_440A:
	ld a,c
	cp $1B
	jr z,Func_4424
	ld a,$08
	inc c
	call Func_4434
	inc c
	ld a,c
	cp $23
	jr z,Func_441E
	inc c
	jr Func_441E

Func_441E:
	ld a,$80
	call Func_4434
	ret

Func_4424:
	inc c
	xor a
	call Func_4434
	ret

Func_442A:
	ret

Func_442B:
	inc de
	ld a,[de]
	inc de
	ld [hl],d
	dec hl
	ld [hl],e
	inc hl
	ld b,a
	ret

Func_4434:
	push af
	ldh a,[hCD]
	or a
	jr nz,Func_443D
	pop af
	ld [$ff00+c],a
	ret

Func_443D:
	pop af
	ret

Func_443F:
	inc [hl]
	push de
	ld e,a
	add a,a
	add a,e
	add a,$01
	ld e,a
	ld d,$00
	add hl,de
	ld [hl],b
	pop de
	inc hl
	ld [hl],e
	inc hl
	ld [hl],d
	ret

; ---- data $4451-$7FFF ----
INCLUDE "src/data/data_4451.asm"
