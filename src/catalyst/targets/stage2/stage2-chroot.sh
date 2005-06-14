#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/Attic/stage2-chroot.sh,v 1.10.2.1 2005/06/14 19:13:38 wolf31o2 Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

if [ -n "${clst_CCACHE}" ]
then
	export clst_myfeatures="${clst_myfeatures} ccache"
	emerge -b -k --oneshot --nodeps ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gnome -gtk" emerge -b -k --oneshot --nodeps distcc || exit 1
fi
										
if [ -n "${clst_PKGCACHE}" ]
then
	export bootstrap_opts="-r"
fi

if [ -n "${clst_FETCH}" ]
then
	export bootstrap_opts="-f"
fi

GRP_STAGE23_USE="$(portageq envvar GRP_STAGE23_USE)"


## setup the environment
export FEATURES="${clst_myfeatures}"

if [ "${clst_VERBOSE}" ]
then
	/usr/portage/scripts/bootstrap.sh -p ${bootstrap_opts}
	echo "Press any key within 15 seconds to pause the build..."
	read -s -t 15 -n 1
	if [ $? -eq 0 ]
	then
		echo "Press any key to continue..."
		read -s -n 1
	fi
fi

## START BUILD
/usr/portage/scripts/bootstrap.sh ${bootstrap_opts} || exit 1
