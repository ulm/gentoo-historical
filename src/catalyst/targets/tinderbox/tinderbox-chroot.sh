#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/tinderbox/Attic/tinderbox-chroot.sh,v 1.9 2005/01/26 21:59:40 wolf31o2 Exp $

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

# setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"

# START THE BUILD
USE="build" emerge portage
#turn off auto-use:
export USE_ORDER="env:pkg:conf:defaults"	
#back up pristine system
rsync -avx --exclude "/root/" --exclude "/tmp/" --exclude "/usr/portage/" / /tmp/rsync-bak/ 

for x in ${clst_tinderbox_packages}
do
	if [ -n "${clst_VERBOSE}" ]
	then
		emerge --usepkg --buildpkg -vp $x
		sleep 5
	fi
	
	emerge --usepkg --buildpkg $x
	
	if [ "$?" != "0" ]
	then
		echo "! $x" >> /tmp/tinderbox.log	
	else
		echo "$x" >> /tmp/tinderbox.log
	fi
	echo "Syncing from original pristine tinderbox snapshot..."
	rsync -avx --delete --exclude "/root/*" --exclude "/tmp/" --exclude "/usr/portage/*" /tmp/rsync-bak/ /
done
