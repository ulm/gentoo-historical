#!/bin/bash

if [[ $# -ne 2 ]] ; then
	echo "Usage: $0 <ver> <patch ver>"
	exit 1
fi
gver=$1
pver=$2

tar=gpm-${gver}-patches-${pver}.tar.bz2

rm -rf tmp
rm -f ${tar}

mkdir -p tmp/patch
cp -r $gver/*.patch tmp/patch/ || exit 1
cp ../README* tmp/patch/

tar -jcf ${tar} \
	-C tmp patch || exit 1
rm -r tmp

du -b ${tar}
