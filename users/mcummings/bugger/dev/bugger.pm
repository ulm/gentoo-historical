package bugger;

use WWW::Bugzilla;
my $bugver = $WWW::Bugzilla::VERSION;
if ( $bugver < 0.4 ) {
    print
"bugger requires at least WWW::Bugzilla 0.4.\nPlease emerge a newer version\n\n";
    exit();
}
use WWW::Mechanize;
my $mechver = $WWW::Mechanize::VERSION;
if ( $mechver < 1.02 ) {
    print
"bugger requires at least WWW::Mechanize 1.02.\nPlease emerge a newer version\n\n";
    exit();
}

use HTML::Strip;
my $stripver = $HTML::Strip::VERSION;
if ( $stripver < 1.02 ) {
    print
"bugger requires at least HTML::Strip 1.02.\nPlease emerge a newer version\n\n";
    exit();
}

sub list_bugs {

    my %buglist;
    my $bugcount = 0;
    my $bugfor   = shift;
    my $stype    = shift;
    chomp($bugfor);

    my $mech = connect_mech();
    $mech->form_number(1);
    $mech->field( 'email2', "" );

    if ( $stype eq "cc" ) {
        $mech->field( 'email1', $bugfor );
        $mech->untick( 'emailassigned_to1', '1' );
        $mech->tick( 'emailcc1', '1' );
        $mech->select( 'emailtype1', 'exact' );
    }
    elsif ( $stype eq "assigned" ) {
        $mech->field( 'email1', $bugfor );
        $mech->tick( 'emailassigned_to1', '1' );
        $mech->select( 'emailtype1', 'exact' );
    }
    elsif ( $stype eq "reporter" ) {
        $mech->field( 'email1', $bugfor );
        $mech->untick( 'emailassigned_to1', '1' );
        $mech->tick( 'emailreporter1', '1' );
        $mech->select( 'emailtype1', 'exact' );
    }
    elsif ( $stype eq "keyword" ) {
        $mech->field( 'email1', "" );
        $mech->untick( 'emailassigned_to1', '1' );
        $mech->field( 'long_desc', $bugfor );
        $mech->select( 'long_desc_type', 'anywordssubstr' );
    }
    $mech->untick( 'emailreporter2', '1' );

    $mech->select( 'order', 'Bug Number' );
    $mech->submit();

    $mech->follow_link( text_regex => qr/CSV/ );
    my $content = $mech->content;
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
    return (%buglist);

}

sub show_bug {
    my $BUG = shift;
    chomp($BUG);
    my $mech = connect_mech();
    $mech->submit_form(
        form_number => 2,
        fields      => { id => "$BUG", }
    );
    $mech->follow_link( text_regex => qr/format for printing/i );

    my $TextBody = $mech->content();

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

    return (%bugtext);
}

sub add_bug {

    # Recreating the form is just fun
    my $bugz = WWW::Bugzilla->new(
        server   => $server,
        email    => $login,
        product  => "Gentoo Linux",
        password => $password,
    );
    clearscreen();
    my @versions = $bugz->available('version');
    foreach my $vers (@versions) {
        print "$vers\n";
    }
    print "Version: ";
    my $version = <STDIN>;
    chomp($version);
    unless ($version) { $version = "unspecified" }
    $bugz->version($version);
    clearscreen();
    my @components = $bugz->available('component');

    foreach my $comp (@components) {
        print "$comp\n";
    }
    print "Component: ";
    my $component = <STDIN>;
    chomp($component);
    unless ($component) { $component = "Ebuilds" }
    $bugz->component($component);
    clearscreen();
    print "Assigned to: ";
    my $assigned = <STDIN>;
    chomp($assigned);
    $bugz->assigned_to($assigned);
    clearscreen();
    print "Summary: ";
    my $summary = <STDIN>;
    chomp($summary);
    $bugz->summary($summary);
    clearscreen();
    print "Long Description: (CTL-D to end)\n";
    my @description = <STDIN>;
    my $longd       = "@description";
    $bugz->description($longd);

    clearscreen();
    print "Adding bug...\n";
    my $bugnumber = $bugz->commit;
    print "Bug $bugnumber added.";
}

