#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/relnotes/genrelnotes.sh,v 1.3 2004/01/04 05:15:47 zhen Exp $

## Gentoo Release Notes generator
## John Davis <zhen@gentoo.org>; 2003 12 30
## genrelnotes.sh basically takes the busy work out of release notes.
## It will ask some simple questions, then fill in some blanks such as
## your name (for the author), release version, date, etc.

source /sbin/functions.sh

XMLLINT="/usr/bin/xmllint"
LYNX="/usr/bin/lynx"
XSLTPROC="/usr/bin/xsltproc"

usage() {
	echo "Gentoo Release Notes Generator (genrelnotes.sh)"
	echo "Valid arguments: "
	echo
	echo "sedme: (genrelnotes.sh sedme output.xml) runs a sed on the template to produce"
	echo "a template corrected (output.xml) for the current release."
	echo
	echo "genall: (genrelnotes.sh genall input.xml) creates txt and html versions on input.xml"
	echo
	echo "gentxt: (genrelnotes.sh gentxt input.xml) generates txt from input.xml"
	echo
	echo "genhtml: (genrelnotes.sh genhtml input.xml) generates html from input.xml"
}

sedme() {
	if [ -z $1 ]
	then
		echo "You need to specify an output file!"
		exit 1
	fi
	local arch
	local email
	local name
	local release
	local reldate

	echo "The following questions will fill out the release notes template: "
	echo -n "Name: "; read name
	echo -n "e-mail: "; read email
	echo -n "Release Architecture: "; read arch
	echo -n "Release Version Stamp: "; read release
	echo -n "Release Date: "; read reldate

	/usr/bin/sed -e s:##NAME:"${name}": \
		-e s:##EMAIL:"${email}": \
		-e s:##DATE:"${date}": \
		-e s:##ARCH:"${arch}": \
		-e s:##RELEASE:"${release}": \
		-e s:##RELDATE:"${reldate}":\
		relnotes.xml > ${1}
}

gentxt() {
	if [ -z ${1} ]
	then
		echo "You need to specify an input file!"
		exit 1
	fi
	if [ -e ${LYNX} ]
	then
		if [ ! -e "`basename ${1} .xml`.html" ]
		then
			genhtml ${1}
		fi
		${LYNX} --dump "`basename ${1} .xml`.html" > "`basename ${1} .xml`.txt"
	else
		echo "${LYNX} not found!"
		exit 1
	fi
}

genhtml() {
	if [ -z ${1} ]
	then
		echo "You need to specify an input file!"
		exit 1
	fi
	if [ -e ${XSLTPROC} ]
	then
		if [ ! -e  guide.xsl ]
		then
			mkdir xsl
			echo "Fetching guide.xsl from gentoo.org for HTML processing: "
			/usr/bin/wget -c -O xsl/guide.xsl "http://www.gentoo.org/cgi-bin/viewcvs.cgi/*checkout*/xml/htdocs/xsl/guide.xsl?rev=1.91&cvsroot=gentoo"
			/usr/bin/wget -c -O xsl/content.xsl "http://www.gentoo.org/cgi-bin/viewcvs.cgi/*checkout*/xml/htdocs/xsl/content.xsl?rev=1.2&cvsroot=gentoo"
			/usr/bin/wget -c -O xsl/handbook.xsl "http://www.gentoo.org/cgi-bin/viewcvs.cgi/*checkout*/xml/htdocs/xsl/handbook.xsl?rev=1.12&cvsroot=gentoo"
		fi
		${XSLTPROC} xsl/guide.xsl ${1} > "`basename ${1} .xml`.html"
	else
		echo "${XSLTPROC} not found!"
		exit 1
	fi
}

case "$1" in
	"sedme")
		sedme $2
		exit 0
	;;

	"genall")
		genhtml $2
		gentxt $2
		exit 0
	;;

	"gentxt")
		gentxt $2
		exit 0
	;;

	"genhtml")
		genhtml $2
		exit 0
	;;

	"-h"|"--help"|*)
		usage
		exit 1
	;;
esac
