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
RSYNC_ARGS="--rsh=ssh -a"

# create the directory if this is the first time this has run
mkdir -p ${WORKDIR}/cvsroot

# grab a recent copy of the cvs modules for viewcvs

rsync ${RSYNC_ARGS} cvs.gentoo.org:/home/cvsroot/gentoo \
--exclude /home/cvsroot/gentoo/admin/ ${WORKDIR}/cvsroot/gentoo

rsync ${RSYNC_ARGS} cvs.gentoo.org:/home/cvsroot/gentoo-x86 \
${WORKDIR}/cvsroot/gentoo-x86

rsync ${RSYNC_ARGS} cvs.gentoo.org:/home/cvsroot/gentoo-src \
${WORKDIR}/cvsroot/gentoo-src

#done
