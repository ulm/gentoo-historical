#!/bin/bash

if [[ $# -ne 2 ]] ; then
	echo "Usage: $0 <tcp-wrappers ver> <patch ver>"
	exit 1
fi

tver=$1
pver=$2
if [[ ! -d $tver ]] ; then
	echo "dir '$tver' does not exist"
	exit 1
fi

tar=tcp-wrappers-${tver}-patches-${pver}.tar.bz2
rm -f tcp-wrappers-${tver}-*.tar.bz2
tar -jcf ${tar} --exclude="CVS" ${tver}

du -b *.bz2
