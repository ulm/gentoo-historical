#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/Attic/stage2-preclean-chroot.sh,v 1.5 2005/04/04 17:48:33 rocket Exp $

. /tmp/chroot-functions.sh
update_env_settings

export CONFIG_PROTECT="-*"

if [ -n "${clst_CCACHE}" ]
then
	emerge -C dev-util/ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then
	emerge -C sys-devel/distcc || exit 1
fi
