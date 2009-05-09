#!/bin/bash

usage()
{
	echo "Usage: $0 <package version>"
	exit 1
}

[[ $# -ne 1 ]] && usage

PN=${PWD##*/}
PV=$1
P="${PN}-${PV}"
pver=

if [[ ! -d ./${PV} ]] ; then
	echo "Error: ${PV} is not a valid version"
	exit 1
fi

if [[ -z ${pver} ]] ; then
	pver=$(awk '{print $1; exit}' ./${PV}/README.history)
	[[ -z ${pver} ]] && usage
fi

rm -rf tmp
rm -f ${P}-*.tar.bz2

mkdir -p tmp/patch
cp -r ../README* ${PV}/*.patch ${PV}/README.history tmp/patch/ || exit 1

tar jcf ${P}-patches-${pver}.tar.bz2 -C tmp patch || exit 1
rm -r tmp

du -b ${P}-*.tar.*
