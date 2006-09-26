#!/bin/bash

if [[ -z $2 ]] ; then
	echo "Usage: $0 <elfutils ver> <patch ver>"
	exit 1
fi
ever=$1
pver=$2

if [[ ! -d ./${ever} ]] ; then
	echo "Error: ${ever} is not a valid elfutils ver"
	exit 1
fi

rm -rf tmp
rm -f elfutils-${ever}-*.tar.bz2

mkdir -p tmp/patch
cp -r ../README* ${ever}/*.patch tmp/patch/ || exit 1

tar -jcf elfutils-${ever}-patches-${pver}.tar.bz2 \
	-C tmp patch || exit 1
rm -r tmp

du -b elfutils-${ever}-*.tar.bz2
