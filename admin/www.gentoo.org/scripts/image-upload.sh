#!/bin/bash
[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1
echo 'Syncing up images to ibiblio...'
rsync --delete -ae ssh ${WEBROOT}/../images/ drobbins@login.ibiblio.org:web-gentoo/images/
echo "Images synchronized."
