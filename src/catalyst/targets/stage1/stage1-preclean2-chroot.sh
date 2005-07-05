#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/stage1-preclean2-chroot.sh,v 1.10.2.3 2005/07/05 21:47:46 wolf31o2 Exp $
		
# now, some finishing touches to initialize gcc-config....
unset ROOT

if [ -x /usr/bin/gcc-config ]
then
	mythang=$( cd /etc/env.d/gcc; ls ${clst_CHOST}-* | head -n 1 )
	if [ -z "${mythang}" ]
	then
		mythang=1
	fi
	gcc-config ${mythang}
fi

if [ -x /usr/bin/binutils-config ]
then
	mythang=$( cd /etc/env.d/binutils; ls ${clst_CHOST}-* | head -n 1 )
	if [ -z "${mythang}" ]
	then
		mythang=1
	fi
	binutils-config ${mythang}
fi

/usr/sbin/env-update
source /etc/profile

# stage1 is not going to have anything in zoneinfo, so save our Factory timezone
if [ -d /usr/share/zoneinfo ] ; then
	rm -f /etc/localtime
	cp /usr/share/zoneinfo/Factory /etc/localtime
else
	echo UTC > /etc/TZ
fi

# this cleans out /var/db, but leaves behind files portage needs for removal
#find /var/db/pkg -type f | grep -v '\(COUNTER\|CONTENTS\|SLOT\|ebuild\)' | xargs rm -f
