#!/bin/bash
[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1
install -d ${WEBROOT}/dyn/arch
cd ${WEBROOT}/..
tar cvzf ${WEBROOT}/dyn/arch/xml-guide-latest.tar.gz --exclude htdocs/dyn htdocs

