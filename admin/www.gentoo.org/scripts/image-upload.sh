#!/bin/bash
[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1
echo 'Syncing up images to ibiblio...'
rsync --delete -ave ssh ${WEBROOT}/../images/ drobbins@login.ibiblio.org:gentoo/images/
echo "Images synchronized."
