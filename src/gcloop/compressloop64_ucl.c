/* Creates a compressed image, given a file as an argument.
 * (c)1999 Paul `Rusty' Russell.  GPL.
 *
 * CVS version: $Source: /var/cvsroot/gentoo/src/gcloop/compressloop64_ucl.c,v $
 * Version $Id: compressloop64_ucl.c,v 1.1 2004/06/24 19:09:19 lu_zero Exp $
 *
 * CHANGELOG:
 * * Fri Apr 11 2003 Luca Barbato
   - ucl + other changes.
 * * Thu Dec 19 2002 [VS]
   A whole lot of cleaning up, adding options, and generally making it a
   useful utility instead of just a pile of C statements:
   - Added help (a "Usage()" function)
   - added options with "getopt()"
   - explicitly guessed blocks, counted them and compared these
   - put writing head and index to the end of the program, so the head
     can use the correct number of blocks.
     the additions are (c) 2002 Valentijn Sessink. GPL applies (see above).
     Todo: add GPL info on top of this file.
 * * Wed Dec 18 2002 [VS] added CVS versioning info
 * * Mon Dec 16 2002 Valentijn Sessink <valentyn@openoffice.nl> [VS]
 *   total rewrite. Previous version did a malloc() to build an
 *   on the fly disk image. Which meant 600M malloc()s.
 *   I fixed this with a rather trivial open(). However, this
 *   means that you can no more use compressloop to compress
 *   to stdout.
 * * Sat Sep 29 2001 Klaus Knopper <knopper@knopper.net>
 * - changed compression to Z_BEST_COMPRESSION,
 * * Sat Jun 17 2000 Klaus Knopper <knopper@knopper.net>
 * - Support for reading file from stdin,
 * - Changed Preamble.
 * * Sat Jul 28 2001 Klaus Knopper <knopper@knopper.net>
 * - cleanup and gcc 2.96 / glibc checking
 */
#include <stdio.h>
#include <netinet/in.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include "compressed_loop.h"
#include <ucl/ucl.h>
#include <errno.h>

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

struct cloop_head64
{
	char preamble[CLOOP_HEADROOM];
	u_int32_t block_size;
	u_int64_t num_blocks;
};

#define CLOOP_VERSION	"1.00"

#endif /*_COMPRESSED_LOOP_H*/
/*-------------------------------*/

#define MAX_KMALLOC_SIZE 1L<<17

#define CLOOP_PREAMBLE	"#gcloop nrv2e "  CLOOP_VERSION

#define CLOOP_PREAMBLE32 GCLOOP_PREAMBLE " i32"

#define CLOOP_PREAMBLE64 GCLOOP_PREAMBLE " i64"

/* #define CLOOP_PREAMBLE "#!/bin/sh\n" "insmod cloop.o file=$0 && mount -r -t iso9660 /dev/cloop $1\n" "exit $?\n"
*/
/* defaults */
#define IMAGESIZE 2000000000
#define BLOCKSIZE 131072

int Usage(char* argv) {
fprintf(stderr, "Usage: %s [options] infile outfile\n", argv);
fprintf(stderr, "Options:\n");
fprintf(stderr, "\t-b blocksize\t\tSet block size (multiple of 512 bytes)\n");
fprintf(stderr, "\t-c compression\t\tSet compression (0-10, 0 is fastest, 10 is best)\n");
fprintf(stderr, "\t-i imagesize\t\tSet input image size (in bytes) if it cannot be determined\n");
fprintf(stderr, "\t-I forced-imagesize\tForce input image size (in bytes), even if determined\n");
fprintf(stderr, "\t-v \tBe more verbose (accumulates)\n");
fprintf(stderr, "\t-V \tPrint version information and exit\n");
fprintf(stderr, "\t-l \tUses 64bit integers for the index, the default is 32bit\n");
/*
fprintf(stderr, "\t-t tempfile\tstore data in temporary file\n");
 */
exit(1);
return 1;
} /* Usage() */

