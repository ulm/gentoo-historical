#!/usr/bin/perl -w
# $Header: /var/cvsroot/gentoo/users/vladimir/esearch/Attic/edb.pl,v 1.1 2003/03/06 10:12:43 vladimir Exp $
# Copyright (c) 2003 Graham Forest <vladimir@gentoo.org>
# Distributed under the GPL v2 or later
use strict;
use File::Find;
use Term::ANSIColor qw(:constants);

###############################################################################
#  User prefs
#
my $PORTDIR = "/usr/portage/";

###############################################################################
#  Main - Check &wanted for the real meat
#

my %done;

open FILE, ">packages.txt";
find(
	{ 
		wanted => \&wanted,
		no_chdir => 1
	},
	$PORTDIR
);

###############################################################################
#  Subroutines
#
sub wanted {
	# We want only proper ebuilds
	return if m/skel\.ebuild$/ || ! m/\.ebuild$/;
	my $ebuild = $_;
	
	s/^$PORTDIR//;
	my @chunks = ebuild_path_to_name($_);
	
	unless(defined $done{"$chunks[0]/$chunks[1]"}) {
		my @contents = get_file($ebuild);
		print FILE "$chunks[0]/$chunks[1]#";
		for (@contents) {
			my ($gotdesc, $gotpage);
			if (m/^DESCRIPTION="([^"]+)"/) {
				print FILE "$1#";
				$gotdesc++;
			}
			elsif (m/^HOMEPAGE="([^"]+)"/) {
				print FILE "$1";
				$gotpage++;
			}
			last if $gotdesc && $gotpage;
		}
		print FILE "\n";
	}
	
	$done{"$chunks[0]/$chunks[1]"} = 1;
	
}

sub ebuild_path_to_name {
	return ($1, $2, $3) if $_[0] =~ /^
	([\w0-9-]+)						# Category
	\/								# Slash
	([\w0-9+-]+)					# Name
	\/								# Slash
	\2								# Matching name
	-								# Dash
	(
	[\d\.]+[a-z]?					# Version (with optional letter)
	(?:_(?:alpha|beta|pre|rc|p)\d*)?# Optional suffix (with optional number)
	(?:-r\d+)?						# Optional revision with number
	)
	\.ebuild						# Hrmmmm...
	$/x;
	return 0;
}

sub get_file {
# Return the contents of the specified file
	my $file = shift;
	open(MOO, "<$file") or die "Couldn't open $file for reading\n";
	my @contents = <MOO>;
	close MOO;
	return @contents;
}
