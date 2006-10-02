#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/Attic/stage2-preclean-chroot.sh,v 1.11 2006/10/02 20:41:54 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

if [ -n "${clst_CCACHE}" ]
then
	run_emerge -C dev-util/ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then
	run_emerge -C sys-devel/distcc || exit 1
fi

cleanup_distcc

rm -f /var/log/emerge.log
