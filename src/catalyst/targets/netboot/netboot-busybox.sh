#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/Attic/netboot-busybox.sh,v 1.5.2.1 2005/07/05 21:47:46 wolf31o2 Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

# setup our environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"
export USE_ORDER="env:pkg:conf:defaults"	

# Use the catalyst config
export USE="netboot make-busybox-symlinks"

if [ ! -z "${1}" ]
then
	export USE="${USE} savedconfig"
	# Do not use package for busybox since the config can change
	ROOT=${IMAGE_PATH} emerge --nodeps busybox || exit 1
else
	ROOT=${IMAGE_PATH} emerge --nodeps ${clst_myemergeopts} busybox || exit 1

fi

