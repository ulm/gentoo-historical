package WWW::Bugzilla;

$WWW::Bugzilla::VERSION = '0.2';

use strict;
use warnings;
use File::Spec::Functions qw(catdir);
use WWW::Mechanize;
use Carp qw(croak);

use constant FIELDS => qw( product version component status assigned_to resolution dup_id assigned_to summary bug_number description os platform severity priority cc url add_cc target_milestone status_whiteboard keywords depends_on blocks additional_comments );
 
my %new_field_map = (   product => 'product',
                        version => 'version',
                        component => 'component',
                        assigned_to => 'assigned_to',
                        summary => 'short_desc',
                        description => 'comment',
                        os => 'op_sys',
                        platform => 'rep_platform',
                        severity => 'bug_severity',
                        priority => 'priority',
                        cc => 'cc',
                        url => 'bug_file_loc' );

my %update_field_map = (product => 'product',
                        bug_number => 'id',
                        platform => 'rep_platform',
                        product => 'product',
                        os => 'op_sys',
                        add_cc => 'newcc',
                        component => 'component',
                        version => 'version',
                        cc => 'cc',
                        status => 'knob',
                        priority => 'priority',
                        severity => 'bug_severity',
                        target_milestone => 'target_milestone',
                        url => 'bug_file_loc',
                        summary => 'short_desc',
                        status_whiteboard => 'status_whiteboard',
                        keywords => 'keywords',
                        depends_on => 'dependson',
                        blocks => 'blocked',
                        additional_comments => 'comment' );

=head1 NAME

WWW::Bugzilla - Handles submission/update of bugzilla bugs via WWW::Mechanize.

=head1 SYNOPSIS

    use WWW::Bugzilla;

    # create new bug
    my $bz = WWW::Bugzilla->new(    server => 'www.mybugzilla.com', 
                                    email => 'buguser@bug.com',
                                    password => 'mypassword' );

    # enter info into some fields and save new bug

    # get list of available version choices
    my @versions = $bz->available('version');

    # set version
    $bz->version( $versions[0] );

    # get list of available products
    my @products = $bz->available('product');

    # set product
    $bz->product( $products[0] );

    # get list of components available
    my @components = $bz->available('component');

    # set component
    $bz->component( $components[0] );

    # optionally do the same for platform, os, priority, severity.
    $bz->assigned_to( 'joeschmoe@whatever.com' );
    $bz->summary( $some_text );
    $bz->description( $some_more_text );

    # submit bug, returning new bug number
    my $bug_number = $bz->commit;

    # all of the above could have been done in a much easier
    # way, had we known what values to use. See below:

    my $bz = WWW::Bugzilla->new(    server => 'www.mybugzilla.com',
                                    email => 'buguser@bug.com',
                                    password => 'mypassword' 
                                    version => 'Alpha',
                                    product => 'MyProduct',
                                    component => 'API',
                                    assigned_to => 'joeschmoe@whatever.com',
                                    summary => $some_text,
                                    description => $some_more_text);

    my $bug_number = $bz->commit;

    # Below is an example of how one would update a bug.

    my $bz = WWW::Bugzilla->new(    server => 'www.mybugzilla.com',
                                    email => 'buguser@bug.com',
                                    password => 'mypassword' 
                                    bug_number => 46 );

    # show me the chosen component
    my $component = $bz->component;

    # change component
    $bz->component( 'Test Failures' );

    $bz->add_cc( 'me@me.org' );

    $bz->add_attachment(    filepath => '/home/me/file.txt',
                            description => 'description text',
                            is_patch => 0,
                            comment => 'comment text here' );

    $bz->additional_comments( "comments here");

    # below are examples of changing bug status
    $bz->change_status("assigned");
    $bz->change_status("fixed");
    $bz->change_status("later");
    $bz->mark_as_duplicate("12");
    $bz->reassign("someone@else.com");

    $bz->commit;

=head1 DESCRIPTION

WWW::Bugzilla currently provides an API to posting new Bugzilla
bugs, as well as updating existing Bugzilla bugs.

=head1 INTERFACE

=head2 METHODS

=over

=item new()

Initialize WWW::Bugzilla object.  If bug_number is passed in, 
will initialize as existing bug. Will croak() unless the 
Bugzilla login page on server specified returns a 200 or 404.
new() supports the following name-value parameters.

=over

=item server (required)

URL of the bugzilla server you wish to interface with. Do not 
place http:// or https:// in front of the url (see 'use_ssl' option
below)

=item email (required)

Your email address used by bugzilla, in other words your
bugzilla login.

=item password (required)

Bugzilla password.

=item use_ssl (optional)

If set, will use https:// protocol, defaults to http://

=item product

Bugzilla product name, required if entering new bug
(not updating).

=item bug_number (optional)

If you mean to update an existing bug (not create a new one)
include a valid bug number here.

