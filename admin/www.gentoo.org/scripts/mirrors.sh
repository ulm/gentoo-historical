#!/bin/bash
#
# $Header: /var/cvsroot/gentoo/admin/www.gentoo.org/scripts/mirrors.sh,v 1.1 2003/03/14 01:07:39 rajiv Exp $
#
# this script creates lists of our (rsync) mirrors.
# the list is used by mirrorselect.

[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1

host rsync.gentoo.org | awk -F" " '{print $4}' > ${WEBROOT}/dyn/rsync-mirrors.txt
