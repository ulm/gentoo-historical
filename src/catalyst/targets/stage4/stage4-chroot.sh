#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

. /tmp/chroot-functions.sh

check_portage_version
update_env_settings

setup_myfeatures
setup_myemergeopts

## setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"

## START BUILD
setup_portage
#turn off auto-use:
export USE_ORDER="env:pkg:conf:defaults"	

echo "Bringing system up to date using profile specific use flags"
GRP_STAGE23_USE="$(portageq envvar GRP_STAGE23_USE)"
export USE="-* ${clst_HOSTUSE} ${GRP_STAGE23_USE}"
run_emerge -u system


echo "Emerging packages using stage4 use flags"
if [ -n "${clst_stage4_use}" ]
then 
	export USE="-* ${clst_HOSTUSE} ${GRP_STAGE23_USE}"
else	
	USE="${clst_stage4_use}"
fi

run_emerge "${clst_packages}"
