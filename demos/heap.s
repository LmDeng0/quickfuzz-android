	.text
	.file	"heap.c"
	.globl	oob                     // -- Begin function oob
	.p2align	2
	.type	oob,@function
oob:                                    // @oob
// %bb.0:
	sub	sp, sp, #48             // =48
	stp	x29, x30, [sp, #32]     // 8-byte Folded Spill
	add	x29, sp, #32            // =32
	adrp	x8, .L.str
	add	x8, x8, :lo12:.L.str
	orr	x0, xzr, #0xf
	mov	w9, #42
	str	x0, [sp, #16]           // 8-byte Folded Spill
	mov	x0, x8
	str	w9, [sp, #12]           // 4-byte Folded Spill
	bl	printf
	ldr	x8, [sp, #16]           // 8-byte Folded Reload
	mov	x0, x8
	bl	malloc
	stur	x0, [x29, #-8]
	ldur	x8, [x29, #-8]
	ldr	w9, [sp, #12]           // 4-byte Folded Reload
	strb	w9, [x8, #15]
	ldur	x0, [x29, #-8]
	bl	free
	ldp	x29, x30, [sp, #32]     // 8-byte Folded Reload
	add	sp, sp, #48             // =48
	ret
.Lfunc_end0:
	.size	oob, .Lfunc_end0-oob
                                        // -- End function
	.globl	uaf                     // -- Begin function uaf
	.p2align	2
	.type	uaf,@function
uaf:                                    // @uaf
// %bb.0:
	sub	sp, sp, #48             // =48
	stp	x29, x30, [sp, #32]     // 8-byte Folded Spill
	add	x29, sp, #32            // =32
	adrp	x8, .L.str.1
	add	x8, x8, :lo12:.L.str.1
	orr	x0, xzr, #0xf
	mov	w9, #42
	str	x0, [sp, #16]           // 8-byte Folded Spill
	mov	x0, x8
	str	w9, [sp, #12]           // 4-byte Folded Spill
	bl	printf
	ldr	x8, [sp, #16]           // 8-byte Folded Reload
	mov	x0, x8
	bl	malloc
	stur	x0, [x29, #-8]
	ldur	x0, [x29, #-8]
	bl	free
	ldur	x8, [x29, #-8]
	ldr	w9, [sp, #12]           // 4-byte Folded Reload
	strb	w9, [x8, #7]
	ldp	x29, x30, [sp, #32]     // 8-byte Folded Reload
	add	sp, sp, #48             // =48
	ret
.Lfunc_end1:
	.size	uaf, .Lfunc_end1-uaf
                                        // -- End function
	.globl	usage                   // -- Begin function usage
	.p2align	2
	.type	usage,@function
usage:                                  // @usage
// %bb.0:
	sub	sp, sp, #32             // =32
	stp	x29, x30, [sp, #16]     // 8-byte Folded Spill
	add	x29, sp, #16            // =16
	adrp	x8, .L.str.2
	add	x8, x8, :lo12:.L.str.2
	mov	w9, #-1
	str	x0, [sp, #8]
	ldr	x1, [sp, #8]
	mov	x0, x8
	str	w9, [sp, #4]            // 4-byte Folded Spill
	bl	printf
	ldr	w9, [sp, #4]            // 4-byte Folded Reload
	mov	w0, w9
	bl	exit
.Lfunc_end2:
	.size	usage, .Lfunc_end2-usage
                                        // -- End function
	.globl	main                    // -- Begin function main
	.p2align	2
	.type	main,@function
main:                                   // @main
// %bb.0:
	sub	sp, sp, #48             // =48
	stp	x29, x30, [sp, #32]     // 8-byte Folded Spill
	add	x29, sp, #32            // =32
	orr	w8, wzr, #0x2
	stur	wzr, [x29, #-4]
	stur	w0, [x29, #-8]
	str	x1, [sp, #16]
	ldur	w0, [x29, #-8]
	cmp	w0, w8
	cset	w8, ne
	tbnz	w8, #0, .LBB3_1
	b	.LBB3_2
.LBB3_1:
	ldr	x8, [sp, #16]
	ldr	x0, [x8]
	bl	usage
.LBB3_2:
	orr	w8, wzr, #0x1
	ldr	x9, [sp, #16]
	ldr	x0, [x9, #8]
	str	w8, [sp, #12]           // 4-byte Folded Spill
	bl	atoi
	ldr	w8, [sp, #12]           // 4-byte Folded Reload
	cmp	w8, w0
	cset	w10, eq
	str	w0, [sp, #8]            // 4-byte Folded Spill
	tbnz	w10, #0, .LBB3_5
	b	.LBB3_3
.LBB3_3:
	orr	w8, wzr, #0x2
	ldr	w9, [sp, #8]            // 4-byte Folded Reload
	cmp	w8, w9
	cset	w8, eq
	tbnz	w8, #0, .LBB3_6
	b	.LBB3_4
.LBB3_4:
	b	.LBB3_7
.LBB3_5:
	bl	oob
	b	.LBB3_8
.LBB3_6:
	bl	uaf
	b	.LBB3_8
.LBB3_7:
	ldr	x8, [sp, #16]
	ldr	x0, [x8]
	bl	usage
.LBB3_8:
	mov	w0, #0
	ldp	x29, x30, [sp, #32]     // 8-byte Folded Reload
	add	sp, sp, #48             // =48
	ret
.Lfunc_end3:
	.size	main, .Lfunc_end3-main
                                        // -- End function
	.type	.L.str,@object          // @.str
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str:
	.asciz	"LOG: Incoming out of bounds access\n"
	.size	.L.str, 36

	.type	.L.str.1,@object        // @.str.1
.L.str.1:
	.asciz	"LOG: Incoming use after free\n"
	.size	.L.str.1, 30

	.type	.L.str.2,@object        // @.str.2
.L.str.2:
	.asciz	"%s {1|2}\n1: Out of bounds heap access\n2: Use after free heap access\n"
	.size	.L.str.2, 69


	.ident	"clang version 6.0.0-1ubuntu2 (tags/RELEASE_600/final)"
	.section	".note.GNU-stack","",@progbits
