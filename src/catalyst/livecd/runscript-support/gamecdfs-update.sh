#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/gamecdfs-update.sh,v 1.6.2.2 2005/04/09 15:52:20 wolf31o2 Exp $

# we grab our configuration
source /tmp/gamecd.conf || exit 1

# here we replace out game information into several files
sed -i -e "s:livecd:gamecd:" /etc/hosts
sed -i -e "s:##GAME_NAME:${GAME_NAME}:" /etc/motd

# here we setup our xinitrc
echo "exec ${GAME_EXECUTABLE}" > /etc/X11/xinit/xinitrc

# we add spind to default here since we don't want the CD to spin down
rc-update add spind default
rc-update add x-setup default

# This is my hack to reduce tmpfs usage
mkdir -p /usr/livecd/db/pkg/x11-base
mv /var/db/pkg/x11-base/xorg* /usr/livecd/db/pkg/x11-base

# This should help setup our PORTAGE_TMPDIR
echo 'PORTAGE_TMPDIR="/tmp"' >> /etc/make.conf
