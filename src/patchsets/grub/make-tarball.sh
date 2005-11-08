#!/bin/bash

if [[ $# -ne 2 ]] ; then
	echo "Usage: $0 <grub ver> <patch ver>"
	exit 1
fi
gver=$1
pver=$2

if [[ ! -d ./${gver} ]] ; then
	echo "Error: ${gver} is not a valid grub ver"
	exit 1
fi

rm -rf tmp
rm -f grub-${gver}-*.tar.bz2

mkdir -p tmp/patch
cp -r ../README* ${gver}/*.patch tmp/patch/ || exit 1

#find tmp -type f -a ! -name 'README*' | xargs bzip2

tar -jcf grub-${gver}-patches-${pver}.tar.bz2 \
	-C tmp patch || exit 1
rm -r tmp

du -b grub-${gver}-*.tar.bz2