sub update_bug {
    my $BUG  = shift;
    my $bugz = WWW::Bugzilla->new(
        server     => $server,
        email      => $login,
        password   => $password,
        bug_number => $BUG,
    );
    clearscreen();
    print "Comment: (CTRL-D to end)\n";
    my @comments = <STDIN>;
    my $longc    = "@comments";
    $bugz->additional_comments($longc);
    print "\nBug $BUG updated\n" if $bugz->commit;

}

sub change_status {
    my $BUG  = shift;
    my $bugz = WWW::Bugzilla->new(
        server     => $server,
        email      => $login,
        password   => $password,
        bug_number => $BUG,
    );
    clearscreen();

# What I would like to do here is offer a short menu of change status, add cc, mark as dup, reassign, depends_on, blocks
    print "Change Options\n";
    print "Status\nAdd cc:\nMark as Dup\nReassign\nDepends On...\nBlocks\n";
    print "Change: ";
    my $choice = <STDIN>;
    chomp($choice);
    clearscreen();
    if ( $choice =~ /^sta/i ) {
        my @status =
          qw(assigned fixed invalid wontfix later remind worksforme reopen verified closed);
        foreach my $change (@status) {
            print "$change\n";
        }
        print "Status Change: ";
        my $status = <STDIN>;
        chomp($status);
        $bugz->change_status($status);
        clearscreen();
        print "Comment: (CTRL-D to end)\n";
        my @comment = <STDIN>;
        my $longc   = "@comment";
        $bugz->additional_comments($longc);
    }
    elsif ( $choice =~ /^ad/i ) {
        print "Add CC: ";
        my $addcc = <STDIN>;
        chomp($addcc);
        $bugz->add_cc($addcc);

        # add cc code
    }
    elsif ( $choice =~ /^ma/i ) {

        #Mark as dup code
        print "Mark as duplicate of bug number: ";
        my $dupid = <STDIN>;
        chomp($dupid);
        $bugz->mark_as_duplicate("$dupid");
    }
    elsif ( $choice =~ /^re/i ) {

        # Reassign
        print "Reassign bug to :";
        my $newstuckee = <STDIN>;
        chomp($newstuckee);
        $bugz->reassign($newstuckee);
    }
    elsif ( $choice =~ /^de/i ) {

        # Depend block
        print "Bug depends on bug id: ";
        my $depper = <STDIN>;
        chomp($depper);
        $bugz->depends_on($depper);
    }
    elsif ( $choice =~ /^bl/i ) {

        # Blocks
        print "$BUG is a blocker of: ";
        my $blocker = <STDIN>;
        chomp($blocker);
        $bugz->blocks($blocker);
    }
    else {
        clearscreen();
        print "Unable to proceed without a valid choice.\n";
        exit();
    }
    print "\nBug $BUG changed\n" if $bugz->commit;

}

sub add_attach {
    my $BUG = shift;

    my $bugz = WWW::Bugzilla->new(
        server     => $server,
        email      => $login,
        password   => $password,
        bug_number => $BUG,
    );
    clearscreen();
    print "Attachment with path (ex. /home/me/file.txt) :";
    my $attachment = <STDIN>;
    chomp($attachment);
    clearscreen();
    print "Description: ";
    my $descr = <STDIN>;
    chomp($descr);
    clearscreen();
    print "Is this a patch? (y/n) ";
    my $patch = <STDIN>;
    chomp($patch);
    if ( $patch =~ /y/i ) { $patch = 1 }
    else { $patch = 0 }
    clearscreen();
    print "Comment: (CTRL-D to end)\n";
    my @comment = <STDIN>;
    my $longc   = "@comment";
    clearscreen();
    $bugz->add_attachment(
        filepath    => $attachment,
        description => $descr,
        is_patch    => $patch,
        comment     => $longc
    );
    clearscreen();
    print "Attachment added to bug $BUG\n" if $bugz->commit;
}

