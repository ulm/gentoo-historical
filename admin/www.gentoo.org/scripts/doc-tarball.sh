#!/bin/bash									
[ -z ${GENTOO_WEB_DOCROOT} ] && echo "Webroot is not set, exiting" && exit 1
TAR="/bin/tar"

install -d ${GENTOO_WEB_DOCROOT}/dyn/doc-snapshots

for x in cs de en es fr it ja kr nl
do
cd ${GENTOO_WEB_DOCROOT}/doc
${TAR} cjf ${GENTOO_WEB_DOCROOT}/dyn/doc-snapshots/docs-latest-${x}.tar.bz2 ${x}/ --exclude CVS 
done

