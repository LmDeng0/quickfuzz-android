	.arch armv8-a
	.file	"heap.c"
	.text
	.section	.rodata
	.align	5
.LC0:
	.string	"LOG: Incoming out of bounds access"
	.zero	61
	.text
	.align	2
	.global	oob
	.type	oob, %function
oob:
.LASANPC5:
.LFB5:
	.cfi_startproc
	stp	x29, x30, [sp, -32]!
	.cfi_def_cfa_offset 32
	.cfi_offset 29, -32
	.cfi_offset 30, -24
	add	x29, sp, 0
	.cfi_def_cfa_register 29
	adrp	x0, .LC0
	add	x0, x0, :lo12:.LC0
	bl	puts
	mov	x0, 15
	bl	malloc
	str	x0, [x29, 24]
	ldr	x0, [x29, 24]
	add	x2, x0, 15
	mov	x0, x2
	lsr	x3, x0, 3
	mov	x1, 68719476736
	add	x1, x3, x1
	ldrsb	w1, [x1]
	cmp	w1, 0
	cset	w3, ne
	and	w3, w3, 255
	and	x4, x0, 7
	sxtb	w4, w4
	cmp	w4, w1
	cset	w1, ge
	and	w1, w1, 255
	and	w1, w3, w1
	and	w1, w1, 255
	cmp	w1, 0
	beq	.L2
	bl	__asan_report_store1
.L2:
	mov	w0, 42
	strb	w0, [x2]
	ldr	x0, [x29, 24]
	bl	free
	nop
	ldp	x29, x30, [sp], 32
	.cfi_restore 30
	.cfi_restore 29
	.cfi_def_cfa 31, 0
	ret
	.cfi_endproc
.LFE5:
	.size	oob, .-oob
	.section	.rodata
	.align	5
.LC1:
	.string	"LOG: Incoming use after free"
	.zero	35
	.text
	.align	2
	.global	uaf
	.type	uaf, %function
uaf:
.LASANPC6:
.LFB6:
	.cfi_startproc
	stp	x29, x30, [sp, -32]!
	.cfi_def_cfa_offset 32
	.cfi_offset 29, -32
	.cfi_offset 30, -24
	add	x29, sp, 0
	.cfi_def_cfa_register 29
	adrp	x0, .LC1
	add	x0, x0, :lo12:.LC1
	bl	puts
	mov	x0, 15
	bl	malloc
	str	x0, [x29, 24]
	ldr	x0, [x29, 24]
	bl	free
	ldr	x0, [x29, 24]
	add	x2, x0, 7
	mov	x0, x2
	lsr	x3, x0, 3
	mov	x1, 68719476736
	add	x1, x3, x1
	ldrsb	w1, [x1]
	cmp	w1, 0
	cset	w3, ne
	and	w3, w3, 255
	and	x4, x0, 7
	sxtb	w4, w4
	cmp	w4, w1
	cset	w1, ge
	and	w1, w1, 255
	and	w1, w3, w1
	and	w1, w1, 255
	cmp	w1, 0
	beq	.L4
	bl	__asan_report_store1
.L4:
	mov	w0, 42
	strb	w0, [x2]
	nop
	ldp	x29, x30, [sp], 32
	.cfi_restore 30
	.cfi_restore 29
	.cfi_def_cfa 31, 0
	ret
	.cfi_endproc
.LFE6:
	.size	uaf, .-uaf
	.section	.rodata
	.align	5
.LC2:
	.string	"%s {1|2}\n1: Out of bounds heap access\n2: Use after free heap access\n"
	.zero	59
	.text
	.align	2
	.global	usage
	.type	usage, %function
usage:
.LASANPC7:
.LFB7:
	.cfi_startproc
	stp	x29, x30, [sp, -32]!
	.cfi_def_cfa_offset 32
	.cfi_offset 29, -32
	.cfi_offset 30, -24
	add	x29, sp, 0
	.cfi_def_cfa_register 29
	str	x0, [x29, 24]
	adrp	x0, .LC2
	add	x0, x0, :lo12:.LC2
	ldr	x1, [x29, 24]
	bl	printf
	bl	__asan_handle_no_return
	mov	w0, -1
	bl	exit
	.cfi_endproc
.LFE7:
	.size	usage, .-usage
	.align	2
	.global	main
	.type	main, %function
main:
.LASANPC8:
.LFB8:
	.cfi_startproc
	stp	x29, x30, [sp, -32]!
	.cfi_def_cfa_offset 32
	.cfi_offset 29, -32
	.cfi_offset 30, -24
	add	x29, sp, 0
	.cfi_def_cfa_register 29
	str	w0, [x29, 28]
	str	x1, [x29, 16]
	ldr	w0, [x29, 28]
	cmp	w0, 2
	beq	.L7
	ldr	x0, [x29, 16]
	lsr	x2, x0, 3
	mov	x1, 68719476736
	add	x1, x2, x1
	ldrsb	w1, [x1]
	cmp	w1, 0
	beq	.L8
	bl	__asan_report_load8
