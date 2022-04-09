#include <stdio.h>
#include <stdlib.h>

void vul(char* p) {
        p[16] = 'a';
}

void normal(char* p) {
        p[15] = 'a';
}

int main() {
        int c;
        char* buf = malloc(16);
        scanf("%d", &c);

        if (c > 1024) {
                vul(buf);
        } else {
                normal(buf);
        }
        free(buf);
}
