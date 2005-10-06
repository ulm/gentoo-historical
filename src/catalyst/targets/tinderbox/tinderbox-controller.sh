#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/tinderbox/Attic/tinderbox-controller.sh,v 1.4 2005/10/06 20:56:54 wolf31o2 Exp $

. ${clst_sharedir}/targets/support/functions.sh

case $1 in
	run)
		shift
		exec_in_chroot ${clst_sharedir}/targets/tinderbox/tinderbox-chroot.sh
	;;

	preclean)
		#exec_in_chroot ${clst_sharedir}/targets/tinderbox/tinderbox-preclean-chroot.sh
		delete_from_chroot /tmp/chroot-functions.sh
	;;

	clean)
		exit 0
	;;

	*)
		exit 1
	;;
	
esac

exit $?
