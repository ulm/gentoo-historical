#!/bin/bash
#
# $Header: /var/cvsroot/gentoo/admin/www.gentoo.org/scripts/distrowatch.sh,v 1.7 2004/02/03 17:19:50 tigger Exp $
#
# this file creates a list of packages from the Portage tree for distrowatch
#

if [ -d "${GENTOO_WEB_SCRIPTS}" -a -d "${GENTOO_WEB_DOCROOT}" ]; then
	#Note: distrowatch lists non-x86 packages like yaboot, so I'm now including all arches (drobbins, 04/04/2003)
	STABLE_ARCHES="x86 ppc sparc mips hppa alpha"
	UNSTABLE_ARCHES="~x86 ~ppc ~sparc ~mips ~hppa ~alpha"
	# gentoo_pkglist_x86.txt contains the stable branch packages
	ACCEPT_KEYWORDS="$STABLE_ARCHES" ${GENTOO_WEB_SCRIPTS}/pkglist.py 1> ${GENTOO_WEB_DOCROOT}/dyn/gentoo_pkglist_x86.txt 2> /dev/null
	
	# gentoo_pkglist_X86.txt contains the unstable branch packages (note capital X)
	ACCEPT_KEYWORDS="$STABLE_ARCHES $UNSTABLE_ARCHES" ${GENTOO_WEB_SCRIPTS}/pkglist.py 1> ${GENTOO_WEB_DOCROOT}/dyn/gentoo_pkglist_X86.txt 2> /dev/null
else
	echo "GENTOO_WEB_SCRIPTS and/or GENTOO_WEB_DOCROOT were not set or were not directories" >&2
	exit 1
fi
