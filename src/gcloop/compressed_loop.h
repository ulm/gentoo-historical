#ifndef _COMPRESSED_LOOP_H
#define _COMPRESSED_LOOP_H

#define CLOOP_HEADROOM 128

struct cloop_head
{
	char preamble[CLOOP_HEADROOM];
	u_int32_t block_size;
	u_int32_t num_blocks;
};
truct cloop_head64
{
	char preamble[CLOOP_HEADROOM];
	u_int32_t block_size;
	u_int64_t num_blocks;
};
			

#define CLOOP_VERSION	"1.00"


#endif /*_COMPRESSED_LOOP_H*/
