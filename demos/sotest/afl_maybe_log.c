#include <stdio.h>
#include <unistd.h>
extern char* __afl_area_ptr;
extern __thread unsigned __afl_prev_loc;
void __afl_maybe_log(unsigned cur_pc) {
	unsigned hash = cur_pc ^ __afl_prev_loc; // calcualte current edge
	__afl_area_ptr[hash]++; // update shared memroy
	__afl_prev_loc = cur_pc >> 1; // update previouse edge
}
