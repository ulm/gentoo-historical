#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/netboot-base/tarball.sh,v 1.1 2004/10/06 16:06:38 vapier Exp $

rm -f filelist
for d in etc sbin ; do
	find ./${d} -type f -a ! -path '*/CVS/*' >> filelist
done
date=$(date +%Y%m%d)
tar -jpcf netboot-base-${date}.tar.bz2 --files-from=filelist
rm -f filelist
