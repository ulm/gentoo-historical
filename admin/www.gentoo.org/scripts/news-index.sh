#!/bin/bash
# Modified by zhen <zhen@gentoo.org> 5/1/2003 to add support for the
# arch projects subpages.

# what arches do we support?
ARCHES="ppc"

[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1
install -d ${WEBROOT}/dyn

# for backwards compatibility, create the main www.gentoo.org newspage.
	cat > ${WEBROOT}/dyn/news-index.xml << EOF 
<?xml version="1.0" encoding="UTF-8"?>
<uris>
EOF

# now do all of the subpages
for x in ${ARCHES}
do
	cat > ${WEBROOT}/dyn/${x}-news-index.xml << EOF 
<?xml version="1.0" encoding="UTF-8"?>
<uris>
EOF
done
	
mydate=`date +"%d %b %Y"`

# again, for backwards compatibility, we keep this in place.
cd ${WEBROOT}
for x in `ls news/200*.xml | sort -r`
do
	echo "<uri>/$x</uri>" >> ${WEBROOT}/dyn/news-index.xml
done
echo "</uris>" >> ${WEBROOT}/dyn/news-index.xml
echo "News index generated :)"

# now the subpages
for x in ${ARCHES}
do
	cd ${WEBROOT}/proj/en/${x}
	for y in `ls news/200*.xml | sort -r`
	do
		echo "<uri>/${y}</uri>" >> ${WEBROOT}/dyn/${x}-news-index.xml
	done
	echo "</uris>" >> ${WEBROOT}/dyn/${x}-news-index.xml
	echo "News index for ${x} generated :)"
done

