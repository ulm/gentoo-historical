#!/usr/bin/perl -w
# $Header: /var/cvsroot/gentoo/users/vladimir/esearch/Attic/esearch.pl,v 1.2 2003/03/06 11:36:04 vladimir Exp $
# Copyright (c) 2003 Graham Forest <vladimir@gentoo.org>
# Distributed under the GPL v2 or later
use strict;
use File::Find;
use Term::ANSIColor qw(:constants);

my @packages = get_file("packages.txt");

my @ACCEPT_KEYWORDS = split/ /, shift @packages;

for (@packages) {
	next if ! /$ARGV[0]/;
	my ($package, $desc, $homepage, $keywords) = split/\0/;
	
	my $keyworks = 0;
	
	for (@ACCEPT_KEYWORDS) {
		$keyworks++ if $keywords =~ /[" ]$_[" ]/;
	}

	$keywords =~ s/^\s+(.+)\s+$/$1/;
	
	chomp for ($package, $desc, $homepage, $keywords);
	print BOLD "$package", RESET;
	print "[ ";
	print $keyworks ? GREEN : RED;
	print $keywords, RESET;
	print "]\n";
	print "Description : $desc\n";
	print "Home page   : $homepage", RESET, "\n\n";
}

sub get_file {
# Return the contents of the specified file
	my $file = shift;
	open(MOO, "<$file") or die "Couldn't open $file for reading\n";
	my @contents = <MOO>;
	close MOO;
	return @contents;
}
