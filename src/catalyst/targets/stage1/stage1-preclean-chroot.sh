#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/stage1-preclean-chroot.sh,v 1.11 2006/10/02 20:41:54 wolf31o2 Exp $

. /tmp/chroot-functions.sh

# Now, some finishing touches to initialize gcc-config....
unset ROOT

setup_gcc
setup_binutils

# Stage1 is not going to have anything in zoneinfo, so save our Factory timezone
if [ -d /usr/share/zoneinfo ]
then
	rm -f /etc/localtime
	cp /usr/share/zoneinfo/Factory /etc/localtime
else
	echo UTC > /etc/TZ
fi

#if [ -n "${clst_CCACHE}" ]
#then
#	run_emerge -C dev-util/ccache || exit 1
#fi

#if [ -n "${clst_DISTCC}" ]
#then
#	run_emerge -C sys-devel/distcc || exit 1
#fi

#cleanup_distcc
