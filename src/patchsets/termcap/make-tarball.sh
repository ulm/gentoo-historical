#!/bin/bash

if [[ -z $2 ]] ; then
	echo "Usage: $0 <termcap ver> <patch ver>"
	exit 1
fi
tver=$1
pver=$2

if [[ ! -d ./${tver} ]] ; then
	echo "Error: ${tver} is not a valid termcap ver"
	exit 1
fi

rm -rf tmp
rm -f termcap-${tver}-*.tar.bz2

mkdir -p tmp/patch/tc.file
cp -r ../README* ${tver}/*.patch tmp/patch/ || exit 1
cp ${tver}/tc.file/*.patch tmp/patch/tc.file/ || exit 1

tar -jcf termcap-${tver}-patches-${pver}.tar.bz2 \
	-C tmp patch || exit 1
rm -r tmp

du -b termcap-${tver}-*.tar.bz2
