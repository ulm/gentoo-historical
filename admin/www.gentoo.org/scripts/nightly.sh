#!/bin/bash
echo ">>> Starting Web update..."
source ~/.bashrc
#to get WEBROOT defined...
#to get all arches in our package listing:
export ACCEPT_KEYWORDS="x86 ppc alpha sparc sparc64"
export PORTDIR="/home/gweb/gentoo-x86"
export FEATURES="-cvs -digest"
${WEBROOT}/../scripts/cvs-page.sh
${WEBROOT}/../scripts/pkgs.py
${WEBROOT}/../scripts/use-index.py
${WEBROOT}/../scripts/site-archive.sh
${WEBROOT}/../scripts/news-index.sh
