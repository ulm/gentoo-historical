#!/bin/bash
#to get WEBROOT defined...
echo ">>> Starting nightly Web update..."
source ~/.bashrc
#to get all arches in our package listing:
export ACCEPT_KEYWORDS="x86 ppc alpha sparc sparc64"
${WEBROOT}/../scripts/cvs-page.sh
${WEBROOT}/../scripts/pkgs.py
${WEBROOT}/../scripts/use-index.sh
