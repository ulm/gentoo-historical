#!/bin/bash

if [[ $# -ne 2 ]] ; then
	echo "Usage: $0 <coreutils ver> <patch ver>"
	exit 1
fi
vver=$1
pver=$2

if [[ ! -d ./${vver} ]] ; then
	echo "Error: ${vver} is not a valid coreutils ver"
	exit 1
fi

rm -rf tmp
rm -f vnc-${vver}-*.tar.bz2

mkdir -p tmp/patch/excluded
cp -r ../README* ${vver}/* tmp/patch/
find tmp/patch -name CVS -type d | xargs rm -rf

tar -jcf vnc-${vver}-patches-${pver}.tar.bz2 \
	-C tmp patch || exit 1
rm -rf tmp

du -b vnc-${vver}-*.tar.bz2
