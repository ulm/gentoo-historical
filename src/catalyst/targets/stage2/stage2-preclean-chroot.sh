#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/Attic/stage2-preclean-chroot.sh,v 1.2 2004/04/14 22:35:29 zhen Exp $

/usr/sbin/env-update
source /etc/profile

export CONFIG_PROTECT="-*"

if [ -n "${clst_CCACHE}" ]
then
	emerge -C dev-util/ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then
	emerge -C sys-devel/distcc || exit 1
	userdel distcc || exit 1
fi
