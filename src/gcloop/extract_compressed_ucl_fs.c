/* Extracts a filesystem back from a compressed fs file */
#include <stdio.h>
#include <netinet/in.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include "compressed_loop.h"
#include <ucl/ucl.h>

struct compressed_block
{
	size_t size;
	void *data;
};

/*--------------------------*/
#ifndef _COMPRESSED_LOOP_H
#define _COMPRESSED_LOOP_H

#define CLOOP_HEADROOM 128

struct cloop_head
{
        char preamble[CLOOP_HEADROOM];
        u_int32_t block_size;
        u_int32_t num_blocks;
};

#define CLOOP_VERSION	"0.99"

#endif /*_COMPRESSED_LOOP_H*/
/*-------------------------------*/

int Version(char* argv) {
fprintf(stderr, "%s Version " CLOOP_VERSION "\n", argv);
exit(1);
return 1;
}

int Usage(char* argv) {
fprintf(stderr, "%s : extracts gcloop image data to stdout\n", argv);
fprintf(stderr, "Usage: %s infile\n", argv);
exit(1);
return 1;
}

int main(int argc, char *argv[])
{
	int handle;
	struct cloop_head head;
	unsigned int i;
	unsigned char *buffer, *clear_buffer;
	int optionchar;
	while ((optionchar=getopt(argc,argv,"V"))!=-1) {
		switch (optionchar) {
			case 'V':
				Version(argv[0]);
				break;
			default:
				printf ("Unknown option: %c\n",optionchar);
				Usage(argv[0]);
				break;
		}
	}

	if (argc != 2) {
		Usage(argv[0]);
	}
	

	handle = open(argv[1], O_RDONLY);
	if (handle < 0) {
		perror("Opening compressed file\n");
		exit(1);
	}

	if (read(handle, &head, sizeof(head)) != sizeof(head)) {
		perror("Reading compressed file header\n");
		exit(1);
	}
#ifdef INDEX_NEW
        buffer = malloc(ntohl(head.block_size));
#else
        buffer = malloc(ntohl(head.block_size) + 
			ntohl(head.block_size)/8 +256);
#endif

	clear_buffer = malloc(ntohl(head.block_size));
	fprintf(stderr, "%u blocks of size %u. Preamble:\n%s\n", 
		ntohl(head.num_blocks), ntohl(head.block_size), head.preamble);

	for (i = 0; i < ntohl(head.num_blocks); i++) {
		int currpos;
		unsigned int destlen = ntohl(head.block_size);
		u_int32_t offset[2], size;

		read(handle, &offset, 2*sizeof(u_int32_t));
                lseek(handle, -sizeof(u_int32_t), SEEK_CUR);
                
		currpos = lseek(handle, 0, SEEK_CUR);
		if (lseek(handle, ntohl(offset[0]), SEEK_SET) < 0) {
			fprintf(stderr, "lseek to %u: %s\n",
				ntohl(offset[0]), strerror(errno));
			exit(1);
		}
                
                size=ntohl(offset[1])-ntohl(offset[0]);
		if (size > ntohl(head.block_size) + ntohl(head.block_size)/8
		    + 256) {
			fprintf(stderr, 
				"Size %u for block %u (offset %u) too big\n",
				size, i, ntohl(offset[0]));
			exit(1);
		}
		read(handle, buffer, size);
		if (lseek(handle, currpos, SEEK_SET) < 0) {
			perror("seeking");
			exit(1);
		}

		fprintf(stderr, "Block %u pos %i length %u => %u\n",
			i, ntohl(offset[0]), size, destlen);
/*		if (i == 3) {
			fprintf(stderr,
				"Block head:%02X%02X%02X%02X%02X%02X%02X%02X\n",
				buffer[0],
				buffer[1],
				buffer[2],
				buffer[3],
				buffer[4],
				buffer[5],
				buffer[6],
				buffer[7]);
			fprintf(stderr,
				"Block tail:%02X%02X%02X%02X%02X%02X%02X%02X\n",
				buffer[3063],
				buffer[3064],
				buffer[3065],
				buffer[3066],
				buffer[3067],
				buffer[3068],
				buffer[3069],
				buffer[3070]);
		}*/
		/* lu_zero :: ucl decompress*/
#ifdef INDEX_NEW
		if (size==0)
		 {
		 memset(clear_buffer,0,destlen);
		 }
		 else if (size>destlen)
                 {
                 fprintf(stderr, "Uncomp: corrupted or old index entry at %u\n", i);
		 }else if (size==destlen)
		 {
		  memcpy(clear_buffer,buffer,size);
		 }
		else
#endif
		switch (ucl_nrv2e_decompress_safe_8(buffer, size,
				clear_buffer, &destlen,NULL)) {
		case UCL_E_OK:
			break;

		case UCL_E_ERROR:
			fprintf(stderr, "Uncomp: oom block %u\n", i);
			exit(1);

		case UCL_E_OUT_OF_MEMORY:
			fprintf(stderr, "Uncomp: not enough out room %u\n", i);
			exit(1);

		case UCL_E_EOF_NOT_FOUND:
			fprintf(stderr, "Uncomp: input corrupt, EOF not found %u\n", i);
			exit(1);
		
		case UCL_E_INPUT_NOT_CONSUMED:
			fprintf(stderr, "Uncomp: input corrupt, not consumed %u\n", i);
			exit(1);

		case UCL_E_LOOKBEHIND_OVERRUN:
	                fprintf(stderr, "Uncomp: input corrupt, lookbehind overrun %u\n", i);
	        	exit(1);
		default:
			fprintf(stderr, "Uncomp: unknown error %u\n", i);
			exit(1);
		}
		
		if (destlen != ntohl(head.block_size)) {
			fprintf(stderr, "Uncomp: bad len %u (%u not %u)\n", i,
				destlen, ntohl(head.block_size));
			exit(1);
		}
		write(STDOUT_FILENO, clear_buffer, ntohl(head.block_size));
	}
	return 0;
}
