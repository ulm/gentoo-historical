#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/Attic/stage3-chroot.sh,v 1.17.2.7 2005/07/14 15:49:03 wolf31o2 Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

if [ -n "${clst_CCACHE}" ]
then
	export clst_myfeatures="${clst_myfeatures} ccache"
	emerge --oneshot --nodeps -b -k ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then   
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gnome -gtk" emerge --oneshot --nodeps -b -k distcc || exit 1
	mkdir -p /etc/distcc
	echo "${clst_distcc_hosts}" > /etc/distcc/hosts
fi

if [ -n "${clst_PKGCACHE}" ]
then
	export clst_myemergeopts="${clst_myemergeopts} --usepkg --buildpkg --newuse"
fi

# setup the build environment
export FEATURES="${clst_myfeatures}"
export USE="${USE} ${clst_HOSTUSE}"
export CONFIG_PROTECT="-*"

## START BUILD
if [ -n "${clst_VERBOSE}" ]
then
	emerge -e ${clst_myemergeopts} -vtp system || exit 1
	echo "Press any key within 15 seconds to pause the build..."
	read -s -t 15 -n 1
	if [ $? -eq 0 ]
	then
		echo "Press any key to continue..."
		read -s -n 1
	fi
fi

if [ -n "${clst_FETCH}" ]
then
	emerge -e ${clst_myemergeopts} -f system || exit 1
fi

emerge -e ${clst_myemergeopts} system || exit 1