int Version(char* argv) {
fprintf(stderr, "%s Version " CLOOP_VERSION " Preamble:" CLOOP_PREAMBLE "\n", argv);
exit(1);
return 1;
}

void Errexit(char* error,char* name) {
	fprintf(stderr, error);
	Usage(name);
}

int main(int argc, char **argv) {
	int in,out;
	unsigned long blocksize=BLOCKSIZE;
	struct stat filestat;
	u_int32_t tmp;
	u_int64_t tmp64;
	u_int64_t indexsize;
	struct cloop_head head;
	unsigned long guessedblocks, countedblocks=0;
	u_int32_t *pointerblock;
	u_int64_t *pointerblock64;
	u_int64_t position;
	u_int64_t  i=0;
	unsigned int last=0;
	unsigned long maxlen;
	char *compressed, *uncompressed;
	int optionchar, index_lenght=32;
	unsigned int statz=0,statn=0,stato=0;
	u_int64_t imagesize=IMAGESIZE;
	unsigned int compression=10;
	unsigned int forceimagesize=0,forceindex=0,verbose=0,determinedimagesize=0;
	//struct ucl_compress_config_t conf=
	//{
    	//	/*bb_endian=*/-1,
    	//	/*bb_size=*/32,
	//	/*max_offset=*/128*1024-1,//to be variable
    	//	/*max_match=*/128*1024-1,
    	//	/*s_level=*/-1,
    	//	/*h_level=*/-1,
    	//	/*p_level=*/-1,
    	//	/*c_flags=*/-1,
	//	/*m_size=*/-1
	//};


	if (ucl_init()!= UCL_E_OK)
	{
   	Errexit("ERROR: ucl_init() failed, something REALLY wrong happened\n\n",argv[0]);
  	}



/* options */
	while ((optionchar=getopt(argc,argv,"b:i:I:c:lFvV"))!=-1) {
		switch (optionchar) {
			case 'b':
				blocksize=atoi(optarg);
				if (blocksize == 0 || blocksize % 512 != 0) Errexit ("Illegal block size. Specify a multiple of 512.", argv[0]);
				break;
			case 'c':
				compression=atoi(optarg);
				if (compression>10) Errexit ("Illegal compression rate. Legal values are 0-10.", argv[0]);
				break;
			case 'i':
				imagesize=atoi(optarg);
				break;
			case 'I':
				imagesize=atoi(optarg);
				forceimagesize=1;
				break;
			case 'l':
				index_lenght=64;
			case 'F':
				forceindex=1;
				fprintf(stderr, "Sorry, this will break with segmentation fault\n");
				break;
			case 'v':
				verbose++;
				break;
			case 'V':
				Version(argv[0]);
				break;
			default:
				printf ("Unknown option: %c\n",optionchar);
				Usage(argv[0]);
		}
	if (verbose>=2) fprintf(stderr,"Option %c with possible sub-option %s\n",optionchar,optarg);
	}

	if (optind == argc) Errexit("ERROR: no infile/outfile present\n\n",argv[0]);
	if (optind == argc-1) Errexit("ERROR: no outfile present\n\n",argv[0]);
	if (optind < argc-2) Errexit("ERROR: too many filenames\n\n",argv[0]);
	if (blocksize > MAX_KMALLOC_SIZE) {
		fprintf(stderr, "WARNING: Blocksize %lu may be too big for a kmalloc() (%lu max), vmalloc could be used instead\n",blocksize,MAX_KMALLOC_SIZE);
		sleep(2);
	}

	if (sizeof(CLOOP_PREAMBLE)+4 > CLOOP_HEADROOM) {
	fprintf(stderr, "*** Preamble (%u chars) > headroom (%u)\n",
			     sizeof(CLOOP_PREAMBLE), CLOOP_HEADROOM);
	return 1;
	}
/* open files */
	in=strcmp(argv[optind],"-")==0?dup(fileno(stdin)):open(argv[optind], O_RDONLY);
	out=open(argv[optind+1], O_WRONLY|O_TRUNC|O_CREAT,S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH);

	if (in < 0) {
		perror("Opening input");
		return 1;
	}
	if (out < 0) {
		perror("Opening output");
		return 1;
	}
	
 
	if ((fstat(in,&filestat)<0)||(filestat.st_size==0)||(forceimagesize)) {
		if (verbose) fprintf(stderr,"Cannot determine the imagesize value, using the provided one.\n");
	} else {
		imagesize=filestat.st_size;determinedimagesize=1;
		if (verbose) fprintf(stderr,"Input file size determined: %lli\n",(long long)filestat.st_size);
	}
	
	if (imagesize>>index_size){
		fprintf(stderr,"The image size is too big for 32bit index, forcing 64bit.\n");
		index_lenght=64;
	}
	
	guessedblocks=(imagesize / blocksize) +1;
	

/* guess index size and seek to block begin */
	if (index_lenght==32)
	{
	indexsize=sizeof(tmp)*(guessedblocks+1);
	if ((pointerblock=malloc((size_t)indexsize))==NULL) {
		fprintf(stderr, "Sorry, could not allocate pointerblock\n");
		return 1;
	}

	if (lseek(out,(off_t)(indexsize+sizeof(head)),SEEK_CUR)<0) {
		fprintf(stderr,"Cannot reposition to start of blocks - aborting.\n");
		return 1;
	}
	/* set position of first block */
	position=sizeof(head)+indexsize;
	} else {
	indexsize=sizeof(tmp64)*(guessedblocks+1);
	if ((pointerblock64=malloc((size_t)indexsize))==NULL) {
		fprintf(stderr, "Sorry, could not allocate pointerblock\n");
		return 1;
	}
	
	if (lseek(out,(off_t)(indexsize+sizeof(head64)),SEEK_CUR)<0) {
		fprintf(stderr,"Cannot reposition to start of blocks - aborting.\n");
	}
	/* set position of first block */
	position=sizeof(head64)+indexsize;
	}
/* verbosity: print out experiences */
	if (verbose) {
/* sorry for the logic parade in image size text. Logic is as follows:
-I will print "forced", $determined will print "determined" and
non-determined will print "default" if it's the default value and "set to user" if it's set by the -i option.
And yes: if a user specifies IMAGESIZE as -i, then it will print "default" and not "set". */
		fprintf(stderr,"Input image size: %lli %s\n",(long long) imagesize,forceimagesize?"(forced)":
				(determinedimagesize?"(determined from input file)":
				(imagesize==IMAGESIZE?"(could not determine - set to default)":"could not determine - set to user specification")));
		fprintf(stderr,"Block size: %li\n",blocksize);
		fprintf(stderr,"Preliminary number of blocks: %lli\n",(long long) guessedblocks);
		fprintf(stderr,"Index size set to: %i bytes, using %i bit integers\n",indexsize, index_lenght);
		fprintf(stderr,"Compression: %i (0 is no compression (silly), 1 is fastest, 10 is highest)\n",compression);
		fprintf(stderr,"Input file: %s\n", (strcmp(argv[optind],"-")==0?"<STDIN>":argv[optind]));
		fprintf(stderr,"Output file: %s\n", argv[optind+1]);
	}
	

/* malloc() buffers */
	if((uncompressed=malloc(blocksize))==NULL) {
		fprintf(stderr, "*** Can't malloc(%ld).\n",blocksize);
		return 1;
	}
	maxlen = blocksize + blocksize + 12;
	if((compressed=malloc(maxlen))==NULL) {
		fprintf(stderr, "*** Can't malloc(%ld).\n",blocksize);
		return 1;
	}

/* start compressing */
	while (! last) {
		int z_error;
		unsigned long total=0; 
		unsigned int len = maxlen;
		memset(compressed,0,len); memset(uncompressed,0,blocksize);
		while(total<blocksize) /* Read a complete block */ {
			     ssize_t r=read(in, uncompressed+total, blocksize-total);
			     if(r<=0) { last=1; break; }
			     total+=r;
		}
		if (total != blocksize){
			last=1;
			fprintf(stderr, "Partial read (%lu bytes of %lu), padding with zeros.\n",
								total, blocksize);
		}
		
		if (total > 0) {
#ifdef INDEX_NEW 
   		if(memcmp(uncompressed,memset(compressed,0,maxlen),blocksize)==0)
        	    {
	 	    len=0; /*the dumbest and simplest way to do that*/
		    fprintf(stderr,"z");
		    statz++;
    		    }
   		    else
#endif		
		if((z_error=ucl_nrv2e_99_compress(uncompressed, blocksize, compressed, &len, NULL, compression, NULL, NULL)) != UCL_E_OK)
					
		    {
			fprintf(stderr, "*** Error %d compressing block %lu! (compressed=%p,"
			" len=%u, uncompressed=%p, blocksize=%lu)\n", z_error, i, compressed,len,uncompressed,blocksize);
			return 1;	
		    }
			
#ifdef INDEX_NEW
	    if(len>=blocksize)
    		{
   	/* 
	 * I know that using correctly the pointers will be faster but now
	 * I just want a drop in solution with new code traceable quickly
	 * lu
	 */
     		len=blocksize;
     		memcpy(compressed,uncompressed,len);
		fprintf(stderr,"n");
		statn++;
    		}
	    else if (len !=0)
	    	{
    		fprintf(stderr,"o");
		stato++;
		}
#endif
			if(index_lenght==32){
			pointerblock[i++]=htonl(position);
			} else {
			pointerblock64[i++]=cpu_to_be64(position);
			}
			position+=len;
			if (write(out, compressed, (size_t)len) != len) {
				fprintf(stderr, "Could not write to output file\n");
				return 1;
			}
			countedblocks++;
			if (verbose>1) fprintf(stderr, " Block# %5lu size %6lu -> %6u (%ld%%), total compression %lu%%\n",
			i, total, len, 100-(len * 100/total),(100 - ((position-indexsize+sizeof(head)) / countedblocks * 100 / blocksize)));

			if (countedblocks > guessedblocks) {
				fprintf(stderr, "You guessed the number of blocks wrong. I will not continue...\n");
				exit (1);
			}
		}
			
	} /* while */
	
	/* write out last index */
	if(index_lenght==32){
		pointerblock[i]=htonl(position);
	} else {
		pointerblock64[i]=cpu_to_be64(position);
	}
	
	if (verbose) {
		fprintf(stderr,"\nCounted number of blocks: %lli (guessed %lli)\n",(long long) countedblocks, (long long) guessedblocks);
		fprintf(stderr,"Compressible blocks: %i\n"
			"Uncompressible blocks: %i\n"
			"Empty blocks: %i\n",stato, statn, statz);
	}
	

	/* Write out head... */
	if (lseek(out,(off_t)0,SEEK_SET)<0) {
		fprintf(stderr,"Cannot lseek to start of file - image will not work.\n");
		return 1;
	}

	memset(head.preamble,0,sizeof(head.preamble));
	
	if(index_lenght==32){
	memcpy(head.preamble, CLOOP_PREAMBLE32, sizeof(CLOOP_PREAMBLE32));
	head.block_size = htonl(blocksize);
	head.num_blocks = htonl(countedblocks);
	write(out, &head, sizeof(head));
	} else {
	memcpy(head.preamble, CLOOP_PREAMBLE64, sizeof(CLOOP_PREAMBLE64));
	head64.block_size = htonl(blocksize);
	head64.num_blocks = cpu_to_be64(countedblocks);
	write(out, &head64, sizeof(head64));
	}

/*	if (lseek(out,(off_t)(sizeof(head)),SEEK_SET)<0) {
		fprintf(stderr,"Cannot lseek to file! Image will not work.\n");
		return 1;
	}*/
	if (write(out,pointerblock,indexsize)!=indexsize) {
			fprintf(stderr,"Cannot write index block, image will not work: indexsize %i, reason %s\n",indexsize,strerror(errno));
		return 1;
	}
return 0;
}
