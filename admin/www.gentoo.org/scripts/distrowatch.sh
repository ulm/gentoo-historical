#!/bin/bash
#
# $Header: /var/cvsroot/gentoo/admin/www.gentoo.org/scripts/distrowatch.sh,v 1.5 2003/04/04 19:55:19 drobbins Exp $
#
# this file creates a list of packages from the Portage tree for distrowatch
#

[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1
[ -z "${WEBSCRIPTS}" ] && echo "\$WEBSCRIPTS not set; exiting" && exit 1

echo ">>> Updating distrowatch lists..."

#Note: distrowatch lists non-x86 packages like yaboot, so I'm now including all arches (drobbins, 04/04/2003)
STABLE_ARCHES="x86 ppc sparc mips hppa alpha"
UNSTABLE_ARCHES="~x86 ~ppc ~sparc ~mips ~hppa ~alpha"
# gentoo_pkglist_x86.txt contains the stable branch packages
echo ">>> Generating stable package list..."
ACCEPT_KEYWORDS="$STABLE_ARCHES" ${WEBSCRIPTS}/pkglist.py 1> ${WEBROOT}/dyn/gentoo_pkglist_x86.txt 2> /dev/null

# gentoo_pkglist_X86.txt contains the unstable branch packages (note capital X)
echo ">>> Generating unstable package list..."
ACCEPT_KEYWORDS="$STABLE_ARCHES $UNSTABLE_ARCHES" ${WEBSCRIPTS}/pkglist.py 1> ${WEBROOT}/dyn/gentoo_pkglist_X86.txt 2> /dev/null

echo ">>> Done."
