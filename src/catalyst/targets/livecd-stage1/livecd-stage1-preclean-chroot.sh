#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage1/Attic/livecd-stage1-preclean-chroot.sh,v 1.5 2005/01/28 18:37:23 wolf31o2 Exp $

/usr/sbin/env-update
source /etc/profile

killall -9 gconfd-2
