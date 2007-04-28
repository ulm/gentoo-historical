#!/usr/bin/perl
# Copyright 1999-2007 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/fortune-gentoo-dev/split.pl,v 1.1 2007/04/28 22:43:14 robbat2 Exp $
#
# This script is designed to split an existing fortune file into it's component
# entries, one per file.
# Robin H. Johnson <robbat2@gentoo.org> (28 Apr 2007)
use strict;

my $ifhn = $ARGV[0];
open IFH,'<',$ifhn or die "Failed to open '$ifhn' - $!";
my $n = 0;
my $i = undef;
my $ofhn;

while(<IFH>) {
	chomp;
	if(/^%$/) {
		next if ($i == 0);
		$i = 0;
		$ofhn = sprintf ("%s_%05d",$ifhn,$n);
		open OFH, ">",$ofhn;
		$n++;
		next;
	}
	$i++;
	printf OFH "%s\n",$_;
}
if($i == 0) {
	close OFH;
	unlink $ofhn if(-s $ofhn == 0);
}
