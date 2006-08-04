#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/patchsets/mozilla-firefox/getpacks.sh,v 1.1 2006/08/04 02:03:53 redhatter Exp ${app}/make-tarball.sh,v 1.2 2006/07/30 10:44:28 redhatter Exp $

if [[ $# -ne 1 ]] ; then
	echo "Usage: $0 <version>"
	exit 1
fi
ver=$1

mkdir "langpacks-${ver}"
wget -P "langpacks-${ver}" -m -np -nd \
	"ftp://releases.mozilla.org/pub/mozilla.org/firefox/releases/${ver}/linux-i686/xpi/"
