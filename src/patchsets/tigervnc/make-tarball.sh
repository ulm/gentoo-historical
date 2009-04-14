#!/bin/bash

if [[ $# -ne 2 ]] ; then
	echo "Usage: $0 <tigervnc ver> <patch ver>"
	exit 1
fi
vver=$1
pver=$2

if [[ ! -d ./${vver} ]] ; then
	echo "Error: ${vver} is not a valid tigervnc ver"
	exit 1
fi

rm -rf tmp
rm -f tigervnc-${vver}-*.tar.bz2

mkdir -p tmp/patch/excluded
cp -r ${vver}/* tmp/patch/
find tmp/patch -name CVS -type d | xargs rm -rf

tar -jcf tigervnc-${vver}-patches-${pver}.tar.bz2 \
	-C tmp patch || exit 1
rm -rf tmp

du -b tigervnc-${vver}-*.tar.bz2
