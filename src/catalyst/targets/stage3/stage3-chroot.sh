#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/Attic/stage3-chroot.sh,v 1.13 2004/11/23 00:02:57 zhen Exp $

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
fi

if [ -n "${clst_PKGCACHE}" ]
then
	export clst_myemergeopts="${clst_myemergeopts} --usepkg --buildpkg --newuse"
fi

GRP_STAGE23_USE="$(portageq envvar GRP_STAGE23_USE)"

# setup the build environment
export FEATURES="${clst_myfeatures}"
export USE="-* ${clst_HOSTUSE} ${GRP_STAGE23_USE}"
export CONFIG_PROTECT="-*"

## START BUILD
# portage needs to be merged manually with USE="build" set to avoid frying our
# make.conf. emerge system could merge it otherwise.
USE="build" emerge portage

if [ -n "${clst_VERBOSE}" ]
then
	emerge ${clst_myemergeopts} -vp system || exit 1
	sleep 15
fi

emerge ${clst_myemergeopts} system || exit 1
