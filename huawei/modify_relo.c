#include <bfd.h>
#include <stdio.h>
#include <stdlib.h>

static void
iter_section (bfd *abfd ATTRIBUTE_UNUSED, sec_ptr sec,
				     void *ignore ATTRIBUTE_UNUSED)
{
	  printf("current section name");
}

int main(int argc, char** argv) {
    if (argc < 2) {
	    printf("Usage %s <elf file>", argv[0]);
	    exit(-1);
	}
	bfd* ibfd = bfd_openr (argv[1], NULL);
	printf("input is %p\n", ibfd);
	printf("target is %s\n", bfd_get_target(ibfd));
	asection *sec = bfd_get_section_by_name(ibfd, ".rela.dyn");
	if (sec){
	      printf("HELLO, find .rela.dyn\n");
	}
	bfd_map_over_sections(ibfd, iter_section, 0);
}
