#include <stdio.h>
#include <stdlib.h>

#define SIZE 15

void oob() {
	printf("LOG: Incoming out of bounds access\n");
	char *buf = (char*)malloc(SIZE);
	buf[SIZE] = 42; // boom
	free(buf);	
}

void uaf() {
	printf("LOG: Incoming use after free\n");
	char *buf = (char*)malloc(SIZE);
	free(buf);
	buf[SIZE/2] = 42; // boom
}

void usage(char *prog) {
	printf("%s {1|2}\n1: Out of bounds heap access\n"
		"2: Use after free heap access\n", prog);
	exit(-1);
}
int main(int argc, char* argv[]) {
	int i;
	scanf("%d",&i);
	if (i<10) 
	{		
		oob();
	}
	else if (50>i>10)
	{
			uaf();
	}
		else if (100>i>50)
	{
			oob();
	}
		else if (1000>i>100)
	{
			uaf();
	}
		else if (5000>i>1000)
	{
			oob();
	}
		else if (5000>i>1000)
	{
			uaf();
	}
		else if (5000>i>1000)
	{
			uaf();
	}
		else if (10000>i>5000)
	{
			uaf();
	}
		else if (5000>i>1000)
	{
			oob();
	}
		else if (5000>i>1000)
	{
			uaf();
	}
		
	else
	{
		usage(argv[0]);
	}
			

	return 0;
}

