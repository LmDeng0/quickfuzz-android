#include <stdio.h>

void f(){
	printf("function f\n");
}

void g(){
	printf("function g\n");
}

int main(){
	void (*fptr) () = &f;
	fptr();
	fptr = &g;
	fptr();
	//fptr = 0;
	fptr = &f + 1;
	fptr();
	return 0;
}
