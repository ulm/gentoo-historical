#!/usr/bin/perl
# $Header: /var/cvsroot/gentoo/users/vladimir/eperl/eperl.pl,v 1.11 2003/04/22 23:54:58 vladimir Exp $
# Copyright (c) 2003 Graham Forest <vladimir@gentoo.org>
# Distributed under the GPL v2 or later, and all that cruft
# 
# eperl.pl applies Perl code to all ebuilds in Portage, displays and prompts
#   to accept changes, then runs echangelog upon leaving each directory.
#
# Please be careful with this, and watch all changes closely.
# By using it, you accepts all responsibility for your actions.
# Please have ECHANGELOG_USER set properly.
#
# Usage: eperl.pl '<code>' 'ChangeLog reason'
# 
# <code> being Perl code that may modify $_, which is each individual line of
#        all ebuilds.
#
# Examples:
# eperl.pl 's/Copyright (\d{4}-)2003/Copyright ${1}2004/' 'Updated Copyrights'
# eperl.pl 's/[~-]?x86//g if /^KEYWORDS/' 'x86 abandoned, ppc better afterall'
# eperl.pl 's/python/perl/g' 'Act of God'
#
use strict;
use File::Find;
use File::Basename;
use Term::ReadLine;
use Term::ANSIColor qw(:constants);
use Getopt::Long;

###############################################################################
#  User prefs
#
# Consider that echangelog is dependent on CVS, this should end with gentoo-x86
my $PORTDIR = "/usr/gentoo-x86";

# Turn off all changes
my $debug = 0;

# How many control-c's it takes to really kill it (please use q when possible)
my $max_zaps = 5;

###############################################################################
#  Setup of globals 'n stuff
#
$SIG{INT} = \&catch_zap;
my $num_zaps = 0;

my $term = new Term::ReadLine 'eperl.pl';
my $path_changes = 0;
my $path = "";

###############################################################################
#  Main - Check &wanted for the real meat
#

# Grab options
my $filter = "";
Getopt::Long::Configure("no_ignore_case", "bundling");
GetOptions(
    'help|h|?'		=> \&print_usage,
    'filter=s'		=> \$filter
) or &print_usage, exit;

# Make sure ECHANGELOG_USER is set
if ($ENV{'ECHANGELOG_USER'} eq "") {
	print RED "Please have \$ECHANGELOG_USER set", RESET, "\n";
	exit;
}

# We want two non-option arguments
&print_usage unless scalar @ARGV == 2;

find(
# Start our search of the tree
	{ 
		wanted => \&wanted,
		postprocess => \&postprocess,
		no_chdir => 1
	},
	$PORTDIR
);

###############################################################################
#  Subroutines
#
sub wanted {
# Runs once for each ebuild
	# We want only proper ebuilds
	return if /skel\.ebuild$/ || !/\.ebuild$/;
	
	if($filter ne "") {
	# Filter the worked on files for the --filter option
		return unless /$filter/;
	}
	
	print BOLD YELLOW "$_", RESET, "\n";
	# Put the entire ebuild in @contents
	my @contents = get_file($_);
	my $file = $_;
	# Apply the Perl code, which prints changed lines
	my ($changes, @new_contents) = apply_code($ARGV[0], @contents);
	
	if($changes) {
		# Grab the path, and the ebuild name without .ebuild
		my $ebuild;
		($path, $ebuild) = $_ =~ m|^(.+)/(.+).ebuild$|;
		
		# See if the user wants to accept the changes
		my $response = $term->readline("Accept $changes changes? [N/y/q] ");
		if($response =~ /^q/i) {
			&postprocess;
			print GREEN "User requested quit", RESET, "\n";
			exit;
		}
		
		if($response =~ /^y/i) {
			# This lets us know if we need to run echangelog later
			$path_changes++ if $changes;
			
			# Write the new ebuild to *_new.ebuild
			print RED "Saving changes...", RESET, "\n";
			put_file("$path/${ebuild}_new.ebuild", @new_contents) unless $debug;
			
			# Overwrite the old ebuild with the new
			unless($debug) {
				rename("$path/${ebuild}_new.ebuild", "$path/${ebuild}.ebuild")
				  or die "Couldn't rename $path/${ebuild}_new.ebuild to " .
				         "$path/${ebuild}.ebuild";
			}

			print YELLOW "Done", RESET, "\n\n";
		}
		else {
			# Do nothing
			print GREEN "Skipping file...", RESET, "\n\n";
		}
	}
}

