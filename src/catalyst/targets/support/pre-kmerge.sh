#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

. /tmp/chroot-functions.sh

update_env_settings

export USE="livecd"
run_emerge --oneshot genkernel

install -d /usr/portage/packages/gk_binaries

# Setup case structure for livecd_type
case ${clst_livecd_type} in
	gentoo-release-minimal | gentoo-release-universal)
		case ${clst_mainarch} in
			amd64|x86)
				sed -i 's/initramfs_data.cpio.gz /initramfs_data.cpio.gz -r 1024x768 /' /usr/share/genkernel/genkernel
			;;
		esac
	;;
esac

