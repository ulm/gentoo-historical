#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/patchsets/mozilla-firefox/getpacks.sh,v 1.2 2006/08/04 13:35:14 redhatter Exp ${app}/make-tarball.sh,v 1.2 2006/07/30 10:44:28 redhatter Exp $

app=firefox

if [[ $# -ne 1 ]] ; then
	echo "Usage: $0 <${app} version>"
	exit 1
fi
ver=$1

mkdir "langpacks-${ver}"
wget -P "langpacks-${ver}" -m -np -nd \
	"ftp://releases.mozilla.org/pub/mozilla.org/firefox/releases/${ver}/linux-i686/xpi/"

cd "langpacks-${ver}"
for f in *.xpi; do
	mv -v "${f}" "${app}-${ver}-${f}"
done
cd "${OLDPWD}"