sub get_file {
# Return the contents of the specified file
	my $file = shift;
	open(FILE, "<$file") or die "Couldn't open $file for reading\n";
	my @contents = <FILE>;
	close FILE;
	return @contents;
}

sub apply_code {
# Take argument one, and apply it as code to all other arguments, print 
#  differences, then return the number of changes followed by all the arguments
	my $code = shift;
	my $changes = 0;
	for (@_) {
		# Don't want to change CVS Header lines
		next if /\$Header:/;
		chomp;
		my $temp = $_;
		# This dies if it didn't make it to "return 1", ie, $code b0rked
		eval "$code;return 1;" or die "Couldn't eval $code: $!\n";
		
		# This checks for changes, and prints each line if there are any
		if ($temp ne $_) {
			$changes++;
			print RED "<-", RESET, "$temp\n";
			print RED "->", RESET, "$_\n";
		}
	}
	return ($changes, @_);
}
		   
sub put_file {
# Takes a path as argument one, opens it as a file, and writes all other
#  arguments to it, one per line
	my $file = shift;
	open(FILE, ">$file") or die "Couldn't open $file for reading\n";
	for (@_) {
		chomp;
		print FILE "$_\n";
	}
	close FILE;
}

sub postprocess {
# Executed upon leaving each ebuild directory
	if($path_changes) {
		# Run echangelog in the ebuild dir
		print RED "Updating ChangeLog in $path for $path_changes ";
		print "changed files...", RESET "\n\n";
		chdir $path or die "Couldn't chdir to $path: $!\n";
		unless($debug) {
			system("echangelog", "$ARGV[1]") == 0
			  or die "Couldn't echangelog $ARGV[1]";
		}
		# Run repoman in the ebuild dir
		print RED "repoman committing' in $path for $path_changes ";
		print "changed files...", RESET "\n\n";
		chdir $path or die "Couldn't chdir to $path: $!\n";
		unless($debug) {
			system("repoman", "commit", "-m", "$ARGV[1]") == 0
			  or die "Couldn't repoman commit $ARGV[1]";
		}
		
		
		$path_changes = 0;
	}
}

sub catch_zap {
# Stop attempts to control-c, so changelogs get updated proper-like
	print BOLD RED "Please exit by typing 'q'", RESET, "\n";
	if (++$num_zaps >= $max_zaps) {
		print BOLD RED "Exit forced", RESET, "\n";
		exit;
	}
}

sub print_usage {
# If you're wondering, give up now
	my $desc = "Apply Perl code to ebuilds globally";
	my $usage = "[options] '<code>' 'Changelog Reason'";
	my %options = (
		"--filter=<regex>" => 
		"Checked against the path to the ebuild, skipped if it doesn't match"
	);
	
	print "\n";
	print BOLD basename($0), "- $desc", RESET;
	print "\n\n";
	print BOLD YELLOW "Usage:", RESET, "\n";
	print "   " . basename($0) . " $usage\n\n";
	print BOLD YELLOW "Options:", RESET, "\n";
	for (sort keys %options) {
		print "   $_\t$options{$_}\n";
	}
	print "\n";
	print BOLD "Copyright (c) 2003 Graham Forest <vladimir\@gentoo.org>", RESET;
	print "\n\n";
	
	exit;
}
