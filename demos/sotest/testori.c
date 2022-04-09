#include <stdio.h>
#include <stdlib.h>
#include "heapso.h"

int main(int argc, char* argv[]) {
	if (argc != 2) usage(argv[0]);
	switch (atoi(argv[1])) {
		case 1:
			oob();
			break;
		case 2:
			uaf();
			break;
		default:
			usage(argv[0]);
	}
	return 0;
}
