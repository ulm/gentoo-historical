#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/stage1-chroot.sh,v 1.29.2.10 2005/07/20 22:36:15 wolf31o2 Exp $
		
/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

export clst_myfeatures="${clst_myfeatures} nodoc noman noinfo"

if [ -n "${clst_CCACHE}" ]
then
	export clst_myfeatures="${clst_myfeatures} ccache"	
	emerge --oneshot --nodeps -b -k ccache || exit 1
fi
		
if [ -n "${clst_DISTCC}" ]
then   
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gtk -gnome" emerge --oneshot --nodeps -b -k distcc || exit 1
	mkdir -p /etc/distcc
	echo "${clst_distcc_hosts}" > /etc/distcc/hosts
fi

if [ -n "${clst_PKGCACHE}" ]
then
	export clst_myemergeopts="${clst_myemergeopts} --usepkg --buildpkg --newuse"
fi

# setup our environment
export FEATURES="${clst_myfeatures}"
export ROOT=${1}
install -d ${ROOT}

## START BUILD
export clst_buildpkgs="$(/tmp/build.py)"
STAGE1_USE="$(portageq envvar STAGE1_USE)"

## Sanity check profile
if [ -z "${clst_buildpkgs}" ]
then
	echo "Your profile seems to be broken."
	echo "Could not build a list of build packages."
	echo "Double check your /etc/make.profile link and the 'packages' files."
	exit 1
fi

if [ -n "${clst_VERBOSE}" ]
then
	USE="-* build" emerge ${clst_myemergeopts} -vtp --noreplace ${clst_buildpkgs} || exit 1
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
	USE="-* build ${STAGE1_USE}" emerge ${clst_myemergeopts} -f --noreplace ${clst_buildpkgs} || exit 1
fi

USE="-* build ${STAGE1_USE}" emerge ${clst_myemergeopts} --noreplace ${clst_buildpkgs} || exit 1
