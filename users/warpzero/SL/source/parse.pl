#!/usr/bin/perl -w
use strict;

my $CC = $ENV{'CC'} | "gcc";
my $input = qx|$CC -E slbc-prms.h|;

$input =~ s/[,\n]/ /g;
$input =~ s/({|})/ $1 /g;
$input =~ s/\s+/ /g;

$input =~ s/^.+?bc_information.+?{([^\;]+);.+/{$1/;
my @table;
my $depth = 0;
my $zero = -1;
my $one = -1;
my $two = 0;

for (split/\s/, $input) {
	s/^"([^"]+)"$/$1/;
	
	
	if(/{/) {
		if( $depth == 1 ) {
			$zero++;
			$one = -1;
			$two = 0;
		}
		elsif( $depth == 2 ) {
			$one++;
			$two = 0;
		}
		$depth++;
		next;
	}
	elsif(/}/) {
		if( $depth == 0) {
			exit;
		}
		elsif( $depth == 1 ) {
			$zero--;
			$one = -1;
			$two = 0;
		}
		elsif( $depth == 2 ) {
			$one--;
			$two = 0;
		}
		$depth--;
		next;
	}
	else {
		print "\$table[$zero][$one][$two] = $_\n";
		$table[$zero][$one][$two] = $_;
		$two++;
	}
}

use Data::Dumper;

#my @table_section = $table[0];
#print $table_section[0]->[0]->[0] . "\n";

#open(FILE, "slbc-n.h");
#my %hash; 
#while(<FILE>){$hash{$1}=$2 if /^#define\s+(\S+)\s+(\S+)/}
print Dumper(\@table);
