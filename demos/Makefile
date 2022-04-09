# Run `make` in Python venv
# `source path/to/venv/bin/activate` and then run `make` `make heaptest` `make stacktest`
#
#
#
CC=gcc
AFLCC=afl-gcc
AFL_USE_ARM=1
AFL_AS_FORCE_INSTRUMENT=1
OPT=-O0 -ggdb -Wall -Wpedantic -Wextra -fPIC -fPIE -pie

all: heap stack afltest heap.asan stack.asan afltest.asan.afl

heap: heap.c
	${CC} ${OPT} heap.c -o heap

heap.asan: heap
	quickfuzz -m asan ./heap ./heap.asan.s
	${CC} heap.asan.s -lasan -o heap.asan

.PHONY=heaptest
heaptest: heap heap.asan
	./heap 1
	./heap.asan 1; true
	./heap 2
	./heap.asan 2; true

stack: stack.c
	${CC} ${OPT} stack.c -o stack

stack.asan: stack
	quickfuzz -m asan ./stack ./stack.asan.s
	${CC} stack.asan.s -lasan -o stack.asan

.PHONY=stacktest
stacktest: stack stack.asan
	./stack 1
	./stack.asan 1; true
	./stack 2
	./stack.asan 2; true

afltest: afltest.c
	${CC} ${OPT} afltest.c -o afltest

afltest.asan.afl: afltest
	quickfuzz -m asan ./afltest ./afltest.asan.s
	${CC} afltest.asan.s -lasan -o afltest.asan
	${AFLCC} afltest.asan.s -lasan -o afltest.asan.afl

.PHONY=test
test: heaptest stacktest

.PHONY=clean
clean:
	rm -f heap heap.asan heap.asan.s heap.asan.analysis_cache stack stack.asan stack.asan.s stack.asan.analysis_cache afltest.asan.s afltest.asan afltest.asan.afl afltest
