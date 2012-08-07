#!/bin/bash

PN="binutils"

usage()
{
	echo "Usage: $0 <${PN} ver> <patch ver> [uclibc ver]"
	exit 1
}

[[ $# -eq 0 ]] && usage
[[ $# -gt 3 ]] && usage

PV=$1
pver=$2
uver=$3

if [[ ! -d ./${PV} ]] ; then
	echo "Error: ${PV} is not a valid ${PN} ver"
	exit 1
fi
if [[ -n ${uver} ]] && [[ ! -d ./${PV}/uclibc ]] ; then
	echo "Error: ${PV} doesnt support uClibc :("
	exit 1
fi

if [[ -z ${pver} ]] ; then
	pver=$(awk '{print $1; exit}' ./${PV}/README.history)
	[[ -z ${pver} ]] && usage
fi

tbase="${PN}-${PV}"
case ${PV} in
2.2[2-9].*)
	comp="xz"
	tsfx="tar.xz"
	;;
*)
	comp="bzip2"
	tsfx="tar.bz2"
	;;
esac

rm -rf tmp
rm -f ${tbase}-*.${tsfx}

mkdir -p tmp/patch
cp -r ../README* ${PV}/*.patch ${PV}/README.history tmp/patch/ || exit 1
if [[ -n ${uver} ]] ; then
	mkdir -p tmp/uclibc-patches
	cp -r ../README* ${PV}/uclibc/*.patch tmp/uclibc-patches/ || exit 1
fi

tar -cf - -C tmp patch | ${comp} > ${tbase}-patches-${pver}.${tsfx} || exit 1
if [[ -n ${uver} ]] ; then
	tar -cf - -C tmp uclibc-patches | ${comp} > ${tbase}-uclibc-patches-${uver}.${tsfx} || exit 1
fi
rm -r tmp

du -b ${tbase}-*.${tsfx}