# The following is a horrid hack, but I'm trying to keep the number of dependancies
# to a minimum in this package. So...

sub download_attach {
    my $BUG     = shift;
    my $downdir = $config{'downdir'} || "/tmp";
    my $agent   = WWW::Mechanize->new();
    $agent->get("http://bugs.gentoo.org/show_bug.cgi?id=$BUG");
    my $TextBody = $agent->content();
    my @TextBody = split( /\n/, $TextBody );
    my %grabbed  = ();
    foreach my $line (@TextBody) {

        if ( my ($download_url) = $line =~ m{(attachment\.cgi\?id=.*view)} ) {
            my $down = "http://bugs.gentoo.org/$download_url";
            my ($id) = $download_url =~ m{id=(\d+)\&amp};
            unless ( $grabbed{$id} == "1" ) {
                $grabbed{$id} = 1;

                print "  Downloading $down...\n ";
                my $response =
                  $agent->mirror( $down, "$downdir/$BUG-attachment-$id" );
            }
        }

    }

}

sub clean_line {
    my $line = shift;
    if ( $line =~ /\<input/i ) {
        $line =~ m/value\=\"(.*)\" size\=\"\d+\"\>/;
        $value = $1;
        $line =~ s/value\=\"(.*)\" size\=\"\d+\"\>/\>$1/;
    }
    if ( $line =~ / selected\>/i ) {
        my $tmpline = $line;
        $tmpline =~ / selected\>(\S+).*\<\/option/i;
        my $option = $1;
        if    ( $line =~ /iority/i )  { $line = "Priority : $option" }
        elsif ( $line =~ /everity/i ) { $line = "Severity : $option" }
        return ($line);
    }
    my $cleaned = $hs->parse($line);
    $hs->eof;
    $cleaned =~ s/\t//gm;
    $cleaned =~ s/\s+/ /gm;
    $cleaned =~ s/ valign\=\"top\"//;
    $cleaned =~ s/^\>\s+//;
    if ( $cleaned =~ /^\w\s\w+\s\:/ ) { $cleaned =~ s/ // }
    return ($cleaned);

}

sub clearscreen {

    my $clear_string = `clear`;
    print $clear_string;
}

sub connect_mech {
    my $agent = WWW::Mechanize->new();
    $agent->get("http://bugs.gentoo.org/query.cgi?GoAheadAndLogIn=1");
    $agent->submit_form(
        fields => {
            Bugzilla_login    => $main::login,
            Bugzilla_password => $main::password,
        }
    );
    return ($agent);
}

sub connect_bugz {
    my $BUG  = shift;
    my $bugz = WWW::Bugzilla->new(
        server     => $main::server,
        email      => $main::login,
        password   => $main::password,
        bug_number => $BUG,
    );

	return($bugz);
}

sub display_csv {
    my $content = shift;
    chomp($content);

    my @baseline = split( /\n/, $content );
    my $returncount = @baseline;
    $returncount--;
    print "$returncount items returned\n";
    my $rowcount = 1;
    foreach my $line ( sort @baseline ) {
        $line =~ s/\"//mg;
        my @rowline = split( /,/, $line );
        next if ( $rowline[0] =~ m/bug_id/ );
        next if ( $rowline[0] eq "" );
        next if ( $rowline[0] =~ /^\n$/ );
        $rowcount = $rowcount + 4;
        print "Bug ID $rowline[0]\nPriority $rowline[1]\n$rowline[7]\n\n";
        if ( $rowcount >= $rows ) {
            print "Press Enter to Continue";
            my $junk = <STDIN>;
            $rowcount = 0;
        }
    }
}

1;
