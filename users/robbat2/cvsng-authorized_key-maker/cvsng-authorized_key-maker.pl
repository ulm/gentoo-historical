#!/usr/bin/perl -wT
###
### LDAP->authorized_keys creation tool
### Copyright 2007 Robin H. Johnson <robbat2@gentoo.org>
###
### $Header: /var/cvsroot/gentoo/users/robbat2/cvsng-authorized_key-maker/cvsng-authorized_key-maker.pl,v 1.3 2007/02/21 08:31:21 robbat2 Exp $
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
use Time::HiRes qw(gettimeofday);
use Getopt::Std;
use Unicode::Normalize;
use POSIX qw(strftime);

my ($pwd,$ldap,$msg,@msg);

# This is the commandstring appended to keys
my $commandstring = 'no-port-forwarding,no-X11-forwarding,no-agent-forwarding,command="/usr/local/bin/cvsvnwrapper.sh"';

# LDAP stuff
my $server = 'ldap://ldap1.gentoo.org';
my $basedn = 'dc=gentoo, dc=org';
my $userfilter = '(&(uidNumber=*)(gentooStatus=active)(gentooAccess=cvs.gentoo.org)(sshPublicKey=*))';
my $directusersregex = '^stork.gentoo.org$|^infrastructure.group$';

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

    
$msg = $ldap->search( filter => $userfilter, base => $basedn, limit => 50000, attrs => ['uid','uidNumber','gentooAccess','sshPublicKey']);
$msg->code && warn "error: ", $msg->error;

@msg = $msg->entries;

foreach (@msg) {
	#use Data::Dumper;
	my $uid = $_->get_value ('uid');
	my $uidNumber = $_->get_value ('uidNumber');
	my $gentooAccess = $_->get_value ('gentooAccess', asref => 1);
	my $sshPublicKey = $_->get_value ('sshPublicKey', asref => 1);
	my $specialaccess = 0;
	print "uid=".$uid." ";
	if(grep {/$directusersregex/} @$gentooAccess) {
		print "Skipping\n";
		$specialaccess = 1;
	}
	my @raw_keys_ssh2 = grep (/ssh-/,@$sshPublicKey);
	# Clean up keys that had embedded newlines
	# and are thus invalid
	foreach(@raw_keys_ssh2) {
		my $a = $_;
		$_ =~ s/\n.*/ (truncated key garbage after embedded newline)/g;
		if($a ne $_) {
			print "Malformed-key-seen ";
		}
	}
	my @keys_ssh2 = grep (/command="\/usr\/bin\/cvs server"|command="\/usr\/local\/bin\/cvsvnwrapper.sh"/,@raw_keys_ssh2);
	push @keys_ssh2, (grep (!/command=/,@raw_keys_ssh2));

	# Make the location for the file
	my $home_dir = '/home/'.$uid;
	my $ssh_dir = $home_dir.'/.ssh';
	my $authorized_keys = $ssh_dir.'/authorized_keys';
	my $authorized_keys_temp = $ssh_dir.'/authorized_keys.tmp';
	mkdir $home_dir,0711;
	mkdir $ssh_dir,0700;
	chown $uidNumber,0, $home_dir, $ssh_dir;
	open(AKEYS,'>',$ssh_dir.'/authorized_keys.tmp');
	my ($s, $ms) = gettimeofday();
	print AKEYS '# '.$ssh_dir.'/authorized_keys created '.strftime("%a, %d %b %Y %H:%M:%S.".sprintf("%06d",$ms)." %z",gmtime($s))."\n";
	foreach(@keys_ssh2) {
		print "writing-key ";
		my $prefix='';
		# If they aren't special, rip out prefix of key
		$_ =~ s/^.*ssh-/ssh-/g if ($specialaccess != 1);
		# and force it to what we want it to be.
		$prefix = $commandstring.' ' if ($specialaccess != 1);
		print AKEYS $prefix.$_."\n";
	}
	close AKEYS;
	chown $uidNumber,-1, $authorized_keys, $authorized_keys_temp;
	rename $authorized_keys_temp, $authorized_keys;

	#foreach(@$sshPublicKey) {
	#	$_ =~ s/\n/ XXX /g;
	#	print $uid."\t".$_."\n";
	#	#print $uid."\n";
	#}
	#print Dumper($sshPublicKey);
	#print Dumper(@p);
	print "done\n";
}
