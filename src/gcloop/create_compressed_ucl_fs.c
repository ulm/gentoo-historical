/* Creates a compressed image, given a file as an argument.
 * (c)1999 Paul `Rusty' Russell.  GPL.
 *
 * CHANGELOG:
 * * Thu Jan 2 2003 Luca Barbato <lu_zero@sig11.org>
 * - ucl compression, uncompressible blocks handling
 * * Sat Sep 29 2001 Klaus Knopper <knopper@knopper.net>
 * - changed compression to Z_BEST_COMPRESSION,
 * * Sat Jun 17 2000 Klaus Knopper <knopper@knopper.net>
 * - Support for reading file from stdin,
 * - Changed Preamble.
 * * Sat Jul 28 2001 Klaus Knopper <knopper@knopper.net>
 * - cleanup and gcc 2.96 / glibc checking
 */
/*#define INDEX_NEW*/
#include <stdio.h>
#include <netinet/in.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "compressed_loop.h"
#include <ucl/ucl.h>

#define MAX_KMALLOC_SIZE 1L<<17

#define CLOOP_PREAMBLE	"#gcloop nrv2e "  CLOOP_VERSION

struct cb_list
{
	struct cb_list *next;
	size_t size;
	char data[0];
};

void free_cb_list(struct cb_list *cbl)
{
 if(cbl->next) free_cb_list(cbl->next);
 free(cbl);
}

int Version(char* argv) {
fprintf(stderr, "%s Version " CLOOP_VERSION " Preamble:" CLOOP_PREAMBLE "\n", argv);
exit(1);
return 1;
}

int Usage(char* argv) {
fprintf(stderr, "Usage: %s filename blocksize(bytes).\n",argv);
fprintf(stderr, "Use '-' as filename for stdin.\n");
exit(1);
return 1;
} /* Usage() */
 

/* Now using the goto style because it is quicker to read */
static struct cb_list *create_compressed_blocks(int handle, unsigned int
                          blocksize, unsigned long *numblocks)
{
 struct cb_list *cbl,**cbp=&cbl;
 unsigned long i=0;
 unsigned int last;
 unsigned long long total_uncompressed=0,total_compressed=0;
 unsigned int maxlen = blocksize + blocksize + 256;
 ucl_byte *compressed, *uncompressed;

 if((uncompressed=malloc(blocksize))==NULL)
  {
   fprintf(stderr, "*** Can't malloc(%d).\n",blocksize);
   return NULL;
  }
 if((compressed=malloc(maxlen))==NULL)
  {
   fprintf(stderr, "*** Can't malloc(%d).\n",maxlen);
   goto free_uncompressed;
  }
 for(i=0,last=0; !last; i++)
  {
   int z_error;
   unsigned long total=0;
   unsigned int len=0;
   memset(uncompressed,0,blocksize);
   while(total<blocksize) /* Read a complete block */
    {
     ssize_t r=read(handle, uncompressed+total, blocksize-total);
     if(r<=0) { last=1; break; }
     total+=r;
    }
   total_uncompressed += total;
   if (total != blocksize)
    {
     last=1;
     fprintf(stderr, "Partial read (%lu bytes of %u), padding with zeros.\n",
					total, blocksize);
    }
#ifdef INDEX_NEW 
   if(memcmp(uncompressed,memset(compressed,0,maxlen),blocksize)==0)
    {
     len=0; /*the dumbest and simplest way to do that*/
    }
   else
#endif
   if((z_error=ucl_nrv2e_99_compress(uncompressed, blocksize,compressed, &len,
					NULL,10,NULL,NULL)) != UCL_E_OK)
    {
     fprintf(stderr, "*** Error %d compressing block %lu! (compressed=%p, len=%u, uncompressed=%p, blocksize=%u)\n", z_error, i, compressed,len,uncompressed,blocksize);
     goto error_free_cb_list;
    }
#ifdef INDEX_NEW
   if(len>=blocksize)
    {
   /* I know that using correctly the pointers will be faster but now
    * I just want a drop in solution with new code traceable quickly
    */
     len=blocksize;
     memcpy(compressed,uncompressed,len);
    }
#endif
   if((*cbp = malloc(sizeof(struct cb_list)+len))==NULL) /* get another block */
    {
     fprintf(stderr, "*** Out of memory allocating block ptrs (virtual memory exhausted).\n");
     goto error_free_cb_list;
    }
   total_compressed+=len;
   /* Print status */
   fprintf(stderr, "Block# %5lu size %6lu -> %6u [compression ratio %3lu%%, overall: %3Lu%%]\n", i, total, len, total>0?((len*100)/total):100,total_uncompressed>0?((total_compressed*100)/total_uncompressed):100);
   (*cbp)->size = len;
   memcpy((*cbp)->data, compressed, len);
   (*cbp)->next=NULL;
   cbp=&((*cbp)->next);
  } /* for */
 goto free_compressed;

 error_free_cb_list:
    if(cbl) { free_cb_list(cbl); cbl=NULL; i=0; }

 free_compressed:
        free(compressed);
 free_uncompressed:
    free(uncompressed);
 
 *numblocks=i;
 return cbl;
}

