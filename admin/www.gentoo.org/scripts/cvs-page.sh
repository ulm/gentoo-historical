#!/bin/bash

source ~/.bashrc

XSLTPROC=xsltproc
OUTLOG=/tmp/clog

if [ -d "${CVS_DOCROOT}" -a -d "${WEB_DOCROOT}" ]; then
	yesterday=`date -d "1 day ago 00:00" -R`
	today=`date -d "00:00" -R`
	cvsdate=-d\'${yesterday}\<${today}\'
	nicedate=`date -d yesterday +"%d %b %Y %Z (%z)"`

	cd ${CVS_GENTOO_ROOT}/gentoo-x86
	${CVS_WEB_SCRIPTS}/cvs2cl.pl --xml -f $OUTLOG -l "${cvsdate}" 2> /dev/null
	/usr/bin/sed -e 's/xmlns=".*"//' $OUTLOG > ${OUTLOG}.2
	$XSLTP ${CVS_DOCROOT}/xsl/cvs.xsl ${OUTLOG}.2 > ${WEB_DOCROOT}/dyn/index-cvs.xml
else
	echo "CVS_DOCROOT and/or WEB_DOCROOT were not set or were not directories" >&2
	exit 1
fi
