#!/bin/bash
[ -z "${GENTOO_WEB_DOCROOT}" ] && echo "\$GENTOO_WEB_DOCROOT not set; exiting" && exit 1
echo 'Syncing up images to ibiblio...'
rsync --delete -ae ssh ${GENTOO_WEB_DOCROOT}/../images/ drobbins@login.ibiblio.org:web-gentoo/images/
echo "Images synchronized."
