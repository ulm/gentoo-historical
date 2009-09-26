#!/bin/sh

if [ $# -ne 2 ]; then
	echo "Usage: $0 <package ver> <patch ver>"
	exit 1
fi
pkgver=$1
pver=$2

tar=$(basename $(pwd))-${pkgver}-patches-${pver}.tar.bz2

rm -rf tmp
mkdir -p tmp/patch
cp -l *.patch tmp/patch/ || exit 1

tar jcf ${tar} -C tmp . || exit 1

rm -rf tmp

du -b ${tar}
