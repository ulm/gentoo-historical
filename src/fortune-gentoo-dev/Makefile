# Copyright 1999-2007 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/fortune-gentoo-dev/Makefile,v 1.3 2007/04/28 23:25:58 robbat2 Exp $

# These are specific to Gentoo.
# If you are elsewhere, you might want to change them.
STRFILE ?= /usr/bin/strfile
PERL ?= /usr/bin/perl
RM ?= /bin/rm
INSTALL ?= /usr/bin/install -c
INSTALL_DIR ?= $(INSTALL) -d
ROT13 ?= $(PERL) rot13.pl
FORTUNE_DIR ?= /usr/share/fortune
FORTUNE_OFF_DIR ?= $(FORTUNE_DIR)/off

# What are our fortunes called?
FORTUNE_NAME = gentoo-dev

# Everything after here should be automatic
FORTUNE_OFF_NAME = $(FORTUNE_NAME)-off
FORTUNES = $(FORTUNE_NAME) $(FORTUNE_OFF_NAME)
FORTUNES_DAT = $(foreach f,$(FORTUNES),$(f).dat)
OUTPUT = $(FORTUNES) $(FORTUNES_DAT)
all: $(OUTPUT)

FORTUNE_SOURCES := $(wildcard fortunes/*)
FORTUNE_OFF_SOURCES := $(wildcard fortunes-offensive/*)

$(FORTUNE_NAME): $(FORTUNE_SOURCES)
	$(RM) -f $@
	$(PERL) join.pl $@ $^

$(FORTUNE_NAME).dat: $(FORTUNE_NAME)
	$(STRFILE) -o $< $@

$(FORTUNE_OFF_NAME): $(FORTUNE_OFF_SOURCES)
	$(RM) -f $@
	$(PERL) join.pl $@.tmp $^
	$(ROT13) <$@.tmp >$@
	$(RM) -f $@.tmp

$(FORTUNE_OFF_NAME).dat: $(FORTUNE_OFF_NAME)
	$(STRFILE) -ox $< $@

clean:
	$(RM) -f $(OUTPUT)

install: install_$(FORTUNE_NAME) install_$(FORTUNE_OFF_NAME)

install_$(FORTUNE_NAME): $(FORTUNE_NAME) $(FORTUNE_NAME).dat
	$(INSTALL_DIR) $(DESTDIR)$(FORTUNE_DIR)
	for i in $^ ; do \
		$(INSTALL) $$i $(DESTDIR)$(FORTUNE_DIR) || exit 1; \
	done

# Trim off the -off suffix
install_$(FORTUNE_OFF_NAME): $(FORTUNE_OFF_NAME) $(FORTUNE_OFF_NAME).dat
	$(INSTALL_DIR) $(DESTDIR)$(FORTUNE_OFF_DIR)
	for i in $^ ; do \
		$(INSTALL) $$i $(DESTDIR)$(FORTUNE_OFF_DIR)/$${i/-off} || exit 1 ; \
	done
