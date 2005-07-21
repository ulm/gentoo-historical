#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/pre-kmerge.sh,v 1.12.2.6 2005/07/21 14:23:47 rocket Exp $

/usr/sbin/env-update
source /etc/profile

CONFIG_PROTECT="-*" USE="livecd" emerge --oneshot --nodeps genkernel

if [ -n "${clst_CCACHE}" ]
then
	emerge --oneshot --nodeps -b -k ccache || exit 1
fi



install -d /usr/portage/packages/gk_binaries
rm -f /usr/src/linux

if [ "${clst_livecd_type}" = "gentoo-release-minimal" ] \
|| [ "${clst_livecd_type}" = "gentoo-release-universal" ]
then
	case ${clst_mainarch} in
		amd64|x86)
			sed -i 's/initramfs_data.cpio.gz /initramfs_data.cpio.gz -r 1024x768 /'	/usr/share/genkernel/genkernel
		;;
	esac
fi
