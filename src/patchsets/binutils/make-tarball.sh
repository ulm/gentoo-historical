#!/bin/bash

usage()
{
	echo "Usage: $0 <binutils ver> <patch ver> [uclibc ver]"
	exit 1
}

[[ $# -eq 0 ]] && usage
[[ $# -gt 3 ]] && usage

bver=$1
pver=$2
uver=$3

if [[ ! -d ./${bver} ]] ; then
	echo "Error: ${bver} is not a valid binutils ver"
	exit 1
fi
if [[ -n ${uver} ]] && [[ ! -d ./${bver}/uclibc ]] ; then
	echo "Error: ${bver} doesnt support uClibc :("
	exit 1
fi

if [[ -z ${pver} ]] ; then
	pver=$(awk '{print $1; exit}' ./${bver}/README.history)
	[[ -z ${pver} ]] && usage
fi

rm -rf tmp
rm -f binutils-${bver}-*.tar.bz2

mkdir -p tmp/patch
cp -r ../README* ${bver}/*.patch ${bver}/README.history tmp/patch/ || exit 1
if [[ -n ${uver} ]] ; then
	mkdir -p tmp/uclibc-patches
	cp -r ../README* ${bver}/uclibc/*.patch tmp/uclibc-patches/ || exit 1
fi

#find tmp -type f -a ! -name 'README*' | xargs bzip2

tar -jcf binutils-${bver}-patches-${pver}.tar.bz2 \
	-C tmp patch || exit 1
if [[ -n ${uver} ]] ; then
	tar -jcf binutils-${bver}-uclibc-patches-${uver}.tar.bz2 \
		-C tmp uclibc-patches || exit 1
fi
rm -r tmp

du -b binutils-${bver}-*.tar.bz2
