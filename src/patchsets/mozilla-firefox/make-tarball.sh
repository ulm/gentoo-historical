#!/bin/bash

if [[ $# -ne 2 ]] ; then
	echo "Usage: $0 <firefox ver> <patch ver>"
	exit 1
fi
ffver=$1
pver=$2

if [[ ! -d ./${ffver} ]] ; then
	echo "Error: ${ffver} is not a valid mozilla-firefox ver"
	exit 1
fi

[ -d "tmp" ] && rm -rf tmp
[ -e "mozilla-firefox-${ffver}-patches-${pver}.tar.bz2" ] && \
	rm -f mozilla-firefox-${ffver}-patches-${pver}.tar.bz2

echo 
mkdir -p tmp/patch
cp -r ${ffver}/*.patch ./tmp/patch/ || exit 1

find tmp -type d -name CVS -print0 | xargs -0 rm -rf

tar -jcf mozilla-firefox-${ffver}-patches-${pver}.tar.bz2 \
	-C tmp patch || exit 1

rm -r tmp

du -b *-patches-*.tar.bz2
