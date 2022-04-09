#include <stdio.h>
#include <stdlib.h>
#include "heapso.h"

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
