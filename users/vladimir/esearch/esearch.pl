#!/usr/bin/perl -w
# $Header: /var/cvsroot/gentoo/users/vladimir/esearch/Attic/esearch.pl,v 1.1 2003/03/06 10:12:43 vladimir Exp $
# Copyright (c) 2003 Graham Forest <vladimir@gentoo.org>
# Distributed under the GPL v2 or later
use strict;
use File::Find;
use Term::ANSIColor qw(:constants);

my @packages = get_file("packages.txt");
for (@packages) {
	next if ! /$ARGV[0]/;
	my ($package, $desc, $homepage) = split/#/;
	print BOLD YELLOW "$package", RESET, "\n";
	print RED      "$desc", RESET, "\n";
	print RESET       "$homepage", RESET, "\n";
}

sub get_file {
# Return the contents of the specified file
	my $file = shift;
	open(MOO, "<$file") or die "Couldn't open $file for reading\n";
	my @contents = <MOO>;
	close MOO;
	return @contents;
}
