#!/usr/bin/perl -w
#	sl-bc-main.pl - here we define the number for each bytecode
#
# Copyright (C) 2003 Joshua Charles Campbell
#		103 Mary Ave.
#		Missoula MT 59801
#	
#	This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
use strict;
use Getopt::Long qw(:config auto_abbrev bundling);
my $debug = '';
my @input_files_path = ();
my $output_file_path = '';

GetOptions ('debug!' => \$debug, "input-file=s" => \@input_files_path, "output-file=s" => \$output_file_path );
if ( $debug ) { print "Debuging mode is now ON\n"; }
unless ( @input_files_path ) { print STDERR "No input files\n"; die; }
unless ( $output_file_path ) { print STDERR "No output file\n"; die; }

open(INPUT_FILE, $input_files_path[0]) or die "Couldn't open file for input $input_files_path[0]: $!";

my @input_data_raw = <INPUT_FILE>;

map { s/^#.*//; s/^(.+?)\s+#.+/$1/ } @input_data_raw; # killing comments

print @input_data_raw if ($debug);

#my @input_data = ();
#push @input_data, split foreach @input_data_raw;
my @input_data = split /\s+/, join (" ", @input_data_raw);

if ($debug) {
	print ((scalar @input_data) . " words read from input starting with\n");
	print $input_data[0] . "\n";
	print $input_data[1] . "\n";
}
#$preped_header = `$ENV{'CC'} -E slbc-en.h`;

#-- BEGIN HEADERFILE LOADING ----------------------------
#this is vladimir's code here... it modded to make sense and to use $debug

sub get_3d_header_table {
	
	my ($headerfile, $tablename) = @_;
	
	my $CC = $ENV{'CC'} | "gcc";
	my $english_to_bc_raw = qx|$CC -E $headerfile|;
	
	$english_to_bc_raw =~ s/[,\n]/ /g;
	$english_to_bc_raw =~ s/({|})/ $1 /g;
	$english_to_bc_raw =~ s/\s+/ /g;

	$english_to_bc_raw =~ s/^.+?$tablename.+?{([^\;]+);.+/{$1/;
	my @refined_table;
	my $depth = 0;
	my $section = -1;
	my $operation = -1;
	my $code = 0;

	for (split/\s/, $english_to_bc_raw) {

		s/^"([^"]+)"$/$1/;
		if(/{/) {
			if( $depth == 1 ) {
				$section++;
				$operation = -1;
				$code = 0;
			}
			elsif( $depth == 2 ) {
				$operation++;
				$code = 0;
			}
			$depth++;
			next;
		}
		elsif(/}/) {
			if( $depth == 0) {
				exit;
			}
			elsif( $depth == 1 ) {
				$section--;
				$operation = -1;
				$code = 0;
			}
			elsif( $depth == 2 ) {
				$operation--;
				$code = 0;
			}
			$depth--;
			next;
		}
		else {
			if ($debug) {print "\$tablename[$section][$operation][$code] = $_\n";}
			$refined_table[$section][$operation][$code] = $_;
			$code++;
		}
	}
	return @refined_table;
}

my @english_to_bc = get_3d_header_table ( "slbc-en.h", "english_to_bc" );
my @op_parameters = get_3d_header_table ( "slbc-prms.h", "bc_information");

# we also need a C #define hash from slbc-n.h -- and we got it!

open(SLBC_N, "slbc-n.h");
my %slbc_n; 
while(<SLBC_N>){$slbc_n{$1} = hex $2 if /^#define\s+(\S+)\s+(\S+)/}
close(SLBC_N);

my %slbc_nts; #tasty hash because our headerfiles aren't as sane as we thought
# map the section opcodes to their tables
my $section_table = $english_to_bc[0];
for my $sti ( 0..$#english_to_bc ) { 
	$slbc_nts{ hex ($section_table->[$sti][0]) } = $sti; 
	print hex ( $section_table->[$sti][0] ) . "\n" if $debug;
}

#--------------------- end vladimir section here --------------

# right about here we have to start going through the code, Left to Right
# and make sure it is sane, and code it into SL bytecode which we will do later

sub check_bc_section { # only checking one section of the bytecode here
	my ($text_operation, $section) = @_; # perl subs are stupid, $section we are lookin in
#	my @english_to_bc_section;
#	for ( 0 .. $#{$english_to_bc[$section]} ) {
#		$english_to_bc_section[$_][0] = $english_to_bc[$section][$_][0];
#		$english_to_bc_section[$_][1] = $english_to_bc[$section][$_][1];
#	}
	my $english_to_bc_section = $english_to_bc[$section]; # get a section
#	print $section;
#	print $english_to_bc_section;
	for my $current_index (0..$#{$english_to_bc_section}) { # check the entire section
		my $current_operation = $english_to_bc_section->[$current_index][1]; # get the operation we are trying to match to
		print $text_operation . ' ' . $current_operation . "\n" if $debug; # debugging
		return hex $english_to_bc_section->[$current_index][0] if $text_operation =~ /^$current_operation$/i;  # match it and return if we did
	}
	return -1; # -1 means no match in this section
}

sub get_known_bc { # look for a valid, known bytecode OR misuse of a reserved word (return -2) OR return -1 for not found
	my ($text_operation, $current_section) = @_; # $text_operation is straight from the input file -- what we are trying to match
	my $match;
#	$match = check_bc_section($text_operation, $slbc_n{'SLBC_0_0_SECTIONCODE_CONTROL'}); # section 0x0C and 0x0B are valid anywhere
#	return $match if $match >= 0; # means we found a match
	$match = check_bc_section($text_operation, $slbc_nts{$slbc_n{'SLBC_0_0_SECTIONCODE_GLOBAL'}});
	return $match if $match >= 0;
	print "NOT IN GLOBAL\n" if $debug;
	$match = check_bc_section($text_operation, $current_section);
	return $match if $match >= 0;
	print "NOT IN LOCAL\n" if $debug;
	for (my $other_section = 0; $other_section < @english_to_bc; $other_section++) {
		return -2 if check_bc_section($text_operation, $other_section) >= 0; # the text is a reserved word but NOT an operation in the valid sections we just checked
	}
	return -1;
}

print get_known_bc($input_data[1], 0) . "\n" if $debug; # read the second word, assume section 0 (root) for now

# the main lexical analysis loop -- oh god, i am about to orgasm
# ok first things first we need to figure out what the fuck is going on
# besides reserved words (operations and statements) we have two types 
#	of words -- variable names and symbols which are in some cases
#	interchangable (ie. a variable of type symbol can often be used in 
#	place of a specific symbol name)
# for our purposes symbols should take precedence -- but that shouldnt matter
#	because both have to be declared
# for now, this code only needs basic knowledge of how declaring variables works
#	and how sections work


my @user_variables; my $user_variables_count = 0;
my @user_symbols; my $user_symbols_count = 0;
my @bytecode_tree_root; # uh oh... time for a fucking tree in perl... perldoc perlref time
my @bytecode_stack = ();

# the official structure for the tree is ( bytecode, length, pointer 0, ..., pointer length)

# kick it off with the root node
@bytecode_tree_root = ( $slbc_nts{$slbc_n{'SLBC_0_0_SECTIONCODE_ROOT'}}, 0); # we start with the root having nothing in it
push @bytecode_stack, \@bytecode_tree_root; # yes we is pusing a reference to the root node onto the stack...

my $known_bc;
for my $current_word_index (0..$#input_data) {
	print $current_word_index . " " . $input_data[$current_word_index] if $debug;
	# first figure out wtf it is IN CONTEXT
	$known_bc = get_known_bc($input_data[$current_word_index], $bytecode_stack[$#bytecode_stack]->[0]);
	if ( $known_bc == -2 ) {
		print ( STDERR "Invalid use of reserved word \"" . $input_data[$current_word_index] . "\"!\n" );
		die;
	} elsif ( $known_bc >= 0 ) {
		# rec'nized valid operation
		if ($known_bc == check_bc_section($input_data[$current_word_index], $slbc_nts{$slbc_n{'SLBC_0_0_SECTIONCODE_CONTROL'}}) ) {
			if ($known_bc == $slbc_n{'SLBC_0_0_CONTROL_END'} ){
			}
		}
		
		# i need to write an opcode arglist table for operations that support them
	} elsif ($known_bc == -1) {
		# not a reserved word
		
	}
}
