#!/bin/bash
#
# $Header: /var/cvsroot/gentoo/admin/www.gentoo.org/scripts/distrowatch.sh,v 1.4 2003/03/14 05:03:14 rajiv Exp $
#
# this file creates a list of packages from the Portage tree for distrowatch
#

[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1
[ -z "${WEBSCRIPTS}" ] && echo "\$WEBSCRIPTS not set; exiting" && exit 1

echo ">>> Updating distrowatch lists..."

# gentoo_pkglist_x86.txt contains the stable branch packages
echo ">>> Generating stable package list..."
ACCEPT_KEYWORDS="x86" ${WEBSCRIPTS}/pkglist.py 1> ${WEBROOT}/dyn/gentoo_pkglist_x86.txt 2> /dev/null

# gentoo_pkglist_X86.txt contains the unstable branch packages (note capital X)
echo ">>> Generating unstable package list..."
ACCEPT_KEYWORDS="~x86" ${WEBSCRIPTS}/pkglist.py 1> ${WEBROOT}/dyn/gentoo_pkglist_X86.txt 2> /dev/null

echo ">>> Done."
