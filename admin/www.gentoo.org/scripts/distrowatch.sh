#!/bin/sh
#
# this file creates a list of packages from the Portage tree
# for distrowatch to pull from.
#
#############################################################
#                                                           #
#   THE gweb ACCOUNT MUST BE ABLE TO RUN emerge sync IN     #
#   ORDER FOR THIS TO WORK                                  #
#                                                           #
#############################################################

# used for testing
#SCRIPTDIR="./"
#TARGETDIR="/tmp/"

# used for production
SCRIPTDIR="/home/httpd/scripts/"
TARGETDIR="/home/httpd/gentoo/xml/htdocs/dyn/"

# emerge sync needs to be run using sudo so gweb can do it.
sudo /usr/bin/emerge sync > /dev/null 2>&1

# gentoo_pkglist_x86.txt contains the stable branch packages
${SCRIPTDIR}pkglist.py 1> ${TARGETDIR}gentoo_pkglist_x86.txt 2> /dev/null

# wait 5 minutes to let the above stuff finish
sleep 300

# gentoo_pkglist_X86.txt contains the unstable branch packages (note capital X)
ACCEPT_KEYWORDS="~x86" ${SCRIPTDIR}pkglist.py 1> ${TARGETDIR}gentoo_pkglist_X86.txt 2> /dev/null


