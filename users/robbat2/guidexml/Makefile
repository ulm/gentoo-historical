# Quick makefile for building docs
# $Header: /var/cvsroot/gentoo/users/robbat2/guidexml/Makefile,v 1.2 2003/10/17 07:28:10 robbat2 Exp $

SOURCES = mailsolution.xml 
OUTPUTS = $(SOURCES:.xml=.html)
XSLTPROC = xsltproc

%.html: %.xml 
	$(XSLTPROC) -o $@ $^
	sed -e 's,/css/,htdocs/css/,g' -i $@
	sed -e 's,/images/,http://www.gentoo.org/images/,g' -i $@

all: $(OUTPUTS)

clean:
	rm $(OUTPUTS)

