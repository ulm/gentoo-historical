#!/bin/bash
# Copyright 1999-2002 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# Author:  Martin Schlemmer <azarah@gentoo.org>
# $Header: /var/cvsroot/gentoo/src/livecd/profiles/lw-ut2003/aux-files/Attic/depscan.sh,v 1.1 2003/10/19 03:46:49 livewire Exp $

source /etc/init.d/functions.sh

ebegin "Caching service dependencies"


lookbusy() {
        local type
        type=${1}; shift
        for i in "$@"
        do  echo -n $GOOD" * Loading Services" $i;echo -n -e "\r";
        usleep 600000 ;
done
echo $WARN" * Loading Services 100%"
echo -n $NORMAL
}

lookbusy '10%' '20%' '30%' '40%' '50%' '60%' '70%' '80%' '90%' '100%'

/bin/gawk -v SVCDIR="${svcdir}" \
	-f /lib/rcscripts/awk/functions.awk \
	-f /lib/rcscripts/awk/cachedepends.awk

cd /etc/init.d

bash ${svcdir}/depcache | \
	/bin/gawk -v SVCDIR="${svcdir}" \
		-v DEPTYPES="${deptypes}" \
		-v ORDTYPES="${ordtypes}" \
		-f /lib/rcscripts/awk/functions.awk \
		-f /lib/rcscripts/awk/gendepends.awk

eend $? "Failed to cache service dependencies"


# vim:ts=4
