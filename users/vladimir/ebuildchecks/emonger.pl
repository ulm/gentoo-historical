#!/usr/bin/perl -w
use strict;
# Copyright (c) 2003 Graham Forest <vladimir@gentoo.org>
# Distributed under the GPL v2 or later
# Not really for distribution, though ^_^
#
# Some concepts taken from cowfactory.pl, Copyright nall <nall@gentoo.org>
#
# Usage: find /usr/gentoo-x86 -name "*.ebuild" | xargs ./emonger.pl | less
# Usage: ./emonger.pl path-to/ebuild.ebuild
# Usage: ./emonger.pl category/name-version
#

################################################################################
#  User prefs
#
my $PORTAGEDIR = "/usr/gentoo-x86/";
my $SPAWN_EDITOR = 0;
my $SPAWN_ETERM = 0;

################################################################################
#  Init type stuff, set up lists and such
#
my (%valid_keywords, %valid_licenses, %valid_iuses);

# Possible KEYWORDS
$valid_keywords{$_}++ for qw( x86 ppc alpha sparc mips hppa arm * );
map {
	# Add ~ and - variants
	$valid_keywords{"~$_"}++;
	$valid_keywords{"-$_"}++;
} keys %valid_keywords;

# Possible LICENSEs
opendir(LICENSE_DIR, "${PORTAGEDIR}licenses/")
  or die "Can't open ${PORTAGEDIR}licenses/: $!";
$valid_licenses{$_}++ for grep !/^\.+$/, readdir LICENSE_DIR;
close LICENSE_DIR;

# Possible IUSEs
open(USE_DESC, "${PORTAGEDIR}profiles/use.desc")
  or die "Can't open ${PORTAGEDIR}profiles/use.desc: $!";
while (<USE_DESC>) {
	$valid_iuses{$1}++ if /^(\w+) - /;
}
close USE_DESC;
# Delete the arch values from iuses
map { delete $valid_iuses{$_} } keys %valid_keywords;

################################################################################
#  Main

for my $to_be_checked (@ARGV) {
	$to_be_checked =~ s|^$PORTAGEDIR||;
	next if ebuild_inherits($to_be_checked);
	
	if(my %failures = total_check($to_be_checked)) {
		print ebuild_path_to_name($to_be_checked) || $to_be_checked;
		print " - " . join(" ", keys %failures) . "\n";
		
		my $orig_mtime = (stat($PORTAGEDIR . $to_be_checked))[9];
		
		if ($SPAWN_EDITOR) {
			system($ENV{'EDITOR'} . " " . $PORTAGEDIR .  $to_be_checked) == 0
			  or die "Couldn't spawn $ENV{'EDITOR'} $PORTAGEDIR$to_be_checked: $!\n";
		}
		my ($path) = $to_be_checked =~ m|(.+)/|;
		chdir("$PORTAGEDIR$path") or die "Couldn't chdir: $!\n";

		my $new_mtime = (stat($PORTAGEDIR . $to_be_checked))[9];
		
		if($new_mtime - $orig_mtime > 0) {
			if ($SPAWN_ETERM) {
				system("Eterm") == 0 or die "Couldn't exec Eterm";
			}
		}
		
		
		
		#open(EBUILD, "<$PORTAGEDIR$to_be_checked")
		#  or die "Couldn't open $PORTAGEDIR$to_be_checked: $!";
		#my @ebuild = <EBUILD>;
		#close EBUILD;
		
		#my $changes = 0;
		
		#for (@ebuild) {
		#	if (exists $failures{'KEYWORDS'} && /^KEYWORDS/) {
		#		print "Old $_";
		#		$changes++ if s/[~-]?sparc64//g;
		#		s/\s+/ /g;
		#		s/" | "/"/g;
		#		print "New $_\n"
		#	}
		#}
		
		#if($changes) {
		#	my ($temp) = $to_be_checked =~ /^(.+)\.ebuild$/;
		#	$temp .= "_new.ebuild";
		#	open(EBUILD, ">$PORTAGEDIR$temp")
		#	  or die "Couldn't open $PORTAGEDIR$temp: $!";
		#	for (@ebuild) {
		#		chomp;
		#		print EBUILD "$_\n";
		#	}
		
		#	close EBUILD;

		#	unless(scalar total_check($temp)) { 
		#		print "Fix satisfactory, saving, and adding ChangeLog entry\n";
		#		chdir("$PORTAGEDIR$path") or die "Couldn't chdir: $!\n";
		#		rename("$PORTAGEDIR$temp", "$PORTAGEDIR$to_be_checked")
		#		  or die "rename($PORTAGEDIR$temp, $PORTAGEDIR$to_be_checked) failed: $!";
		#		system("echangelog", "Automated removal of remaining sparc64 KEYWORDS")
		#		 == 0 or die "echangelog failed: $!";
		#		
		#	}
		#	else {
		#		unlink("$PORTAGEDIR$temp")
		#		  or die "Couldn't unlink $PORTAGEDIR$temp: $!";
		#	}
		#}

		

	}
}

################################################################################
#  Subroutines

