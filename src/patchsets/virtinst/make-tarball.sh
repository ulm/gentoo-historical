#!/bin/bash

if [[ $# -ne 2 ]] ; then
	echo "Usage: $0 <virtinst ver> <patch ver>"
	exit 1
fi

bver=$1
pver=$2

tar=virtinst-patches-${bver}-${pver}.tbz2

rm -f ${tar}

tar -jcf ${tar} -C ${bver} --exclude=CVS . || exit 1

du -b ${tar}
