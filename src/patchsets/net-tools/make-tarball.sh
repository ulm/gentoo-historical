#!/bin/bash

if [[ $# -ne 1 ]] ; then
	echo "Usage: $0 <patch ver>"
	exit 1
fi
nver=1.60
pver=$1

rm -rf tmp
rm -f net-tools-${nver}-*.tar.bz2

mkdir -p tmp/patch/excluded
cp -r ../README* *.patch tmp/patch/
cp -r extra tmp/
find tmp -type d -name CVS -print0 | xargs -0 rm -r

tar -jcf net-tools-${nver}-patches-${pver}.tar.bz2 \
	-C tmp patch extra || exit 1
rm -rf tmp

du -b net-tools-${nver}-*.tar.bz2