int main(int argc, char **argv)
{
 int in;
 unsigned int blocksize;
 struct cloop_head head;
 unsigned long numblocks;
 unsigned long bytes_so_far;
 unsigned long i;
 struct cb_list *compressed_blocks,*cbp;
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
 if (argc != 3)
	Usage(argv[0]);

 if (ucl_init()!= UCL_E_OK)
  {
   fprintf(stderr, "ucl_init() failed, something is REALLY wrong\n");
   return 4;
  }

 blocksize = atoi(argv[2]);
 if (blocksize == 0 || blocksize % 512 != 0)
  {
   fprintf(stderr, "*** Blocksize must be a multiple of 512.\n");
   return 1;
  }

 if (blocksize > MAX_KMALLOC_SIZE)
  {
   fprintf(stderr, "WARNING: Blocksize %u may be too big for a kmalloc() (%lu max).\n",blocksize,MAX_KMALLOC_SIZE);
   sleep(2);
  }

 if (sizeof(CLOOP_PREAMBLE) > CLOOP_HEADROOM)
  {
   fprintf(stderr, "*** Preamble (%u chars) > headroom (%u)\n",
			sizeof(CLOOP_PREAMBLE), CLOOP_HEADROOM);
   return 1;
  }
		
 in=strcmp(argv[1],"-")==0?dup(fileno(stdin)):open(argv[1], O_RDONLY);

 if (in < 0)
  {
   perror("Opening input");
   return 1;
  }

 compressed_blocks = create_compressed_blocks(in, blocksize, &numblocks);

 close(in);

 memcpy(head.preamble, CLOOP_PREAMBLE, sizeof(CLOOP_PREAMBLE));
 head.block_size = htonl(blocksize);
 head.num_blocks = htonl(numblocks);

 fprintf(stderr, "Block size %u, number of blocks %lu.\n",
         blocksize, numblocks);

 bytes_so_far = sizeof(head) + sizeof(u_int32_t) * (numblocks + 1);
 if(bytes_so_far > MAX_KMALLOC_SIZE)
  {
   fprintf(stderr, "\nWARNING: cloop block index may not fit into a kmalloc()\n*** (%lu bytes max, current %lu)\n\n", MAX_KMALLOC_SIZE, bytes_so_far);
   sleep(2);
  }

 /* Write out head... */
 write(STDOUT_FILENO, &head, sizeof(head));

 if (!compressed_blocks) return 1;

 /* Write offsets */
 for (i=0,cbp=compressed_blocks; i < numblocks+1; i++)
  {
   u_int32_t tmp;
   tmp = htonl(bytes_so_far);
   write(STDOUT_FILENO, &tmp, sizeof(tmp));
   if(cbp) { bytes_so_far += cbp->size; cbp=cbp->next; }
  }

 /* Now write blocks and free them. */
 for (i = 0, cbp=compressed_blocks; cbp && i < numblocks; i++)
  {
   if (write(STDOUT_FILENO, cbp->data, cbp->size) != cbp->size)
    {
     perror("writing block");
     free_cb_list(compressed_blocks);
     return 1;
    }
   cbp=cbp->next;
   free(compressed_blocks); compressed_blocks=cbp;
  }
 fprintf(stderr,"Done.\n");
 return 0;
}
