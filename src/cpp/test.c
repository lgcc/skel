#include <errno.h>
#include <stdio.h>
#include <string.h>


void check_compiler() {
#ifndef __ASSEMBLER__
	printf("Undefined __ASSEMBLER__\n");
#else
	printf("Defined __ASSEMBLER__\n");
#endif

#ifndef __LIBC
	printf("Undefined __LIBC\n");
#else
	printf("Defined __LIBC\n");
#endif

#ifndef _LIBC_REENTRANT
	printf("Undefined _LIBC_REENTRANT\n");
#else
	printf("Defined _LIBC_REENTRANT\n");
#endif
}


int main() {

	int errno;

	errno = EBADF;

	check_compiler();

	fprintf(stderr, "errno: %d, msg: %s\n", errno, strerror(errno));
	perror("perror msg");

	return 0;
}