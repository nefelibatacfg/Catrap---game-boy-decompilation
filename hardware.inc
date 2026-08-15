; ============================================================
; Game Boy hardware register definitions
; ============================================================

; ---- Joypad ----
DEF rP1 EQU $FF00 ; joypad: P15-P10

; ---- Serial ----
DEF rSB EQU $FF01 ; serial transfer data
DEF rSC EQU $FF02 ; serial transfer control

; ---- Timer ----
DEF rDIV EQU $FF04 ; divider
DEF rTIMA EQU $FF05 ; timer counter
DEF rTMA EQU $FF06 ; timer modulo
DEF rTAC EQU $FF07 ; timer control

; ---- Interrupt flags ----
DEF rIF EQU $FF0F ; interrupt flag

; ---- Sound (NRxx) ----
DEF rNR10 EQU $FF10 ; channel 1 sweep
DEF rNR11 EQU $FF11 ; channel 1 duty/length
DEF rNR12 EQU $FF12 ; channel 1 volume/envelope
DEF rNR13 EQU $FF13 ; channel 1 frequency low
DEF rNR14 EQU $FF14 ; channel 1 frequency high/trigger
DEF rNR21 EQU $FF16 ; channel 2 duty/length
DEF rNR22 EQU $FF17 ; channel 2 volume/envelope
DEF rNR23 EQU $FF18 ; channel 2 frequency low
DEF rNR24 EQU $FF19 ; channel 2 frequency high/trigger
DEF rNR30 EQU $FF1A ; channel 3 sound on/off
DEF rNR31 EQU $FF1B ; channel 3 length
DEF rNR32 EQU $FF1C ; channel 3 volume
DEF rNR33 EQU $FF1D ; channel 3 frequency low
DEF rNR34 EQU $FF1E ; channel 3 frequency high/trigger
DEF rNR41 EQU $FF20 ; channel 4 length
DEF rNR42 EQU $FF21 ; channel 4 volume/envelope
DEF rNR43 EQU $FF22 ; channel 4 polynomial counter
DEF rNR44 EQU $FF23 ; channel 4 counter/trigger
DEF rNR50 EQU $FF24 ; volume control (left/right)
DEF rNR51 EQU $FF25 ; channel enable (left/right)
DEF rNR52 EQU $FF26 ; sound on/off

; ---- Wave RAM ($FF30-$FF3F) ----
DEF rWAVExx EQU $FF30

; ---- LCD ----
DEF rLCDC EQU $FF40 ; LCD control
DEF rSTAT EQU $FF41 ; LCD status
DEF rSCY EQU $FF42 ; scroll Y
DEF rSCX EQU $FF43 ; scroll X
DEF rLY EQU $FF44 ; current scanline
DEF rLYC EQU $FF45 ; scanline compare
DEF rDMA EQU $FF46 ; OAM DMA source
DEF rBGP EQU $FF47 ; background palette
DEF rOBP0 EQU $FF48 ; object palette 0
DEF rOBP1 EQU $FF49 ; object palette 1
DEF rWY EQU $FF4A ; window Y
DEF rWX EQU $FF4B ; window X

; ---- Interrupt enable ----
DEF rIE EQU $FFFF ; interrupt enable

; ---- Interrupt constants ----
DEF INT_VBLANK EQU $01
DEF INT_LCD EQU $02
DEF INT_TIMER EQU $04
DEF INT_SERIAL EQU $08
DEF INT_JOYPAD EQU $10
