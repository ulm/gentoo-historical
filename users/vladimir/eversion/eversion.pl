#!/usr/bin/perl -w
use strict;
use File::Find;

print "$_\n" for sort verscomp qw(
  4b 4a 5_alpha 5_alpha1 5b_alpha 5_alpha1-r1 5_beta 5a_beta1 5_beta1-r1 5_pre
  5.2b 5_p1 5_p3 5_pre1 5_pre1-r1 5_rc 5_rc1 5_rc1-r1
);

sub verscomp {
    my @A = versplit($a);
    my @B = versplit($b);

    for ( 0 .. ( $#A >= $#B ? $#A : $#B ) ) {
	# This makes it where the number portions of the versions have the same
    # number of fields, padding with 0's or blanks where needed.
        $A[$_] = "" unless defined $A[$_];
        $B[$_] = "" unless defined $B[$_];

        if ( $A[$_] =~ /^\d+$/ && not $B[$_] =~ /^\d+$/ ) {
            splice( @B, $_, 0, 0 );
        }
        elsif ( $B[$_] =~ /^\d+$/ && not $A[$_] =~ /^\d+$/ ) {
            splice( @A, $_, 0, 0 );
        }

        elsif ( $A[$_] =~ /^[a-z]$/ && not $B[$_] =~ /^[a-z]$/ ) {
            splice( @B, $_, 0, "" );
        }
        elsif ( $B[$_] =~ /^[a-z]$/ && not $A[$_] =~ /^[a-z]$/ ) {
            splice( @A, $_, 0, "" );
        }
    }

    my ( $A, $B );
    while ( @A and @B ) {
        $A = shift @A;
        $B = shift @B;

        #
        # Identicals: Ignore 'em
        #
        if ( $A eq $B ) { next }

        #
        # Normal version numbers: Compare numerically
        #
        elsif ( $A =~ /^\d+$/ and $B =~ /^\d+$/ ) {
            return $A <=> $B if $A <=> $B;
        }

        #
        # Version letters: Compare alphabetically
        #
        elsif ( $A =~ /^[a-z]$/ and $B eq "" ) { return 1 }
        elsif ( $A eq "" and $B =~ /^[a-z]$/ ) { return -1 }
        elsif ( $A =~ /^[a-z]$/ and $B =~ /^[a-z]$/ ) {
            return $A cmp $B if $A cmp $B;
        }

        #
        # Suffixes
        #
        elsif ($A =~ /^(alpha|beta|rc|pre|p)\d*$/
            or $B =~ /^(alpha|beta|rc|pre|p)\d*$/ ) {

            # If they're a suffix, check if they're the same suffix, if so,
            # go by the number after the suffix, if not, go with the highest
            # ranked suffix
            my ( $asuf, $bsuf, $anum, $bnum ) = ( "", "", "", "" );
            ( $asuf, $anum ) = ( $1, $2 )
              if $A =~ /^(alpha|beta|pre|rc|p)(\d*)$/;
            ( $bsuf, $bnum ) = ( $1, $2 )
              if $B =~ /^(alpha|beta|pre|rc|p)(\d*)$/;
            if ( $asuf eq $bsuf ) {
                $anum = $anum ? $anum : 0;
                $bnum = $bnum ? $bnum : 0;
                return $anum <=> $bnum;
            }
            for ( "p", "", "rc", "pre", "beta", "alpha" ) {
                if    ( $A =~ /^$_\d*$/ ) { return 1 }
                elsif ( $B =~ /^$_\d*$/ ) { return -1 }
            }
        }

        #
        # Revisions
        #
        elsif ( $A =~ /^r/ and $B eq "" ) { return 1 }
        elsif ( $B =~ /^r/ and $A eq "" ) { return -1 }
        elsif ( $B =~ /^r/ and $A =~ /^r/ ) {
            my ( $anum, $bnum );
            ($anum) = $1 if $A =~ /^r(\d+)/;
            ($bnum) = $1 if $B =~ /^r(\d+)/;
            $anum = $anum ? $anum : 0;
            $bnum = $bnum ? $bnum : 0;
            return $anum <=> $bnum;
        }
    }

    #
    # We can't determine which comes first
    #
    print STDERR qq|Undefined order: "$A", "$B"\n| unless $A eq "" and $B eq "";
    return 0;
}

sub versplit {
# Takes a version, returns it divided up into the smallest single pieces
# Verify and chop numbers, suffix, and revision out of input
    my @version = $_[0] =~ /^
	((?:\d+\.)*\d+[a-z]?)
	(?:_(alpha\d*|beta\d*|pre\d*|rc\d*|p\d+))?
	(?:-(r\d+))?
	$/x or die "Bunk version: $_[0]";

    # This takes the number part of the version, chops it up at the dots,
    # and add's the result to the beginning of @version after removing the
    # old numbers
    my @numbers = $version[0] =~ /([-.]|\d+|[^-.\d]+)/g;
    @numbers = grep { !/\./ } @numbers;
    shift @version;
    push @numbers, @version;

    # This fills out blanks so that we don't get uninitialized warnings
    map { $_ = "" if not defined $_ } @numbers;
    return @numbers;
}
