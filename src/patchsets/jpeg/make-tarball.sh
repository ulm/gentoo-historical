#!/bin/bash

ver=$1
pver=$2

if [[ $# -ne 2 ]] ; then
	echo "Usage: $0 <pkg ver> <patch ver>"
	exit 1
fi

tar=jpeg-${ver}-patches-${pver}.tar.bz2

rm -rf tmp
rm -f ${tar}

mkdir -p tmp/patch
cp ${ver}/*.patch tmp/patch/ || exit 1
cp ../README* tmp/

tar -jcf ${tar} -C tmp . || exit 1
rm -r tmp

du -b ${tar}
