#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/Attic/grp-preclean-chroot.sh,v 1.7 2005/04/04 17:48:33 rocket Exp $


. /tmp/chroot-functions.sh
update_env_settings

gconftool-2 --shutdown
