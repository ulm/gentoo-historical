#!/bin/sh
#
# This script grabs a recent copy of the cvs repository
#
# AUTHOR: Rob Holland <robh@gentoo.org>
# VERSION: 0.1
# DATE: July 7, 2003
#
######################################################################

source ~/.bashrc

WORKDIR=/home/httpd

# create the directory if this is the first time this has run
mkdir -p ${WORKDIR}/cvsroot

# grab a recent copy of the cvs repository
RSYNC_RSH=ssh rsync -a --exclude /home/cvsroot/gentoo/admin cvs.gentoo.org:/home/cvsroot/ ${WORKDIR}/cvsroot

#done
