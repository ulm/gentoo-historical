#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/pre-kmerge.sh,v 1.12.2.1 2005/04/09 12:50:11 wolf31o2 Exp $

/usr/sbin/env-update
source /etc/profile

CONFIG_PROTECT="-*" USE="livecd" emerge --oneshot --nodeps genkernel

install -d /usr/portage/packages/gk_binaries
rm -f /usr/src/linux

if [ "${clst_livecd_type}" = "gentoo-release-minimal" ] \
|| [ "${clst_livecd_type}" = "gentoo-release-universal" ]
then
	sed -i 's/initramfs_data.cpio.gz /initramfs_data.cpio.gz -r 1024x768 /'\
	/usr/share/genkernel/genkernel
fi
