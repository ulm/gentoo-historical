#!/bin/bash
#
# $Header: /var/cvsroot/gentoo/admin/www.gentoo.org/scripts/mirrors.sh,v 1.6 2003/03/16 09:02:22 rajiv Exp $
#
# this script creates lists of our (rsync) mirrors.
# the list is used by mirrorselect.

# to get WEBROOT and WEBSCRIPTS defined
source ~/.bashrc

[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1

echo "# Gentoo rsync mirrors - <http://www.gentoo.org/>" > ${WEBROOT}/dyn/rsync-mirrors.txt
echo -n "# Last updated: " >> ${WEBROOT}/dyn/rsync-mirrors.txt
date >> ${WEBROOT}/dyn/rsync-mirrors.txt
echo "#" >> ${WEBROOT}/dyn/rsync-mirrors.txt
host rsync.gentoo.org | awk -F" " '{print $4}' | sort >> ${WEBROOT}/dyn/rsync-mirrors.txt
