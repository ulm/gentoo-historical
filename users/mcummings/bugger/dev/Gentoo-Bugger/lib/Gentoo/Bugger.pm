package Gentoo::Bugger;

use 5.008002;
use strict;
use warnings;
use Carp qw(croak);
use WWW::Mechanize 1.02;
use WWW::Bugzilla 0.4;
use HTML::Strip 1.02;

require Exporter;

our @ISA = qw(Exporter);

# Items to export into callers namespace by default. Note: do not export
# names by default without a very good reason. Use EXPORT_OK instead.
# Do not simply export all your public functions/methods/constants.

# This allows declaration	use Gentoo::Bugger ':all';
# If you do not need this, moving things directly into @EXPORT or @EXPORT_OK
# will save memory.
our %EXPORT_TAGS = ( 'all' => [ qw(
	
) ] );

our @EXPORT_OK = ( @{ $EXPORT_TAGS{'all'} } );

our @EXPORT = qw(
	
);

our $VERSION = '0.01';


# Preloaded methods go here.

sub new {
	my $proto = shift;
	my %args = @_;
	my $class = ref($proto) || $proto;
	my $self = {};
	$self->{onerror} =  \&Gentoo::Bugger::_die;
	$self->{onwarn} = \&Gentoo::Bugger::_warn;
	$self->{BUGID} = undef;
	$self->{SEARCH} = undef;
croak("'server', 'login', and 'password' are all required arguments.") if ( (not $args{server}) or (not $args{login}) or (not $args{password}) ); 

	$self->{server} = $args{server};
	$self->{login} = $args{login};
	$self->{password} = $args{password};
	$self->{downdir} = $args{downdir}||"/tmp";
	$self->{runmode} = $args{runmode};


	$self->{pagelevel} = 0;

	$self->{mech} = WWW::Mechanize->new();
    
	bless ($self, $class);
   	$self->connect_mech( delete $args{server}, delete $args{login}, delete $args{password});
	return $self;
}


sub connect_mech {
    my $self = shift;
    my $agent = $self->{mech};
    my ($server,$login,$password) = @_;
    my $url = 'http://'.$server.'/query.cgi?GoAheadAndLogIn=1';
    $agent->get( $url );
    $agent->submit_form(
        fields => {
            Bugzilla_login    => $login,
            Bugzilla_password => $password,
	    },
        
    );
    $self->{pagelevel} = 1;
    return ($agent);
}

sub list_bugs {
	my $self = shift;


    my %buglist;
    my $bugcount = 0;
    my $bugfor   = shift;
    my $stype    = shift;
    chomp($bugfor);

    $self->{mech}->form_number(1);
    $self->{mech}->field( 'email2', "" );

    if ( $stype eq "cc" ) {
        $self->{mech}->field( 'email1', $bugfor );
        $self->{mech}->untick( 'emailassigned_to1', '1' );
        $self->{mech}->tick( 'emailcc1', '1' );
        $self->{mech}->select( 'emailtype1', 'exact' );
    }
    elsif ( $stype eq "assigned" ) {
        $self->{mech}->field( 'email1', $bugfor );
        $self->{mech}->tick( 'emailassigned_to1', '1' );
        $self->{mech}->select( 'emailtype1', 'exact' );
    }
    elsif ( $stype eq "reporter" ) {
        $self->{mech}->field( 'email1', $bugfor );
        $self->{mech}->untick( 'emailassigned_to1', '1' );
        $self->{mech}->tick( 'emailreporter1', '1' );
        $self->{mech}->select( 'emailtype1', 'exact' );
    }
    elsif ( $stype eq "keyword" ) {
        $self->{mech}->field( 'email1', "" );
        $self->{mech}->untick( 'emailassigned_to1', '1' );
        $self->{mech}->field( 'long_desc', $bugfor );
        $self->{mech}->select( 'long_desc_type', 'anywordssubstr' );
    }
    $self->{mech}->untick( 'emailreporter2', '1' );

    $self->{mech}->select( 'order', 'Bug Number' );
    $self->{mech}->submit();
    $self->{pagelevel}++;

    $self->{mech}->follow_link( text_regex => qr/CSV/ );
    $self->{pagelevel}++;
    my $content = $self->{mech}->content;
    my @baseline = split( /\n/, $content );
    if ($baseline[0] =~ m/bug_id/i){
    foreach my $line ( sort @baseline ) {
        $line =~ s/\"//mg;
        my @rowline = split( /,/, $line );
        next if ( $rowline[0] =~ m/bug_id/ );
        next if ( $rowline[0] eq "" );
        next if ( $rowline[0] =~ /^\n$/ );
        $bugcount++;
        $buglist{$bugcount} = {
            'BugID'       => "$rowline[0]",
            'Priority'    => "$rowline[1]",
            'Description' => "$rowline[7]"
        };
    }
    }
    $self->go_back();
    return (%buglist);

}

