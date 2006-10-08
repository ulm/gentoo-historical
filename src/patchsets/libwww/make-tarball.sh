#!/bin/bash

if [[ $# -ne 2 ]] ; then
	echo "Usage: $0 <libwww ver> <patch ver>"
	exit 1
fi
lver=$1
pver=$2

if [[ ! -d ./${lver} ]] ; then
	echo "Error: ${lver} is not a valid libwww ver"
	exit 1
fi

rm -rf tmp
rm -f libwww-${lver}-*.tar.bz2

mkdir -p tmp/patch/excluded
cp -r ../README* ${lver}/* tmp/patch/
find tmp/patch -name CVS -type d | xargs rm -rf

tar -jcf libwww-${lver}-patches-${pver}.tar.bz2 \
	-C tmp patch || exit 1
rm -rf tmp

du -b libwww-${lver}-*.tar.bz2
