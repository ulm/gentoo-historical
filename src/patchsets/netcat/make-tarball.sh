#!/bin/bash

if [[ $# -ne 1 ]] ; then
	echo "Usage: $0 <patch ver>"
	exit 1
fi
pver=$1

tar=netcat-110-patches-${pver}.tar.bz2

rm -rf tmp
rm -f ${tar}

mkdir -p tmp/patch
cp *.patch tmp/patch/ || exit 1
cp ../README* debian-* nc.1 tmp/

tar -jcf ${tar} -C tmp . || exit 1
rm -r tmp

du -b ${tar}
