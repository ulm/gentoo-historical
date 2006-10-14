#!/bin/sh

if [ $# -ne 1 ]; then
	echo "Usage: $0 <patch ver>"
	exit 1
fi
pver=$1

tar=netkit-rsh-0.17-patches-${pver}.tar.bz2

rm -r tmp
mkdir -p tmp/patch
cp *.patch tmp/patch/ || exit 1

tar -jcf ${tar} -C tmp . || exit 1

rm -r tmp

du -b ${tar}
