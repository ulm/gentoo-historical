#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/Attic/stage3-chroot.sh,v 1.24 2005/12/08 15:16:48 rocket Exp $

. /tmp/chroot-functions.sh
check_portage_version

update_env_settings

setup_myfeatures
setup_myemergeopts


# setup the build environment
export FEATURES="${clst_myfeatures}"
export USE="${USE} ${clst_HOSTUSE}"

## START BUILD
# portage needs to be merged manually with USE="build" set to avoid frying our
# make.conf. emerge system could merge it otherwise.

setup_portage

run_emerge "-e system"
