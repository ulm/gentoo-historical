#!/bin/bash									
[ -z ${WEBROOT} ] && echo "Webroot is not set, exiting" && exit 1
TAR="/bin/tar"

install -d ${WEBROOT}/dyn/doc-snapshots

for x in cs de en es fr it ja kr nl
do
cd ${WEBROOT}/doc
${TAR} cjf ${WEBROOT}/dyn/doc-snapshots/docs-latest-${x}.tar.bz2 ${x}/ --exclude CVS 
done

