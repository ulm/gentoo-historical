#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/patchsets/seamonkey/make-tarball.sh,v 1.2 2011/06/23 11:41:39 polynomial-c Exp ${app}/make-tarball.sh,v 1.2 2006/07/30 10:44:28 redhatter Exp $

app=seamonkey

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
[ -e "${app}-${ver}-patches-${pver}.tar.xz" ] && \
	rm -f ${app}-${ver}-patches-${pver}.tar.xz

echo 
mkdir -p tmp/patch
cp -r ${ver}/*.patch ./tmp/patch/ || exit 1

find tmp -type d -name CVS -print0 | xargs -0 rm -rf

tar -Jcf ${app}-${ver}-patches-${pver}.tar.xz \
	-C tmp patch || exit 1

rm -r tmp

du -b *-patches-*.tar.xz
