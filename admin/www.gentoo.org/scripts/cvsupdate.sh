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

# we actually want to go to gentoo/xml instead of gentoo/xml/htdocs
# this ensures we update the gentoo/xml/images directory, too
cd ${WEBROOT}/../
cvs update -dPQ

#done
