#!/bin/bash

if [[ $# -ne 1 ]] ; then
	echo "Usage: $0 <patch ver>"
	exit 1
fi
gver=1.20.1
pver=$1

tar=gpm-${gver}-patches-${pver}.tar.bz2

rm -rf tmp
rm -f ${tar}

mkdir -p tmp/patch
cp -r *.patch tmp/patch/ || exit 1

find tmp -type f | xargs bzip2

tar -jcf ${tar} \
	-C tmp patch || exit 1
rm -r tmp

du -b ${tar}
