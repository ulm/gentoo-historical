#!/bin/bash
XSLTP=xsltproc
OUTLOG=/tmp/clog
#[ -z "${WEBROOT}" ] && echo "\$WEBROOT not set; exiting" && exit 1
export WEBROOT=~/gentoo-src/gentoo-xml/htdocs
source ~/.keychain/*-sh
cd ~/gentoo-x86 
echo ">>> Updating cvs..."
cvs -q update -dP
yesterday=`date -d "1 day ago 00:00" -R`
today=`date -d "00:00" -R`
cvsdate=-d\'${yesterday}\<${today}\'
nicedate=`date -d yesterday +"%d %b %Y %Z (%z)"`
echo ">>> Generating cvs log..."
~/gentoo-src/gentoo-xml/scripts/cvs2cl.pl --xml -f $OUTLOG -l "${cvsdate}" 2> /dev/null
/usr/bin/sed -e 's/xmlns=".*"//' $OUTLOG > ${OUTLOG}.2
$XSLTP ${WEBROOT}/xsl/cvs.xsl ${OUTLOG}.2 > ${WEBROOT}/dyn/index-cvs.xml
echo ">>> Done :)"
