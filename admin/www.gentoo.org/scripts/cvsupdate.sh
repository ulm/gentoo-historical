#!/bin/sh
#
# This script runs periodic cvs updates of the www.gentoo.org web site.
#
# AUTHOR: Kurt Lieber <klieber@gentoo.org>
# VERSION: 0.1
# DATE: April 11, 2003
#
######################################################################

source ~/.bashrc

cd ${GENTOO_WEB_DOCROOT}
cvs -z0 -Q update -dP

# now get the images
cd ${GENTOO_WEB_DOCROOT}/../images/
cvs -z0 -Q update -dP

#done
