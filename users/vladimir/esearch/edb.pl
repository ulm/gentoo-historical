#!/usr/bin/perl -w
# $Header: /var/cvsroot/gentoo/users/vladimir/esearch/Attic/edb.pl,v 1.4 2003/03/06 12:37:35 vladimir Exp $
# Copyright (c) 2003 Graham Forest <vladimir@gentoo.org>
# Distributed under the GPL v2 or later
use strict;
use File::Find;
use Term::ANSIColor qw(:constants);

###############################################################################
#  User prefs
#
my $PORTDIR = "/usr/portage/";

my $ARCH = `uname -a`;
$ARCH = (split/ /, $ARCH)[10];

my ($ACCEPT_KEYWORDS) = grep(/^ACCEPT_KEYWORDS/, get_file("/etc/make.conf"))
  || "none";
$ACCEPT_KEYWORDS = $1 if $ACCEPT_KEYWORDS =~ m/^ACCEPT_KEYWORDS="([^"]+)"/;

###############################################################################
#  Main - Check &wanted for the real meat
#

my %done;

open FILE, ">packages.txt" or die "Can't open packages.txt to write the DB";

# First line contains a space seperated list of all acceptable keywords
print FILE "$ARCH $ACCEPT_KEYWORDS\n";

# Scan the portage tree
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
	
	# Next file if this one has a bad name
	return if scalar @chunks < 3;
	
	
	unless(defined $done{"$chunks[0]/$chunks[1]"}) {
	# Don't open an ebuild of the same name but different version as one
	#   that we've already done
		my @contents = get_file($ebuild);
		print FILE "$chunks[0]/$chunks[1]\0";
		my ($desc, $page, $key);
		for (@contents) {
		# Write all the cruft
			my ($gotdesc, $gotpage, $gotkey);
			if (m/^DESCRIPTION="([^"]+)"/) {
				$desc = "$1\0";
				$gotdesc++;
			}
			elsif (m/^HOMEPAGE="([^"]+)"/) {
				$page = "$1\0";
				$gotpage++;
			}
			elsif (m/^KEYWORDS="([^"]+)"/) {
			# Padded with spaces to make parsing easier later
				$key = " $1 ";
				$key =~ s/\s+/ /g;
				$gotkey++;
			}
			last if $gotdesc && $gotpage && $gotkey;
		}
		
		# Set up sane defaults
		print FILE $desc ? $desc : "No description available\0";
		print FILE $page ? $page : "No home page available\0";
		print FILE $key  ? $key  : "No KEYWORDS available\0";
		print FILE "\n";
	}
	
	# Make sure we skip the same category/name next time
	$done{"$chunks[0]/$chunks[1]"} = 1;
	
}

sub ebuild_path_to_name {
	return ($1, $2, $3) if $_[0] =~ m/^
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
	print RED "Bad ebuild name:", RESET, "$PORTDIR$_[0] - Ignoring\n";
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
