#!/bin/sh
#
# This script grabs a recent copy of various cvs repositories
# so that viewcvs can do web views of them
#
# AUTHOR: Rob Holland <tigger@gentoo.org>
# VERSION: 1.0
# DATE: 20th Janurary 2004
#
######################################################################

source ~/.bashrc

RSYNC_ARGS="--rsh=ssh -a --delete --delete-excluded"

if [ -d "${GENTOO_CVS_RAW}" ]; then
	# grab a recent copy of the cvs modules for viewcvs

	rsync ${RSYNC_ARGS} cvs.gentoo.org:/home/cvsroot/gentoo/ \
	--exclude /home/cvsroot/gentoo/admin/ ${GENTOO_CVS_RAW}/gentoo/

	rsync ${RSYNC_ARGS} cvs.gentoo.org:/home/cvsroot/gentoo-x86/ \
	${GENTOO_CVS_RAW}/gentoo-x86/

	rsync ${RSYNC_ARGS} cvs.gentoo.org:/home/cvsroot/gentoo-src/ \
	${GENTOO_CVS_RAW}/gentoo-src/
else
	echo "Either GENTOO_CVS_RAW isn't set or it isn't a directory" >&2
	exit 1
fi
