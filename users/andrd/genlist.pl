#!/usr/bin/perl

use Net::LDAP;
use IO;
my $output = new IO::File(">devlist.xml");

use XML::Writer;
my $writer = new XML::Writer( OUTPUT => $output );

sub create_section{
	my ($section_name)=@_;
	$writer->startTag('section');
	$writer->dataElement('title',$section_name);
	$writer->startTag('body');
	$writer->startTag('table');
#make header row
	$writer->startTag('tr');
	$writer->dataElement('th','Username');
	$writer->dataElement('th','Name');
	$writer->dataElement('th','Location');
	$writer->dataElement('th','Areas of responsibility');
	$writer->endTag();
}
sub create_row{
	my ($entry)=@_;
	$writer->startTag('tr');
	$writer->dataElement('ti',$entry->get('uid'));
	$writer->dataElement('ti',$entry->get('cn'));
	$writer->dataElement('ti',$entry->get($loc_attr));
	$writer->dataElement('ti',$entry->get($resp_attr));
	$writer->endTag();
}
sub end_section{
	$writer->endTag('table');
	$writer->endTag('body');
	$writer->endTag('section');
}
my $admin = q[];			#Labbeled as admin, but just needs read privs
my $ad_pw = q[];			#Password for said account
my $lsvr  = q[eagle.gentoo.org];	#LDAP Server
my $org   = q[dc=gentoo,dc=org];	#Base DN
my $loc_attr = q[geocos];		#Holds location informaion used in devlist
my $resp_attr = q[responsibilites];	#Responsibilites of developer listed on devlist.xml, obviously not in any standard schema, but we need a custom one to hold this and subdivision informaion
my $section_attr = q[section];		#Soecfies which section of the page the developer falls under

my $ldap = Net::LDAP->new($lsvr) or die "error connecting to $lsvr: $@";

#enable ssl/tls before we transmit passwords
start_tls(verify => 'none');    #should be changed to require and all certs should be accessible

$ldap->bind($admin, password => $ad_pw);

my %sections;
my $results = $ldap->search (  # Retrive all entries from the database
		filter => "(& ($org))"
		);

if($results->code) {
	die "received LDAP error: @{[$results->error]};
}

#let's start making the devlist
#basic header information
$writer->xmlDecl( 'UTF-8' );
$writer->pi('xml-stylesheet href="/xsl/guide.xsl" type="text/xsl"');
$writer->startTag('mainpage', 'id'=>'devlist');
$writer->dataElement('title','Gentoo Linux Developers');

#author(possily mention autogeneration?)
$writer->startTag('author','title'=>'Editor');
$writer->startTag('mail','link'=>'andrd@gentoo.org');
$writer->charachters('Abhishek Amit');
$writer->endTag();
$writer->endTag();

#date
$writer->dataElement('version','Current');
my $gm = gmtime( );
$writer->dataElement('date',$gm->mday . ' ' . $gm->mon . ' ' . $gm->year);
#start of real document
$writer->startTag('chapter');

foreach my $entry ($results->all_entries) {
	push @{ $sections{$entry->get($section_element)} } $entry;
	for $section ( keys %sections){
		create_section($section);
		for $i ( 0 .. $#{ $sections{$section} } ) {
			create_row($sections{$family}[$i]);
		}
		end_section();
	}
}
$writer->end();
$ldap->unbind;   # Unbind and close connection
