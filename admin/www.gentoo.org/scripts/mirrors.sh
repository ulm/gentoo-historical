#!/bin/bash
#
# $Header: /var/cvsroot/gentoo/admin/www.gentoo.org/scripts/mirrors.sh,v 1.7 2004/02/03 17:19:50 tigger Exp $
#
# this script creates lists of our (rsync) mirrors.
# the list is used by mirrorselect.

# to get GENTOO_WEB_DOCROOT and WEBSCRIPTS defined
source ~/.bashrc

[ -z "${GENTOO_WEB_DOCROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1

echo "# Gentoo rsync mirrors - <http://www.gentoo.org/>" > ${GENTOO_WEB_DOCROOT}/dyn/rsync-mirrors.txt
echo -n "# Last updated: " >> ${GENTOO_WEB_DOCROOT}/dyn/rsync-mirrors.txt
date >> ${GENTOO_WEB_DOCROOT}/dyn/rsync-mirrors.txt
echo "#" >> ${GENTOO_WEB_DOCROOT}/dyn/rsync-mirrors.txt
host rsync.gentoo.org | awk -F" " '{print $4}' | sort >> ${GENTOO_WEB_DOCROOT}/dyn/rsync-mirrors.txt
