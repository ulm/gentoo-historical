#!/usr/bin/make

CFLAGS:=-Wall -O2  -I. -g -DINDEX_NEW 

all: newnames

#ucl hacked
uclall: create_compressed_ucl_fs extract_compressed_ucl_fs compressloop_ucl
#lzo hacked
#lzoall: create_compressed_lzo_fs extract_compressed_lzo_fs
#zlib original ones
#zall: zcode create_compressed_zlib_fs extract_compressed_zlib_fs compressloop

#zcode: zlib-1.1.4/adler32.o zlib-1.1.4/uncompr.o zlib-1.1.4/trees.o zlib-1.1.4/zutil.o zlib-1.1.4/inflate.o zlib-1.1.4/infblock.o zlib-1.1.4/inftrees.o zlib-1.1.4/infcodes.o zlib-1.1.4/infutil.o zlib-1.1.4/inffast.o

#create_compressed_zlib_fs: create_compressed_zlib_fs.o
#	$(CC) -o $@ $< zlib-1.1.4/libz.a

#compressloop: compressloop.o
#	$(CC) -o $@ $< zlib-1.1.4/libz.a

#extract_compressed_zlib_fs: extract_compressed_zlib_fs.o
#	$(CC) -o $@ $< zlib-1.1.4/libz.a

#zlib-1.1.4/%.o:
#	$(MAKE) -C zlib-1.1.4/ CFLAGS="-O2 -DNO_MEMCPY"
# using the liblzo.a and the compatibility include for tests,
# the mini ones will be used if everything is ok

#create_compressed_lzo_fs: create_compressed_lzo_fs.o
#	$(CC) -o $@ $< -static -llzo

#extract_compressed_lzo_fs: extract_compressed_lzo_fs.o
#	$(CC) -o $@ $< -static -llzo

create_compressed_ucl_fs: create_compressed_ucl_fs.o
	$(CC) -o $@ $< -static -lucl

compressloop_ucl: compressloop_ucl.o
	$(CC) -o $@ $< -static -lucl

extract_compressed_ucl_fs: extract_compressed_ucl_fs.o
	$(CC) -o $@ $< -static -lucl

newnames: uclall
	@echo
	@echo New naming scheme
	@echo
	ln -s create_compressed_ucl_fs create_gcloop_ucl
	ln -s compressloop_ucl compress_gcloop_ucl
	ln -s extract_compressed_ucl_fs extract_gcloop_ucl

clean:
	rm -f create_compressed_*fs extract_compressed_*fs \
	compress_loop_ucl  *.o\
	compressloop compressloop_ucl \
	create_gcloop_ucl compress_gcloop_ucl extract_gcloop_ucl

create_compressed_*fs.o: compressed_loop.h
