#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/Attic/grp-preclean-chroot.sh,v 1.10 2006/01/17 19:30:45 wolf31o2 Exp $

. /tmp/chroot-functions.sh
update_env_settings
cleanup_distcc

gconftool-2 --shutdown