=item version component status assigned_to resolution dup_id assigned_to summary bug_number description os platform severity priority cc url add_cc target_milestone status_whiteboard keywords depends_on blocks additional_comments

These are fields that can be initialized on new(), useful for new bugs.
Please note that some of these fields apply only to bugs being updated,
and if you set them here, they will be overridden if the value is already
set in the actual bug on the server.  These fields also have thier own
get/set methods (see below).

=back

=cut 

use Class::MethodMaker
    new_with_init => 'new',
    new_hash_init => 'hash_init',
    get_set       => [ FIELDS ];

sub init {
    my $self = shift;
    my %args = @_;
                        
    croak("'server', 'email', and 'password' are all required arguments.") if ( (not $args{server}) or (not $args{email}) or (not $args{password}) ); 

    croak("'product' required for new bug.") if ( (not $args{product}) and (not $args{bug_number}) );

    $self->{mech} =  WWW::Mechanize->new();

    $self->{protocol} = $args{use_ssl} ? 'https' : 'http';

    $self->{server} = $args{server};                                                                              
    $self->_login( delete $args{server}, delete $args{email}, delete $args{password});
    
    # finish the object
    $self->hash_init(%args);

    $self->{bug_number} ? $self->_get_update_page : $self->_get_new_page;

    return $self;
}

sub _get_new_page {
    my $self = shift;
                                                                  
    my $mech = $self->{mech};
                                                                  
    my $new_page = $self->{protocol}.'://'.catdir($self->{server},'enter_bug.cgi?product='.$self->{product});
    $mech->get($new_page);

    # bail unless OK or Redirect happens
    croak("Cannot open page $new_page") unless ( ($mech->status == '200') or ($mech->status == '404') );

}

sub _get_update_page {
    my $self = shift;

    my $mech = $self->{mech};

    my $update_page = $self->{protocol}.'://'.catdir($self->{server},'show_bug.cgi?id='.$self->{bug_number});
    $mech->get($update_page);

    # bail unless OK or Redirect happens
    croak("Cannot open page $update_page") unless ( ($mech->status == '200') or ($mech->status == '404') );

    # set fields to chosen values
    foreach my $field ( keys %update_field_map ) {
        if ($mech->current_form->find_input($update_field_map{$field})) {    
            $self->{$field} = $mech->current_form->value( $update_field_map{$field} );
        } 
    } 
}

sub _login {
    my $self = shift;
    my ($server, $email, $password) = @_;

    my $mech = $self->{mech};

    my $login_page = $self->{protocol}.'://'.catdir($server,'query.cgi?GoAheadAndLogIn=1');
    
    $mech->get( $login_page ); 

    # bail unless OK or Redirect happens
    croak("Cannot open page $login_page") unless ( ($mech->status == '200') or ($mech->status == '404') );

    $mech->form_number(1);
    $mech->field('Bugzilla_login', $email);
    $mech->field('Bugzilla_password', $password);
    $mech->submit_form();
 
}

=item product() version() component() status() assigned_to() resolution() dup_id() assigned_to() summary() bug_number() description() os() platform() severity() priority() cc() url() add_cc() target_milestone() status_whiteboard() keywords() depends_on() blocks() additional_comments()

get/set the value of these bug fields.  Some apply only to new bugs, some 
only to bugs being updated. commit() must be called to save these 
permanently.

=item available() 

Returns list of available options for field requested. Below are known
valid fields:

product
platform
os
version
priority
severity
component
target_milestone

=cut

sub available {
    my $self = shift;
    my $field_choice = shift;
    my $mech = $self->{mech};

    if (my $item = $mech->current_form->find_input( $field_choice )) {
        return $item->possible_values();
    } else {
        return undef;
    }
}

=item reassign() 

Mark bug being updated as reassigned to another user. Takes email 
address as parameter.  Status/resolution will not be updated 
until commit() is called.

=cut

sub reassign {
    my $self = shift;
    my $email = shift;
   
     croak("reassign() needs a bug number passed in as a parameter") if not $email;
                                                                             
    croak("reassign() may not be called until the bug is committed for the first time") if not $self->{bug_number};

    $self->{status} = 'reassign';
    $self->{assigned_to} = $email;  
}

=item mark_as_duplicate() 

Mark bug being updated as duplicate of another bug number.
Takes bug number as argument.
Status/resolution will not be updated until commit() is called.

=cut 

sub mark_as_duplicate {
    my $self = shift;
    my $dup_id = shift;

    croak("mark_as_duplicate() needs a bug number passed in as a parameter") if not $dup_id;
    
    croak("mark_as_duplicate() may not be called until the bug is committed for the first time") if not $self->{bug_number};

    $self->{status} = 'duplicate';
    $self->{dup_id} = $dup_id;    
}

=item change_status()

Change status of bug being updated.  Status/resolution will not
be updated until commit() is called.  The following are valid 
options (case-insensitive):

assigned
fixed
invalid
wontfix
later
remind
worksforme
reopen
verified
closed

=cut