sub show_bug {
    my $self = shift;
    my $BUG = shift;
    chomp($BUG);
    my %bugtext;
    $self->{mech}->submit_form(
        form_number => 2,
        fields      => { id => "$BUG", }
    );
    $self->{pagelevel}++;
    #my $ccline = $mech;
    $self->{mech}->follow_link( text_regex => qr/format for printing/i );
    $self->{pagelevel}++;

    my $TextBody = $self->{mech}->content();

    our $hs = HTML::Strip->new();
    my $hrcount;

    my @blocks = split( /\<\!\-\- 1\.0\@bugzilla\.org \-\-\>/, $TextBody );

    my @fulltext;
    $fulltext[0] = $hs->parse("$blocks[2]");
    $fulltext[1] = $hs->parse("$blocks[3]");
    $fulltext[0] =~ s/Bug\#\:\n/Bug\#\:/i;
    $fulltext[0] =~ s/\n\s{0,}/\n/mg;
    $fulltext[1] =~ s/\n\s{0,}/\n/mg;
    $fulltext[0] =~ s/\n\n/\n/mg;
    $fulltext[1] =~ s/\n\n/\n/mg;
    my @sintext = split( /\n/, $fulltext[0] );
    my (
        $header,   $reporter, $status, $priority, $resolution,
        $severity, $assigned, $URL,    $textblock
    );

    #my $ccline;
    foreach my $TextLine (@sintext) {
        if ( $TextLine =~ m/Bug $BUG/ ) { $header = clean_line($TextLine) }
        elsif ( $TextLine =~ m/reported by: /i ) {
            $TextLine =~ s/reported by: //i;
            $reporter = clean_line($TextLine);
        }

     # Removed for now because CC: line doesn't appear in the text formatted
     # version of the show bugs page on bugzie
     #elsif ($TextLine =~ m/CC:/i) {$TextLine =~ s/CC://i; $ccline = $TextLine;}
        elsif ( $TextLine =~ m/status:/i ) {
            $TextLine =~ s/status: //i;
            $status = clean_line($TextLine);
        }
        elsif ( $TextLine =~ m/priority:/i ) {
            $TextLine =~ s/priority: //i;
            $priority = clean_line($TextLine);
        }
        elsif ( $TextLine =~ m/resolution:/i ) {
            $TextLine =~ s/resolution: //i;
            $resolution = clean_line($TextLine);
        }
        elsif ( $TextLine =~ m/severity:/i ) {
            $TextLine =~ s/severity: //i;
            $severity = clean_line($TextLine);
        }
        elsif ( $TextLine =~ m/assigned to:/i ) {
            $TextLine =~ s/assigned to: //i;
            $assigned = clean_line($TextLine);
        }
        elsif ( $TextLine =~ m/URL:/i ) {
            $TextLine =~ s/URL: //i;
            $URL = clean_line($TextLine);
        }
        else { next }
    }
    %bugtext = (
        'header'   => "$header",
        'reporter' => "$reporter",

        #'cclist' => "$ccline",
        'status'     => "$status",
        'priority'   => "$priority",
        'resolution' => "$resolution",
        'severity'   => "$severity",
        'assigned'   => "$assigned",
        'URL'        => "$URL",
        'textblock'  => "$fulltext[1]",
    );
    my $pages = $self->{pagelevel};
    $self->go_back( );

    return (%bugtext);
}


sub go_back {
	my $self = shift;
	for (my $count = $self->{pagelevel}; $count > 1; $count--)
	  { $self->{pagelevel}--; $self->{mech}->back() }
}

sub die {
    my $self = shift;

    return unless my $handler = $self->{onerror};

    $handler->(@_);
}


# NOT an object method!
sub _warn {
    require Carp;
    &Carp::carp; # pass thru
}

# NOT an object method!
sub _die {
    require Carp;
    &Carp::croak; # pass thru
}




1;
__END__
# Below is stub documentation for your module. You'd better edit it!

=head1 NAME

Gentoo::Bugger - Perl extension for blah blah blah

=head1 SYNOPSIS

  use Gentoo::Bugger;
  blah blah blah

=head1 DESCRIPTION

Stub documentation for Gentoo::Bugger, created by h2xs. It looks like the
author of the extension was negligent enough to leave the stub
unedited.

Blah blah blah.

=head2 EXPORT

None by default.



=head1 SEE ALSO

Mention other useful documentation such as the documentation of
related modules or operating system documentation (such as man pages
in UNIX), or any relevant external documentation such as RFCs or
standards.

If you have a mailing list set up for your module, mention it here.

If you have a web site set up for your module, mention it here.

=head1 AUTHOR

A. U. Thor, E<lt>mcummings@nonetE<gt>

=head1 COPYRIGHT AND LICENSE

Copyright (C) 2004 by A. U. Thor

This library is free software; you can redistribute it and/or modify
it under the same terms as Perl itself, either Perl version 5.8.2 or,
at your option, any later version of Perl 5 you may have available.


=cut
