#!/usr/bin/perl
# $ Header: $
# Copyright (c) 2003 Graham Forest <vladimir@gentoo.org>
# Distributed under the GPL v2 or later
# Please be careful with this, don't use it if you're not reasonably fluent
#  with Perl.
#
use strict;
use File::Find;
use Term::ReadLine;
use Term::ANSIColor qw(:constants);

###############################################################################
#  User prefs
#
# Consider that echangelog is dependent on CVS, this should end with gentoo-x86
my $PORTDIR = "/usr/gentoo-x86";

###############################################################################
#  Setup of globals 'n stuff
#
my $term = new Term::ReadLine 'eregex.pl';

###############################################################################
#  Main - Check &wanted for the real meat
#
unless ( scalar @ARGV == 2 ) {
# We need two arguments
	print RED "\nPlease be careful with this, and watch all changes closely\n";
	print "By using it, you accepts all responsibility for ", BOLD, "your ";
	print RESET RED "actions.\nPlease have ECHANGELOG_USER set properly\n\n";
	print RESET "Usage: eperl.pl '<code>' 'ChangeLog reason'\n\n";
	exit;
}

find( { wanted => \&wanted, no_chdir => 1 }, $PORTDIR );

###############################################################################
#  Subroutines
#
sub wanted {
	# We want only proper ebuilds
	return if /skel\.ebuild$/ || !/\.ebuild$/;
	
	print "$_\n";
	# Put the entire ebuild in @contents
	my @contents = get_file($_);
	# Apply the Perl code, which prints changed lines
	my ($changes, @new_contents) = apply_code($ARGV[0], @contents);
	
	if($changes) {
		# Grab the path, and the ebuild name without .ebuild
		my ($path, $ebuild) = $_ =~ m|^(.+)/(.+).ebuild$|;
		
		# See if the user wants to accept the changes
		if($term->readline("Accept $changes changes? [no] ") =~ /^y/i) {
			# Write the new ebuild to *_new.ebuild
			print "Saving changes...\n";
			put_file("$path/${ebuild}_new.ebuild", @new_contents);
			
			# Overwrite the old ebuild with the new
			rename("$path/${ebuild}_new.ebuild", "$path/${ebuild}.ebuild")
			  or die "Couldn't rename $path/${ebuild}_new.ebuild to " .
			         "$path/${ebuild}.ebuild";
			
			# Run echangelog in the ebuild dir
			print "Updating ChangeLog\n";
			chdir $path or die "Couldn't chdir to $path: $!\n";
			system("echangelog", "$ARGV[1]") == 0
			  or die "Couldn't echangelog $ARGV[1]";
			
			print "Done\n\n";
		}
		else {
			# Do nothing
			print "Skipping file...\n\n";
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
		my $temp = $_;
		eval qq/
			# This var gets interpolated and run as code
			$code;
			
			# This checks for changes, and prints each line if there are any
			if (\$temp ne \$_) {
				\$changes++;
				print "<-\$temp";
				print "->\$_";
			}
			return 1;
		# This dies if it didn't make it to "return 1", ie, $code b0rked
		/ or die "Couldn't eval $code: $!\n";
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