sub change_status {
    my $self = shift;
    my $new_status = shift;

    croak("change_status() may not be called until the bug is committed for the first time") if not $self->{bug_number};

    $new_status = uc($new_status);

    my %status = (  'ASSIGNED'  => 'accept', 
                    'REOPEN'    => 'reopen',
                    'VERIFIED'  => 'verify',
                    'CLOSED'    => 'close' );

    my %resolution = (  'ASSIGNED'  => 1,
                        'FIXED'     => 1,
                        'INVALID'   => 1,
                        'WONTFIX'   => 1,
                        'LATER'     => 1,
                        'REMIND'    => 1,
                        'WORKSFORME' => 1   );

    croak ("$new_status is not a valid status.") if not ($resolution{$new_status} or $status{$new_status});

    if ($status{$new_status}) {
        $self->{status} = $status{$new_status};
    } else {
        $self->{status} = 'resolve';
        $self->{resolution} = $new_status;
    }
}

=item add_attachment()

Adds attachment to existing bug - will not work for new 
bugs.  Below are available params:

=over

=item *

filepath (required)

=item *

description (required)

=item *

is_patch (optional boolean)

=item *

content_type - Autodetected if not defined.

=item *

comment (optional)

=item *

finished - will not return object to update form if set (optional boolean) 

=back

=cut

sub add_attachment {
    my $self = shift;
    my %args = @_;
    my $mech = $self->{mech};

    croak("You must include a filepath and description.") unless ($args{filepath} and $args{description});
 
    my $attach_page = $self->{protocol}.'://'.catdir($self->{server},'attachment.cgi?bugid='.$self->{bug_number}.'&action=enter');
    
    $mech->get( $attach_page );
    $mech->field( 'data', $args{'filepath'} );
    $mech->field( 'description', $args{description} ) if $args{description};
    $mech->field( 'comment', $args{comment} ) if $args{comment};
    $mech->field( 'ispatch', 1 ) if $args{'is_patch'};
    
    if ( $args{content_type} ) {
        $mech->field( 'contenttypemethod', 'manual' );
        $mech->field( 'contenttypeentry', $args{content_type} );
    } else {
        $mech->field( 'contenttypemethod', 'autodetect' );
    }

    $mech->submit_form(); 

    $self->_get_update_page() unless ($args{finished});  
}

=item commit()

Submits bugzilla new or update form. Returns bug_number. Optionally
takes parameter finished- if set will you are done updating the bug,
and wil not return you to the update page.

=cut 

sub commit {
    my $self = shift;
    my %args = @_;
    my $mech = $self->{mech};
    
    if ($self->{bug_number}) {
        foreach my $field ( keys %update_field_map ) {
            $mech->field( $update_field_map{$field}, $self->{$field} ) if defined($self->{$field});
            # handle special cases
            if ($self->{resolution}) {
                $mech->field('resolution', $self->{resolution});
                $self->{resolution} = undef;
            }
            if ($self->{dup_id}) {
                $mech->field('dup_id', $self->{dup_id});
                $self->{dup_id} = undef;
            }
            if ($self->{assigned_to}) {
                $mech->field('assigned_to', $self->{assigned_to});
                $self->{assigned_to} = undef;
            }
        }
    } else {
        foreach my $field ( keys %new_field_map ) {
            if ($mech->current_form->find_input($new_field_map{$field})) {
                # if field is defined and it has changed
                if ( defined($self->{$field}) ) {
                    $mech->field( $new_field_map{$field}, $self->{$field} ) if ($mech->current_form->value($new_field_map{$field}) ne $self->{$field});
                }
            } 
        }
    }

    $mech->submit_form();
    $self->{bug_number} = $mech->current_form->value( 'id' ) if not ($self->{bug_number});

    $self->_get_update_page() unless ($args{finished});

    return $self->{bug_number};
}

=back

=head1 BUGS, IMPROVEMENTS

There may well be bugs in this module.  Using it as I have, I just
have not run into any.  In addition, this module does not support 
ALL of Bugzilla's features.  I will consider any patches or improvements,
just send me an email at the address listed below.
 
=head1 AUTHOR

Matthew C. Vella, the_mcv@yahoo.com

=head1 LICENSE
                                                                      
  WWW::Bugzilla - Module providing API to create or update Bugzilla bugs.
  Copyright (C) 2003 Matthew C. Vella (the_mcv@yahoo.com)
                                                                      
  This module is free software; you can redistribute it and/or modify
it
  under the terms of either:
                                                                      
  a) the GNU General Public License as published by the Free Software
  Foundation; either version 1, or (at your option) any later version,                                                                      
  or
                                                                      
  b) the "Artistic License" which comes with this module.
                                                                      
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See either
  the GNU General Public License or the Artistic License for more details.
                                                                      
  You should have received a copy of the Artistic License with this
  module, in the file ARTISTIC.  If not, I'll be glad to provide one.
                                                                      
  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
  USA

=cut

1;
