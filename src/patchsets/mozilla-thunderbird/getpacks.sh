#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/patchsets/mozilla-thunderbird/getpacks.sh,v 1.2 2007/03/02 10:42:20 armin76 Exp ${app}/make-tarball.sh,v 1.2 2006/07/30 10:44:28 redhatter Exp $

PN=mozilla-thunderbird

if [[ $# -ne 1 ]] ; then
	echo "Usage: $0 <${PN} portage version>"
	exit 1
fi
PV=$1
MY_PV=${PV/_}
P=${PN}-${PV}
S=${P}-xpi

mkdir ${S}
wget -P "${S}" -m -np -nd \
	"ftp://releases.mozilla.org/pub/mozilla.org/thunderbird/releases/${MY_PV}/linux-i686/xpi/"

cd ${S}
for f in *.xpi; do
	bn="$( basename "${f}" .xpi)"
	locales="${locales} ${bn}"
	mv -v "${f}" "${P}-${bn}.xpi"
done
cd "${OLDPWD}"
echo "Locales: ${locales}"
