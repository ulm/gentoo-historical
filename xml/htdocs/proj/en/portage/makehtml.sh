#!/bin/bash

for X in *.xml "$@"; do
  if [ ! -e "${X}" ]; then
		continue
	fi
	X="${X%%.xml}"
	Y="${X}.xsltproc"

	xsltproc --path ~/gentoo/xml/htdocs/dtd:~/gentoo/xml/htdocs/xsl \
		~/gentoo/xml/htdocs/xsl/project.xsl \
		"${X}.xml" > "${Y}"

	xsltproc --path ~/gentoo/xml/htdocs/dtd:~/gentoo/xml/htdocs/xsl \
		~/gentoo/xml/htdocs/xsl/guide.xsl "${Y}" > "${X}.html"

	rm -f "${Y}"
done