# Usage  : "category/name/name-version[_suffix[#]][-revision#].ebuild"
# Returns: An array containing the elements that have errors
sub total_check {
	my $to_be_checked = shift;
	my %failures;
	#$failures{"NAME"}=1 unless ebuild_name_check($to_be_checked);
	$failures{"KEYWORDS"}=1 unless keywords_check(get_values("KEYWORDS", $to_be_checked));
	$failures{"LICENSE"}=1 unless license_check(get_values("LICENSE", $to_be_checked));
	#$failures{"IUSE"}++ unless iuse_check(get_values("IUSE", $to_be_checked));

	return %failures;
}

# Usage  : "category/name/name-version[_suffix[#]][-revision#].ebuild"
# Returns: "category/name-version[_suffix[#]][-revision#]" or 0
sub ebuild_path_to_name {
	return "$1/$2-$3" if $_[0] =~ /^
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

# Usage  : "category/name-version[_suffix[#]][-revision#]"
# Returns: "category/name/name-version[_suffix[#]][-revision#].ebuild" or 0
sub ebuild_name_to_path {
	return "$1/$2/$2-$3" if $_[0] =~ m/^
	([\w0-9-]+)						# Category
	\/								# Slash
	([a-zA-Z0-9-]+)					# Name
	-								# Dash
	(
	[\d\.]+[a-z]?					# Version (with optional letter)
	(?:_(?:alpha|beta|pre|rc|p)\d*)?# Optional suffix (with optional number)
	(?:-r\d+)?						# Optional revision with number
	)?
	$/x;
	return 0;
}

# Usage1 : "category/name/name-version[_suffix[#]][-revision#].ebuild"
# Usage2 : "category/name-version[_suffix[#]][-revision#]"
# Returns: 0 for fail, 1 for pass
sub ebuild_name_check {
	# Usage 1
	if ($_[0] =~ m/^
	[\w0-9-]+						# Category
	\/								# Slash
	([\w0-9+-]+)					# Name
	\/								# Slash
	\1								# Matching name
	-								# Dash
	[\d\.]+[a-z]?					# Version (with optional letter)
	(_(alpha|beta|pre|rc|p)\d*)?	# Optional suffix (with optional number)
	(-r\d+)?						# Optional revision with number
	\.ebuild						# Hrmmmm...
	$/x) {
		return 1;
	}
	# Usage 2
	elsif ($_[0] =~ m/^
	[\w0-9-]+						# Category
	\/								# Slash
	[a-zA-Z0-9-]+					# Name
	-								# Dash
	[\d\.]+[a-z]?					# Version (with optional letter)
	(_(alpha|beta|pre|rc|p)\d*)?	# Optional suffix (with optional number)
	(-r\d+)?						# Optional revision with number
	$/x) {
		return 1;
	}
	else {
		return 0;
	}
}

# Usage1 : "category/name-version[_suffix[#]][-revision#]"
# Usage2 : "category/name/name-version[_suffix[#]][-revision#].ebuild"
# Returns: 0 for no, 1 if ebuild inherits anything
sub ebuild_inherits {
	my $ebuild = shift;
	
	unless ($ebuild =~ /\.ebuild$/) {
		my $ebuildpath = ebuild_name_to_path($ebuild)
		  or die "Couldn't find path to ebuild for $ebuild";
		$ebuild = $ebuildpath;
	}
	open(EBUILD, "<$PORTAGEDIR$ebuild")
	  or die("Cannot open $PORTAGEDIR$ebuild");
	my $inherits = "0";
	while(<EBUILD>){
		if (m/^inherit /) {
			$inherits = 1;
			last;
		}
	}
	close(EBUILD);
	return($inherits);
}

# Usage1 : "wanted lvalue", category/name-version[_suffix[#]][-revision#]"
# Usage2 : "lvalue","category/name/name-version[_suffix[#]][-revision#].ebuild"
# Returns: rvalue, "NULL" if none
sub get_values{
	my $lvalue = shift;
	my $ebuild = shift;
	my $rvalue = "NULL";

	unless ($ebuild =~ /\.ebuild$/) {
		my $ebuildpath = ebuild_name_to_path($ebuild)
		  or die "Couldn't find path to ebuild for $ebuild";
		$ebuild = $ebuildpath;
	}
	
	open(EBUILD, "<$PORTAGEDIR$ebuild")
	  or die("Cannot open $PORTAGEDIR$ebuild: $!");
	while(<EBUILD>){
		$rvalue = $1 if m/^$lvalue="([^"]*)"/;
	}
	close(EBUILD);
	return($rvalue);
}

# Usage  : "keyword1 [keyword2] [keyword3]..."
# Returns: 0 for fail, 1 for pass
sub keywords_check {
	my $keywords = shift;
	for (split/ /, $keywords) {
		next if $_ eq "";
		return 0 unless defined $valid_keywords{$_};
	}
	return 1;
}

# Usage  : "license1 [license2] [license3]..."
# Returns: 0 for fail, 1 for pass
sub license_check {
	my $license = shift;
	$license =~ s/\|/ /g;
	return 0 if $license =~ /^\s*$/;
	for (split/ /, $license) {
		next if $_ eq "";
		return 0 unless defined $valid_licenses{$_};
	}
	return 1;
}

# Usage  : "iuse1 [iuse2] [iuse3]..."
# Returns: 0 for fail, 1 for pass
sub iuse_check {
	my $iuses = shift;
	for (split/ /, $iuses) {
		next if $_ eq "";
		return 0 unless defined $valid_iuses{$_};
	}
	return 1;
}
