	.arch armv8-a
	.file	"heapso.c"
	.text
	.section	.rodata
	.align	3
.LC0:
	.string	"LOG: Incoming out of bounds access"
	.text
	.align	2
	.global	oob
	.type	oob, %function
oob:
	stp	x29, x30, [sp, -32]!
	add	x29, sp, 0
	adrp	x0, .LC0
	add	x0, x0, :lo12:.LC0
	bl	puts
	mov	x0, 15
	bl	malloc
	str	x0, [x29, 24]
	ldr	x0, [x29, 24]
	add	x0, x0, 15
	mov	w1, 42
	strb	w1, [x0]
	ldr	x0, [x29, 24]
	bl	free
	nop
	ldp	x29, x30, [sp], 32
	ret
	.size	oob, .-oob
	.section	.rodata
	.align	3
.LC1:
	.string	"LOG: Incoming use after free"
	.text
	.align	2
	.global	uaf
	.type	uaf, %function
uaf:
	stp	x29, x30, [sp, -32]!
	add	x29, sp, 0
	adrp	x0, .LC1
	add	x0, x0, :lo12:.LC1
	bl	puts
	mov	x0, 15
	bl	malloc
	str	x0, [x29, 24]
	ldr	x0, [x29, 24]
	bl	free
	ldr	x0, [x29, 24]
	add	x0, x0, 7
	mov	w1, 42
	strb	w1, [x0]
	nop
	ldp	x29, x30, [sp], 32
	ret
	.size	uaf, .-uaf
	.section	.rodata
	.align	3
.LC2:
	.string	"%s {1|2}\n1: Out of bounds heap access\n2: Use after free heap access\n"
	.text
	.align	2
	.global	usage
	.type	usage, %function
usage:
	stp	x29, x30, [sp, -32]!
	add	x29, sp, 0
	str	x0, [x29, 24]
	adrp	x0, .LC2
	add	x0, x0, :lo12:.LC2
	ldr	x1, [x29, 24]
	bl	printf
	mov	w0, -1
	bl	exit
	.size	usage, .-usage
	.ident	"GCC: (Ubuntu/Linaro 7.5.0-3ubuntu1~18.04) 7.5.0"
	.section	.note.GNU-stack,"",@progbits
