#!/bin/bash

gver=$1
pver=$2

if [[ -z ${gver} ]] || [[ ! -d ./${gver} ]] ; then
	echo "Usage: $0 <gdb ver> [patch ver]"
	exit 1
fi

if [[ -z ${pver} ]] ; then
	pver=$(awk '{print $1; exit}' ${gver}/README.history)
	if [[ -z ${pver} ]] ; then
		echo "need patch version"
		exit 1
	fi
fi

if grep -qs Header:.*gentoo ${gver}/*.patch ; then
	echo "error: files were not added with cvs -kb"
	grep Header:.*gentoo ${gver}/*.patch
	exit 1
fi

tar=gdb-${gver}-patches-${pver}.tar.lzma

rm -rf tmp
rm -f ${tar}

mkdir -p tmp/patch
cp ${gver}/*.patch tmp/patch/ || exit 1
mkdir -p tmp/extra
cp `find extra -type f '!' -wholename '*/CVS/*'` tmp/extra/ || exit 1
cp ../README* tmp/

tar cf - -C tmp . | lzma > ${tar} || exit 1
rm -r tmp

du -b ${tar}
