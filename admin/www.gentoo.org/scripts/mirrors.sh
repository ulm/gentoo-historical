#!/bin/bash
#
# $Header: /var/cvsroot/gentoo/admin/www.gentoo.org/scripts/mirrors.sh,v 1.4 2003/03/14 02:40:54 rajiv Exp $
#
# this script creates lists of our (rsync) mirrors.
# the list is used by mirrorselect.

# to get WEBROOT and WEBSCRIPTS defined
source ~/.bashrc

[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1

echo ">>> Updating rsync mirrors text list..."

echo "# Gentoo rsync mirrors - <http://www.gentoo.org/>" > ${WEBROOT}/dyn/rsync-mirrors.txt
echo -n "# Last updated: " >> ${WEBROOT}/dyn/rsync-mirrors.txt
date >> ${WEBROOT}/dyn/rsync-mirrors.txt
echo "#" >> ${WEBROOT}/dyn/rsync-mirrors.txt
host rsync.gentoo.org | awk -F" " '{print $4}' >> ${WEBROOT}/dyn/rsync-mirrors.txt

echo ">>> Done."
