#!/bin/bash

if [[ $# -ne 2 ]] ; then
	echo "Usage: $0 <thunderbird ver> <patch ver>"
	exit 1
fi
tbver=$1
pver=$2

if [[ ! -d ./${tbver} ]] ; then
	echo "Error: ${tbver} is not a valid mozilla-thunderbird ver"
	exit 1
fi

[ -d "tmp" ] && rm -rf tmp
[ -e "mozilla-thunderbird-${tbver}-patches-${pver}.tar.bz2" ] && \
	rm -f mozilla-thunderbird-${tbver}-patches-${pver}.tar.bz2

echo 
mkdir -p tmp/patch
cp -r ${tbver}/*.patch ./tmp/patch/ || exit 1

find tmp -type d -name CVS -print0 | xargs -0 rm -rf

tar -jcf mozilla-thunderbird-${tbver}-patches-${pver}.tar.bz2 \
	-C tmp patch || exit 1

rm -r tmp

du -b *-patches-*.tar.bz2
