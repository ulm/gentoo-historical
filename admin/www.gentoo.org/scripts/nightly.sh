#!/bin/bash
echo ">>> Starting Web update..."

#to get GENTOO_WEB_DOCROOT and GENTOO_WEB_SCRIPTS defined
source ~/.bashrc

#to get all arches in our package listing:
export ACCEPT_KEYWORDS="x86 ppc alpha sparc hppa mips arm"
export PORTDIR="$HOME/gentoo-x86"
export FEATURES="-cvs -digest"

[ -z "${GENTOO_WEB_DOCROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1
[ -z "${GENTOO_WEB_SCRIPTS}" ] && echo "\$GENTOO_WEB_SCRIPTS not set; exiting" && exit 1

${GENTOO_WEB_SCRIPTS}/cvs-page.sh
${GENTOO_WEB_SCRIPTS}/use-index.py
# no idea why the next script was being run, so commenting it out until someone complains
#${GENTOO_WEB_SCRIPTS}/site-archive.sh
${GENTOO_WEB_SCRIPTS}/news-index.sh
# no idea why the next script was being run, so commenting it out until someone complains
#${GENTOO_WEB_SCRIPTS}/doc-tarball.sh
${GENTOO_WEB_SCRIPTS}/icons2xml_v2.pl  
# this script is called every 15 minutes now via crontab, so we'll comment it out here
#${GENTOO_WEB_SCRIPTS}/cvs-repo-update.sh

# this script takes a while (5+ minutes) to run, so leave it near the end
${GENTOO_WEB_SCRIPTS}/distrowatch.sh

# this script also takes a while to run since it uploads the log files to a central server
${GENTOO_WEB_SCRIPTS}/rsync-weblogs.sh

# this script takes the longest of all -- ~1 hour or more.  leave it as the *very* last one
#${GENTOO_WEB_SCRIPTS}/pkgs.py

echo ">>> Nightly Web update done."
