#!/bin/bash
#
# $Header: /var/cvsroot/gentoo/admin/www.gentoo.org/scripts/mirrors.sh,v 1.2 2003/03/14 01:15:10 rajiv Exp $
#
# this script creates lists of our (rsync) mirrors.
# the list is used by mirrorselect.

[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1

echo ">>> Updatine rsync mirrors text list..."

echo "# Gentoo rsync mirrors" > ${WEBROOT}/dyn/rsync-mirrors.txt
echo -n "# Last updated: " >> ${WEBROOT}/dyn/rsync-mirrors.txt
date >> ${WEBROOT}/dyn/rsync-mirrors.txt
echo "#" >> ${WEBROOT}/dyn/rsync-mirrors.txt
host rsync.gentoo.org | awk -F" " '{print $4}' >> ${WEBROOT}/dyn/rsync-mirrors.txt

echo ">>> Done."
