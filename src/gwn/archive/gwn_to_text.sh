#!/bin/bash

XSL="/var/cvsroot/gentoo/src/gwn/gwn2txt.xsl"

xsltproc ${XSL} $1
