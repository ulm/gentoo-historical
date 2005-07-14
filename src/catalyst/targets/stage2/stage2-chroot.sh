#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/Attic/stage2-chroot.sh,v 1.10.2.6 2005/07/14 15:49:03 wolf31o2 Exp $

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
	mkdir -p /etc/distcc
	echo "${clst_distcc_hosts}" > /etc/distcc/hosts
fi
										
if [ -n "${clst_PKGCACHE}" ]
then
	export bootstrap_opts="-r"
fi

if [ -n "${clst_FETCH}" ]
then
	export bootstrap_opts="-f"
fi

## setup the environment
export FEATURES="${clst_myfeatures}"

if [ "${clst_VERBOSE}" ]
then
	/usr/portage/scripts/bootstrap.sh -t ${bootstrap_opts}
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
