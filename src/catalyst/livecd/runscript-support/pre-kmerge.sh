#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/pre-kmerge.sh,v 1.11 2005/03/07 21:14:42 wolf31o2 Exp $

/usr/sbin/env-update
source /etc/profile

if [ ! -x /usr/share/genkernel/genkernel ]
then
	emerge -k -b genkernel
fi

install -d /usr/portage/packages/gk_binaries
rm -f /usr/src/linux

sed -i 's/uchi-hcd/uhci-hcd/' /usr/share/genkernel/x86/modules_load

if [ "${clst_livecd_type}" = "gentoo-release-minimal" ] \
|| [ "${clst_livecd_type}" = "gentoo-release-universal" ]
then
	sed -i 's/initramfs_data.cpio.gz /initramfs_data.cpio.gz -r 1024x768 /'\
	/usr/share/genkernel/genkernel
fi
