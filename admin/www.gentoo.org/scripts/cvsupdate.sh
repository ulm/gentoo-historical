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

cd ${WEBROOT}
cvs update -dPQ

# now get the images
cd ${WEBROOT}/../images/
cvs update -dPQ

#done
