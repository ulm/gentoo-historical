#!/bin/bash
echo ">>> Starting Web update..."

#to get WEBROOT and WEBSCRIPTS defined
source ~/.bashrc

#to get all arches in our package listing:
export ACCEPT_KEYWORDS="x86 ppc alpha sparc hppa mips arm"
export PORTDIR="$HOME/gentoo-x86"
export FEATURES="-cvs -digest"

[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1
[ -z "${WEBSCRIPTS}" ] && echo "\$WEBSCRIPTS not set; exiting" && exit 1

${WEBSCRIPTS}/cvs-page.sh
${WEBSCRIPTS}/use-index.py
# no idea why the next script was being run, so commenting it out until someone complains
#${WEBSCRIPTS}/site-archive.sh
${WEBSCRIPTS}/news-index.sh
# no idea why the next script was being run, so commenting it out until someone complains
#${WEBSCRIPTS}/doc-tarball.sh
${WEBSCRIPTS}/icons2xml_v2.pl  
# this script is called every 15 minutes now via crontab, so we'll comment it out here
#${WEBSCRIPTS}/cvs-repo-update.sh

# this script takes a while (5+ minutes) to run, so leave it near the end
${WEBSCRIPTS}/distrowatch.sh

# this script also takes a while to run since it uploads the log files to a central server
${WEBSCRIPTS}/rsync-weblogs.sh

# this script takes the longest of all -- ~1 hour or more.  leave it as the *very* last one
${WEBSCRIPTS}/pkgs.py

echo ">>> Nightly Web update done."
