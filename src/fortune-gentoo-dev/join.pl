#!/usr/bin/perl
# Copyright 1999-2007 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/fortune-gentoo-dev/join.pl,v 1.1 2007/04/28 22:43:14 robbat2 Exp $
#
# This script is desgined to re-join component entries of a fortune file
# back into a complete fortune file.
# Robin H. Johnson <robbat2@gentoo.org> (28 Apr 2007)
use strict;

my $ofhn = shift @ARGV;
-f $ofhn and die "'$ofhn' already exists.";
open OFH,'>',$ofhn or die "Unable to create '$ofhn': $!";

while(my $ifhn = shift @ARGV) {
	open IFH,'<',$ifhn or die "Unable to open '$ifhn': $!";
	my $i = 0;
	while(<IFH>) {
		chomp;
		s/[[:space:]]+$//g;
		next if (length($_) == 0);
		printf OFH "%s\n",$_;
		$i++;
	}
	print OFH "%\n" if($i > 0);
	close IFH;
}
