#!/bin/bash
# Modified by zhen <zhen@gentoo.org> 5/1/2003 to add support for the
# arch projects subpages.

#to get GENTOO_WEB_DOCROOT and WEBSCRIPTS defined
source ~/.bashrc

# what arches do we support?
ARCHES="ppc"

[ -z "${GENTOO_WEB_DOCROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1
install -d ${GENTOO_WEB_DOCROOT}/dyn

# for backwards compatibility, create the main www.gentoo.org newspage.
	cat > ${GENTOO_WEB_DOCROOT}/dyn/news-index.xml << EOF 
<?xml version="1.0" encoding="UTF-8"?>
<uris>
EOF

# now do all of the subpages
for x in ${ARCHES}
do
	cat > ${GENTOO_WEB_DOCROOT}/dyn/${x}-news-index.xml << EOF 
<?xml version="1.0" encoding="UTF-8"?>
<uris>
EOF
done
	
mydate=`date +"%d %b %Y"`

# again, for backwards compatibility, we keep this in place.
cd ${GENTOO_WEB_DOCROOT}
#for x in `ls news/200*.xml | sort -r`
for x in `ls ${GENTOO_WEB_DOCROOT}/news/200*.xml | sed -e 's/^.*htdocs\///' | sort -r`
do
	echo "<uri>/$x</uri>" >> ${GENTOO_WEB_DOCROOT}/dyn/news-index.xml
done
echo "</uris>" >> ${GENTOO_WEB_DOCROOT}/dyn/news-index.xml
echo "News index generated :)"

# now the subpages
for x in ${ARCHES}
do
	cd ${GENTOO_WEB_DOCROOT}/proj/en/${x}
	#for y in `ls  news/200*.xml | sort -r`
	for y in `ls ${GENTOO_WEB_DOCROOT}/news/200*.xml | sed -e 's/^.*htdocs\///' | sort -r`
	do
		echo "<uri>/${y}</uri>" >> ${GENTOO_WEB_DOCROOT}/dyn/${x}-news-index.xml
	done
	echo "</uris>" >> ${GENTOO_WEB_DOCROOT}/dyn/${x}-news-index.xml
	echo "News index for ${x} generated :)"
done

