#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/relnotes/genrelnotes.sh,v 1.1 2003/12/31 22:24:16 zhen Exp $

## Gentoo Release Notes generator
## John Davis <zhen@gentoo.org>; 2003 12 30
## genrelnotes.sh basically takes the busy work out of release notes.
## It will ask some simple questions, then fill in some blanks such as
## your name (for the author), release version, date, etc.

source /sbin/functions.sh

case "$1" in
	"sedme")
		sedme $2
		exit 0
	;;

	"validate")
		validate
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

usage() {
	einfo "Gentoo Release Notes Generator (genrelnotes.sh)"
	einfo "Valid arguments: "
	echo "sedme: (genrelnotes.sh sedme output.xml) runs a sed on the template to produce"
	echo "a template corrected (output.xml) for the current release."
	echo
	echo "validate: (genrelnotes.sh validate input.xml) validates the XML of the input file"
	echo
	echo "genall: (genrelnotes.sh genall input.xml) creates txt and html versions on input.xml"
	echo
	echo "gentxt: (genrelnotes.sh gentxt input.xml) generates txt from input.xml"
	echo
	echo "genhtml: (genrelnotes.sh genhtml input.xml) generates html from input.xml"
}
