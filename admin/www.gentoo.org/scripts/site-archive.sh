#!/bin/bash
[ -z "${GENTOO_WEB_DOCROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1
install -d ${GENTOO_WEB_DOCROOT}/dyn/arch
cd ${GENTOO_WEB_DOCROOT}/..
tar cvzf ${GENTOO_WEB_DOCROOT}/dyn/arch/xml-guide-latest.tar.gz --exclude htdocs/dyn htdocs

