#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/post-kmerge.sh,v 1.4 2005/02/28 23:21:09 wolf31o2 Exp $

/usr/sbin/env-update
source /etc/profile

#emerge -C genkernel

/sbin/depscan.sh
find /lib/modules -name modules.dep -exec touch {} \;
