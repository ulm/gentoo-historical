#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage1/Attic/livecd-stage1-chroot.sh,v 1.10 2004/12/15 00:50:35 wolf31o2 Exp $

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
	clst_emergeopts="--usepkg --buildpkg --newuse"
else
	clst_emergeopts=""
fi

## setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"

## START BUILD
USE="build" emerge portage
#turn off auto-use:
export USE_ORDER="env:conf:defaults"	

if [ "${clst_VERBOSE}" ]
then
	emerge ${clst_emergeopts} -vp ${clst_packages}
	sleep 15
fi

for packages in ${clst_packages}; do
	emerge ${clst_emergeopts} ${packages}
done
