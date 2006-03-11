#!/usr/bin/make all
# Makefile for the Linux netcard diagnostic and setup package.
# Copyright 1999-2003 Donald Becker / Scyld Computing Corporation.
# $Id: Makefile,v 1.1 2006/03/11 05:39:20 vapier Exp $

# Make variables you may wish to override.
CFLAGS=-O -Wall -Wstrict-prototypes

# PREFIX may be set by the RPM build to set the effective root.
PREFIX=
# Standard directories, ref. gnumake manual.
prefix = $(PREFIX)/usr
exec_prefix = $(prefix)
instdir=$(exec_prefix)/sbin
MANDIR = $(prefix)/man
MANPAGES = etherwake.8 mii-diag.8 netdiag.8

# Diagnostics that can use libmii.
MDIAGS=alta-diag eepro100-diag epic-diag myson-diag\
   natsemi-diag ns820-diag pcnet-diag rtl8139-diag starfire-diag tulip-diag \
   via-diag vortex-diag winbond-diag yellowfin-diag
# Note: hamachi-diag and intel1000-diag require a kernel mechanism to map
# PCI memory regions into user-level diagnostics, and thus are not distributed.

DIAGS=ne2k-pci-diag $(MDIAGS)
UTILS=pci-config mii-diag ether-wake
LIBS = libflash.c libmii.c

ifeq ($(wildcard libflash.c), libflash.c)
  FLASH_DEPEND = libflash.o
  override CFLAGS += -DLIBFLASH
endif
ifeq ($(wildcard libmii.c), libmii.c)
  MII_DEPEND += libmii.o
  override CFLAGS += -DLIBMII
endif


most:  $(DIAGS) $(UTILS) diag-example
all:  most test-configmap config-map.o

diag-example $(MDIAGS): $(FLASH_DEPEND) $(MII_DEPEND)
ne2k-pci-diag: $(FLASH_DEPEND)
mii-diag: $(MII_DEPEND)

install:  $(DIAGS) $(UTILS)
	install -m 755 $^ $(instdir)
	mkdir -p $(MANDIR)/man8/
	install -m 444 $(MANPAGES) $(MANDIR)/man8/

netdiag.tgz: netdiag.spec $(MANPAGES) Makefile $(LIBS) $(addsuffix .c, $(DIAGS) $(UTILS))
	tar cfvz $@ $^

rpm: netdiag.tgz netdiag.spec
	rpm -ta $^

# Kernel module with support for extended diagnostics.
config-map.o: CFLAGS+=-O -I/lib/modules/`uname -r`/build/include -I../netdrivers/

.PHONY : most all clean distclean rpm

# Too many standard ways to clean..
clean distclean mostlyclean maintainer-clean:
	-rm -f $(DIAGS) $(UTILS) diag-example
	-rm -f libflash.o libmii.o
	-rm -f diag.tgz test-configmap
