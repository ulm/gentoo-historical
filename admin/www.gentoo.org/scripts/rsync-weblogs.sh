#!/bin/bash
#
# rsync weblogs to the central server
#
# Kurt Lieber
# klieber@gentoo.org
#
# v0.1
# 
#######################################

RSYNC="/usr/bin/rsync"
LOCALDIR="/var/log/apache/*"
RSYNCSERVER="monitor.gentoo.org::web-logs"
REMOTEDIR="/$HOSTNAME/"
RSYNCOPTIONS=""

${RSYNC} ${RSYNCOPTIONS} ${LOCALDIR} ${RSYNCSERVER}${REMOTEDIR}

