#!/bin/bash
#to get WEBROOT defined...
echo ">>> Starting nightly Web update..."
source ~/.bashrc
${WEBROOT}/../scripts/cvs-page.sh
${WEBROOT}/../scripts/pkgs.py
${WEBROOT}/../scripts/use-index.sh
