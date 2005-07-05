#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/Attic/grp-controller.sh,v 1.3 2005/07/05 21:53:41 wolf31o2 Exp $
. ${clst_sharedir}/targets/support/functions.sh

case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;
	run)
		shift
		export clst_grp_type=$1
		shift
		export clst_grp_target=$1
		shift

		export clst_grp_packages="$*"
		exec_in_chroot ${clst_sharedir}/targets/grp/grp-chroot.sh
	;;

	preclean)
		exec_in_chroot ${clst_sharedir}/targets/grp/grp-preclean-chroot.sh
	;;

	clean)
		exit 0
	;;
	
	*)
		exit 1
	;;

esac
exit $?
