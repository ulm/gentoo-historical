#!/bin/bash -e

pkg="traceroute"
if [[ -z $2 ]] ; then
	echo "Usage: $0 <${pkg} ver> <patch ver>"
	exit 1
fi
ver=$1
pver=$2

if [[ ! -d ./${ver} ]] ; then
	echo "Error: ${ver} is not a valid ${pkg} ver"
	exit 1
fi

rm -rf tmp
rm -f ${pkg}-${ver}-*.tar.bz2

mkdir -p tmp/patch
cp -r ../README* ${ver}/*.patch tmp/patch/ || exit 1

tar -jcf ${pkg}-${ver}-patches-${pver}.tar.bz2 \
	-C tmp patch || exit 1
rm -r tmp

du -b ${pkg}-${ver}-*.tar.bz2
