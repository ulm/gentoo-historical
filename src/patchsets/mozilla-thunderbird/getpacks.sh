#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/patchsets/mozilla-thunderbird/getpacks.sh,v 1.1 2006/09/16 04:38:14 redhatter Exp ${app}/make-tarball.sh,v 1.2 2006/07/30 10:44:28 redhatter Exp $

app=thunderbird

if [[ $# -ne 1 ]] ; then
	echo "Usage: $0 <${app} version>"
	exit 1
fi
ver=$1

mkdir "langpacks-${ver}"
wget -P "langpacks-${ver}" -m -np -nd \
	"ftp://releases.mozilla.org/pub/mozilla.org/thunderbird/releases/${ver}/linux-i686/xpi/"

cd "langpacks-${ver}"
for f in *.xpi; do
	bn="$( basename "${f}" .xpi)"
	locales="${locales} ${bn}"
	mv -v "${f}" "${app}-${bn}-${ver}.xpi"
done
cd "${OLDPWD}"
echo "Locales: ${locales}"
