#!/bin/bash
[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1
cat > ${WEBROOT}/dyn/news-index.xml << EOF 
<?xml version="1.0" encoding="UTF-8"?>
<uris>
EOF
	
mydate=`date +"%d %b %Y"`
cd ${WEBROOT}
for x in `find news -iname 200*.xml | sort -r`
do
	echo "<uri>/$x</uri>" >> ${WEBROOT}/dyn/news-index.xml
done
echo "</uris>" >> ${WEBROOT}/dyn/news-index.xml
echo "News index generated :)"

