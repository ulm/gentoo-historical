#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/Attic/stage3.sh,v 1.13 2004/04/12 14:38:26 zhen Exp $

case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;

	run)
		if [ -n "${clst_ENVSCRIPT}" ]
		then
			cp "${clstr_ENVSCRIPT}" ${clst_chroot_path}/tmp/envscript
		fi

		cp ${clst_sharedir}/targets/stage3/stage3-chroot.sh ${clst_chroot_path}/tmp	
		${clst_CHROOT} ${clst_chroot_path} /tmp/stage3-chroot.sh
		rm -f ${clst_chroot_path}/tmp/stage3-chroot.sh
		[ $? -ne 0 ] && exit 1
	;;

	preclean)
		cp ${clst_sharedir}/targets/stage3/stage3-preclean-chroot.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/stage3-preclean-chroot.sh
		rm -rf ${clst_chroot_path}/tmp/stage3-preclean-chroot.sh
		[ $? -ne 0 ] && exit 1
	;;

	clean)
		exit 0
	;;
	
	*)
		exit 1
	;;

esac
exit 0
