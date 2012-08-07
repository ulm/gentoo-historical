#!/bin/bash

PN="gdb"
PV=$1
pver=$2

if [[ -z ${PV} ]] || [[ ! -d ./${PV} ]] ; then
	echo "Usage: $0 <${PN} ver> [patch ver]"
	exit 1
fi

if [[ -z ${pver} ]] ; then
	pver=$(awk '{print $1; exit}' ${PV}/README.history)
	if [[ -z ${pver} ]] ; then
		echo "need patch version"
		exit 1
	fi
fi

if grep -qs Header:.*gentoo ${PV}/*.patch ; then
	echo "error: files were not added with cvs -kb"
	grep Header:.*gentoo ${PV}/*.patch
	exit 1
fi

tar=${PN}-${PV}-patches-${pver}.tar.xz

rm -rf tmp
rm -f ${tar}

mkdir -p tmp/patch
cp ${PV}/*.patch tmp/patch/ || exit 1
mkdir -p tmp/extra
cp `find extra -type f '!' -wholename '*/CVS/*'` tmp/extra/ || exit 1
cp ../README* tmp/patch/

tar cf - -C tmp patch extra | xz > ${tar} || exit 1
rm -r tmp

du -b ${tar}
