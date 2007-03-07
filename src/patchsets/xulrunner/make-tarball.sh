#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/patchsets/xulrunner/make-tarball.sh,v 1.1 2007/03/07 13:40:44 armin76 Exp $

app=xulrunner

if [[ $# -ne 2 ]] ; then
	echo "Usage: $0 <${app} ver> <patch ver>"
	exit 1
fi
ver=$1
pver=$2

if [[ ! -d ./${ver} ]] ; then
	echo "Error: ${ver} is not a valid ${app} ver"
	exit 1
fi

[ -d "tmp" ] && rm -rf tmp
[ -e "${app}-${ver}-patches-${pver}.tar.bz2" ] && \
	rm -f ${app}-${ver}-patches-${pver}.tar.bz2

echo 
mkdir -p tmp/patch
cp -r ${ver}/*.patch ./tmp/patch/ || exit 1

find tmp -type d -name CVS -print0 | xargs -0 rm -rf

tar -jcf ${app}-${ver}-patches-${pver}.tar.bz2 \
	-C tmp patch || exit 1

rm -r tmp

du -b *-patches-*.tar.bz2
