#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/Attic/netboot-busybox.sh,v 1.1 2004/10/06 01:34:29 zhen Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

if [ -n "${clst_DISTCC}" ]
then   
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gnome -gtk" emerge --oneshot --nodeps -b -k distcc || exit 1
fi

## setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"

## START BUILD
export USE_ORDER="env:conf:defaults"	

# Use the catalyst config
export USE="savedconfig make-busybox-symlinks"
mkdir -pv ${IMAGE_PATH}
ROOT=${IMAGE_PATH} emerge --nodeps ${clst_emergeopts} busybox || exit 1

# Remove portage's unneeded files
rm -R ${IMAGE_PATH}/etc
rm -R ${IMAGE_PATH}/tmp
rm -R ${IMAGE_PATH}/usr
rm -R ${IMAGE_PATH}/var
