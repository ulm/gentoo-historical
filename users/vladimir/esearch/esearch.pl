#!/usr/bin/perl -w
# $Header: /var/cvsroot/gentoo/users/vladimir/esearch/Attic/esearch.pl,v 1.5 2003/03/06 22:22:27 vladimir Exp $
# Copyright (c) 2003 Graham Forest <vladimir@gentoo.org>
# Distributed under the GPL v2 or later
#
# This is my quick, simple, caching Perl implimentation of emerge -s/S
# I like to think it's nifty. It's not quite done yet, so don't get whiny
#
use strict;
use File::Find;
use Term::ANSIColor qw(:constants);
use Getopt::Long;

###############################################################################
#  User prefs
#
my $regex      = '0';
my $searchall  = '0';
my $showmasked = '1';

###############################################################################
#  Main
#
Getopt::Long::Configure("no_ignore_case", "bundling");
GetOptions(
    'help|h|?'		=> sub { &print_usage; exit; },
	
	# These make a commandline switch toggle the user pref above
    'regex|r'		=> sub { $regex      = $regex      ? 0 : 1 },
    'searchall|S'	=> sub { $searchall  = $searchall  ? 0 : 1 },
    'showmasked|m'	=> sub { $showmasked = $showmasked ? 0 : 1 },
) or &print_usage, exit;

# No arguments
unless (scalar @ARGV > 0) {
	&print_usage;
	exit;
}

# Concatenate all arguments that aren't options as a space seperated string
$ARGV[0] = join " ", @ARGV;

# Quote metachars if we don't want regex matching
unless ($regex) {
	$ARGV[0] = quotemeta $ARGV[0];
}

# Grab our DB
my @packages = get_file("packages.txt");

# First line of the DB is our arch, followed by any accepted keywords
#   as set in /etc/make.conf
my @ACCEPT_KEYWORDS = split/ /, shift @packages;


for (@packages) {
# Search the DB, line by line
	
	# Split on \0's (rather unlikely char to conflict with anything
	my ($package, $desc, $homepage, $keywords) = split/\0/;
	
	if ($searchall) {
	# Match the whole thing if we're searching all categories
		next if ! /$ARGV[0]/oi;
	}
	else {
	# Otherwise, match only the package category/name
		next if $package !~ /$ARGV[0]/oi;
	}
	
	# Start off considering everything masked
	my $keyworks = 0;
	
	for (@ACCEPT_KEYWORDS) {
	# Check if any accepted keywords exist
		$keyworks++ if $keywords =~ /[" ]$_[" ]/;
	}

	# Remove leading and trailing space in keywords
	$keywords =~ s/^\s+(.+)\s+$/$1/;
	
	unless ($showmasked) {
	# Skip out now if we aren't printing masked, and we don't have good keywords
		next unless $keyworks;
	}
	
	# Spring cleaning
	chomp for ($package, $desc, $homepage, $keywords);
	
	# Print the category/name in bold white
	print BOLD "$package", RESET;
	
	# Print keywords in green if accepted, in red otherwise
	print "[ ";
	print $keyworks ? GREEN : RED;
	print $keywords, RESET;
	print "]\n";
	
	# Print our description and home page
	print "Description : $desc\n";
	print "Home page   : $homepage", RESET, "\n\n";
	
}

###############################################################################
#  Subroutines
#
sub get_file {
# Return the contents of the specified file
	my $file = shift;
	open(MOO, "<$file") or die "Couldn't open $file for reading\n";
	my @contents = <MOO>;
	close MOO;
	return @contents;
}

sub print_usage {
	print BOLD;
	print "\nesearch.pl - Lightweight, extremely fast Portage search";
	print RESET, "\n\n";
	print BOLD YELLOW "Usage:", RESET, "\n";
	print "   esearch.pl [options] search string\n";
	print BOLD YELLOW "Options:", RESET, "\n";
	print "   --help|h|?		Display this\n";
	print "   --regex|r		Use Perl regular expressions\n";
	print "   --searchall|S	Search all fields\n";
	print "   --showmasked|m	Show masked packages\n\n";
	print BOLD "Copyright (c) 2003 Graham Forest <vladimir\@gentoo.org>";
	print RESET, "\n\n";
}
