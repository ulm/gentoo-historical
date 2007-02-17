#!/usr/bin/perl -wT
###
### LDAP->authorized_keys creation tool
### Copyright 2007 Robin H. Johnson <robbat2@gentoo.org>
###
### $Header: /var/cvsroot/gentoo/users/robbat2/cvsng-authorized_key-maker/cvsng-authorized_key-maker.pl,v 1.1 2007/02/17 11:37:34 robbat2 Exp $
###
### This program is free software; you can redistribute it and/or modify
### it under the terms of the GNU General Public License as published by
### the Free Software Foundation; either version 2 of the License, or
### (at your option) any later version.

use strict;
use warnings;
use Encode;
use Net::LDAP;
use Time::Local;
use Getopt::Std;
use Unicode::Normalize;
use POSIX qw(strftime);

my ($pwd,$ldap,$msg,@msg);

# This is the commandstring appended to keys
my $commandstring = 'no-port-forwarding,no-X11-forwarding,no-agent-forwarding,command="/usr/local/bin/cvsvnwrapper.sh"';

# LDAP stuff
my $server = 'ldap://ldap1.gentoo.org';
my $basedn = 'dc=gentoo, dc=org';

# Start LDAP
$ldap = Net::LDAP->new($server, version => 3) || die "Connection Failed";
# Go secure
$msg  = $ldap->start_tls( verify => 'require', 
                          clientcert => '/etc/openldap/ssl/cert.pem',
                          clientkey  => '/etc/openldap/ssl/req.pem',
                          cafile     => '/etc/openldap/ssl/ca.pem' );
# Check for errors
if ($msg->is_error) { die "Error: ", $msg->error, "\n\n"; }    
# Bind anonymously
$msg = $ldap->bind;
if ($msg->is_error) { die "Error: ", $msg->error, "\n\n"; }    

    
$msg = $ldap->search( filter => '(&(uidNumber=*)(gentooAccess=cvs.gentoo.org)(sshPublicKey=*))', base => $basedn, limit => 50000 );
$msg->code && warn "error: ", $msg->error;

@msg = $msg->entries;

foreach (@msg) {
	my $uid = $_->get_value ('uid');
	my $gentooAccess = $_->get_value ('gentooAccess');
	my $sshPublicKey = $_->get_value ('sshPublicKey');
	print "uid=".$uid." gentooAccess=".$gentooAccess."\n";
}
