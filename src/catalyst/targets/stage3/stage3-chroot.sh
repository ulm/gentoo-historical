#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/Attic/stage3-chroot.sh,v 1.2 2004/04/14 00:17:59 zhen Exp $

/usr/sbin/env-update
source /etc/profile

if [ -n ${clst_ENVSCRIPT} ]
then
	source /tmp/envscript
	rm -f /tmp/envscript
fi

if [ -n "${clst_CCACHE}" ]
then
	export clst_myfeatures="${clst_myfeatures} ccache"
	emerge --oneshot --nodeps ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then   
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gnome -gtk" emerge --oneshot --nodeps distcc || exit 1
	cat /etc/passwd
	sleep 10
	echo "distcc:x:7980:2:distccd:/dev/null:/bin/false" >> /etc/passwd
	/usr/bin/distcc-config --install 2>&1 > /dev/null
	/usr/bin/distccd 2>&1 > /dev/null
fi

if [ -n "${clst_PKGCACHE}" ]
then
	export clst_myemergeopts="${clst_myemergeopts} --usepkg --buildpkg"
fi

grep GRP_STAGE23_USE /etc/make.profile/make.defaults > /tmp/stage23
source /tmp/stage23
rm -f /tmp/stage23

# setup the build environment
export FEATURES="${clst_myfeatures}"
export USE="-* ${clst_HOSTUSE} ${GRP_STAGE23_USE}"
export CONFIG_PROTECT="-*"

## START BUILD
# portage needs to be merged manually with USE="build" set to avoid frying our
# make.conf. emerge system could merge it otherwise.
USE="build" emerge portage
	
emerge ${clst_myemergeopts} system || exit 1
