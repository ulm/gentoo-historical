#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/Attic/stage2-chroot.sh,v 1.19 2006/10/02 20:41:54 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures
setup_myemergeopts

# Setup the environment
export FEATURES="${clst_myfeatures} nodoc noman noinfo"

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

