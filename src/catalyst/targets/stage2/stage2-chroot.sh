#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/Attic/stage2-chroot.sh,v 1.12 2005/06/14 19:43:26 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures
setup_myemergeopts


## setup the environment
export FEATURES="${clst_myfeatures}"
GRP_STAGE23_USE="$(portageq envvar GRP_STAGE23_USE)"

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
