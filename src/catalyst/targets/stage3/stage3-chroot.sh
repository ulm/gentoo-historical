#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/Attic/stage3-chroot.sh,v 1.28 2006/10/02 20:41:54 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures
setup_myemergeopts

# Setup the build environment
export FEATURES="${clst_myfeatures}"
export USE="${USE} ${clst_HOSTUSE}"

## START BUILD
# portage needs to be merged manually with USE="build" set to avoid frying our
# make.conf. emerge system could merge it otherwise.

setup_portage

run_emerge "-e system"
rm -f /var/lib/portage/world
touch /var/lib/portage/world
