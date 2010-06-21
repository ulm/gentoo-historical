#!/bin/bash

cd "${0%/*}"
PN=${PWD##*/}
PV=${1%/}
pver=$2

if [[ -z ${PV} ]] ; then
	echo "Usage: $0 <base ver> [patch ver]"
	exit 1
fi

pv=${PV:0:3}
if [[ ! -d ./patches/${pv} ]] ; then
	echo "Error: ${PV} is not a valid ver"
	exit 1
fi

if [[ -z ${pver} ]] ; then
	echo "Error: need a patch version"
	exit 1
fi

rm -rf tmp
rm -f ${PN}-${PV}-*.tar.bz2

mkdir -p tmp/gentoo
cp -r patches/${pv} tmp/gentoo/patches || exit 1
cp -r configs scripts ../README* tmp/gentoo/ || exit 1

find tmp -type d -name CVS -exec rm -r {} +

tar -jcf ${PN}-${PV}-patches-${pver}.tar.bz2 -C tmp gentoo || exit 1
rm -r tmp

du -b *.tar.bz2
