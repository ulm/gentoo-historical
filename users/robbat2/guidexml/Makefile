# Quick makefile for building docs
# $Header: /var/cvsroot/gentoo/users/robbat2/guidexml/Makefile,v 1.1 2003/10/17 01:55:16 robbat2 Exp $

SOURCES = mailsolution.xml
OUTPUTS = $(SOURCES:.xml=.html)
XSLTPROC = xsltproc

%.html: %.xml ; $(XSLTPROC) -o $@ $^

all: $(OUTPUTS)

clean:
	rm $(OUTPUTS)

