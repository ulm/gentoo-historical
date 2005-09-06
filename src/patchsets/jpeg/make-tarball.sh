#!/bin/bash

if [[ $# -ne 1 ]] ; then
	echo "Usage: $0 <patch ver>"
	exit 1
fi
pver=$1

tar=jpeg-6b-patches-${pver}.tar.bz2

rm -rf tmp
rm -f ${tar}

mkdir -p tmp/patch
cp patches/*.patch tmp/patch/ || exit 1
mkdir -p tmp/extra
cp `find extra -type f '!' -path '*/CVS*/'` tmp/extra/ || exit 1
cp ../README* tmp/

tar -jcf ${tar} -C tmp . || exit 1
rm -r tmp

du -b ${tar}
