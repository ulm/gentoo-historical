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
${WEBSCRIPTS}/pkgs.py
${WEBSCRIPTS}/use-index.py
${WEBSCRIPTS}/site-archive.sh
${WEBSCRIPTS}/news-index.sh
${WEBSCRIPTS}/doc-tarball.sh
${WEBSCRIPTS}/icons2xml.pl > /home/httpd/gentoo/xml/htdocs/dyn/icons.xml

# this script takes a while (5+ minutes) to run, so leave it as the last one.
${WEBSCRIPTS}/distrowatch.sh


echo ">>> Nightly Web update done."
