#!/bin/sh

if [ $# -ne 1 ]; then
	echo "Usage: $0 <patch ver>"
	exit 1
fi
pver=$1

tar=netkit-rsh-0.17-patches-${pver}.tar.lzma

rm -rf tmp
mkdir -p tmp/patch
cp *.patch tmp/patch/ || exit 1

tar cf - -C tmp . | lzma > ${tar} || exit 1

rm -rf tmp

du -b ${tar}
