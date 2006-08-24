#!/bin/bash

if [[ $# -ne 2 ]] ; then
	echo "Usage: $0 <gdb ver> <patch ver>"
	exit 1
fi
gver=$1
pver=$2

tar=gdb-${gver}-patches-${pver}.tar.bz2

rm -rf tmp
rm -f ${tar}

mkdir -p tmp/patch
cp ${gver}/*.patch tmp/patch/ || exit 1
mkdir -p tmp/extra
cp `find extra -type f '!' -path '*/CVS*/'` tmp/extra/ || exit 1
cp ../README* tmp/

tar -jcf ${tar} -C tmp . || exit 1
rm -r tmp

du -b ${tar}
