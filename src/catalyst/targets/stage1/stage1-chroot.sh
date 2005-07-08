#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/stage1-chroot.sh,v 1.29.2.7 2005/07/08 15:07:12 wolf31o2 Exp $
		
portage_version=`/usr/lib/portage/bin/portageq best_version / sys-apps/portage \
	| cut -d/ -f2 | cut -d- -f2,3`
if [ `echo ${portage_version} | cut -d- -f1 | cut -d. -f3` -lt 51 ]
then
	echo "ERROR: Your portage version is too low in your seed stage.  Portage version"
	echo "2.0.51 or greater is required."
	exit 1
fi

/usr/sbin/env-update
source /etc/profile

#if [ -x /usr/bin/gcc-config ]
#then
#	gcc_current=`gcc-config -c`
#	if [ -z "${gcc_current}" ]
#	then
#		gcc_current=1
#	fi
#	gcc-config 3 && source /etc/profile
#	gcc-config ${gcc_current} && source /etc/profile
#fi

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

	USE="-gtk -gnome" emerge --oneshot --nodeps -b -k distcc || exit 1
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
	USE="-* build" emerge ${clst_myemergeopts} -vp --noreplace ${clst_buildpkgs} || exit 1
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