.L8:
	ldr	x0, [x29, 16]
	ldr	x0, [x0]
	bl	usage
.L7:
	ldr	x0, [x29, 16]
	add	x0, x0, 8
	mov	x3, x0
	lsr	x2, x3, 3
	mov	x1, 68719476736
	add	x1, x2, x1
	ldrsb	w1, [x1]
	cmp	w1, 0
	beq	.L9
	mov	x0, x3
	bl	__asan_report_load8
.L9:
	ldr	x0, [x0]
	bl	atoi
	cmp	w0, 1
	beq	.L11
	cmp	w0, 2
	beq	.L12
	b	.L16
.L11:
	bl	oob
	b	.L13
.L12:
	bl	uaf
	b	.L13
.L16:
	ldr	x0, [x29, 16]
	lsr	x2, x0, 3
	mov	x1, 68719476736
	add	x1, x2, x1
	ldrsb	w1, [x1]
	cmp	w1, 0
	beq	.L14
	bl	__asan_report_load8
.L14:
	ldr	x0, [x29, 16]
	ldr	x0, [x0]
	bl	usage
.L13:
	mov	w0, 0
	ldp	x29, x30, [sp], 32
	.cfi_restore 30
	.cfi_restore 29
	.cfi_def_cfa 31, 0
	ret
	.cfi_endproc
.LFE8:
	.size	main, .-main
	.section	.rodata
	.align	3
.LC3:
	.string	"*.LC0"
	.align	3
.LC4:
	.string	"heap.c"
	.align	3
.LC5:
	.string	"*.LC1"
	.align	3
.LC6:
	.string	"*.LC2"
	.section	.data.rel.local,"aw",@progbits
	.align	3
	.type	.LASAN0, %object
	.size	.LASAN0, 192
.LASAN0:
	.xword	.LC0
	.xword	35
	.xword	96
	.xword	.LC3
	.xword	.LC4
	.xword	0
	.xword	0
	.xword	0
	.xword	.LC1
	.xword	29
	.xword	64
	.xword	.LC5
	.xword	.LC4
	.xword	0
	.xword	0
	.xword	0
	.xword	.LC2
	.xword	69
	.xword	128
	.xword	.LC6
	.xword	.LC4
	.xword	0
	.xword	0
	.xword	0
	.text
	.align	2
	.type	_GLOBAL__sub_D_00099_0_oob, %function
_GLOBAL__sub_D_00099_0_oob:
.LFB9:
	.cfi_startproc
	stp	x29, x30, [sp, -16]!
	.cfi_def_cfa_offset 16
	.cfi_offset 29, -16
	.cfi_offset 30, -8
	add	x29, sp, 0
	.cfi_def_cfa_register 29
	adrp	x0, .LASAN0
	add	x0, x0, :lo12:.LASAN0
	mov	x1, 3
	bl	__asan_unregister_globals
	ldp	x29, x30, [sp], 16
	.cfi_restore 30
	.cfi_restore 29
	.cfi_def_cfa 31, 0
	ret
	.cfi_endproc
.LFE9:
	.size	_GLOBAL__sub_D_00099_0_oob, .-_GLOBAL__sub_D_00099_0_oob
	.section	.fini_array.00099,"aw"
	.align	3
	.xword	_GLOBAL__sub_D_00099_0_oob
	.text
	.align	2
	.type	_GLOBAL__sub_I_00099_1_oob, %function
_GLOBAL__sub_I_00099_1_oob:
.LFB10:
	.cfi_startproc
	stp	x29, x30, [sp, -16]!
	.cfi_def_cfa_offset 16
	.cfi_offset 29, -16
	.cfi_offset 30, -8
	add	x29, sp, 0
	.cfi_def_cfa_register 29
	bl	__asan_init
	bl	__asan_version_mismatch_check_v8
	adrp	x0, .LASAN0
	add	x0, x0, :lo12:.LASAN0
	mov	x1, 3
	bl	__asan_register_globals
	ldp	x29, x30, [sp], 16
	.cfi_restore 30
	.cfi_restore 29
	.cfi_def_cfa 31, 0
	ret
	.cfi_endproc
.LFE10:
	.size	_GLOBAL__sub_I_00099_1_oob, .-_GLOBAL__sub_I_00099_1_oob
	.section	.init_array.00099,"aw"
	.align	3
	.xword	_GLOBAL__sub_I_00099_1_oob
	.ident	"GCC: (Ubuntu/Linaro 7.5.0-3ubuntu1~18.04) 7.5.0"
	.section	.note.GNU-stack,"",@progbits
