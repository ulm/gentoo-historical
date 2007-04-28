#!/usr/bin/perl
# Copyright 1999-2007 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/fortune-gentoo-dev/rot13.pl,v 1.1 2007/04/28 23:18:12 robbat2 Exp $
#
# Cheesy rot13 implementation so we don't need an external binary.
# Robin H. Johnson <robbat2@gentoo.org> (28 Apr 2007)
use strict;
while(<>) {
	y/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ/nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM/;
	print;
}
