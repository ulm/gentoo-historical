#!/usr/bin/perl -w
#########################################################
# Script to create package list and descriptions	#
# Written by Colin Morey <peitolm@gentoo.org> 		#
#	June 05 2002					#
#########################################################

use strict;
use diagnostics;
################
# Global vars
################
my $portage_root='/usr/portage/';
my $pkg_input = `python ../python/genpkglist.py`|| die "Unable to get package list:$!\n";
my @package_list= split ('\n',$pkg_input);
my %packages =();
my %category_list=();
my $xml_index='../xml/pkg_index.xml';
my $package_dir='../xml/packages/';
#now to grab the descriptons and stuff

foreach my $line (@package_list){
	my ($name,$version,$category) = split(":",$line);
	$version =~s/(.*)-r0/$1/;
	my $ebuild = "$portage_root/$category/$name/$name-$version.ebuild";
	open(FILE,"$ebuild")|| die "unable to open $ebuild:$!";
	my $filecontent; { local $/ = undef; $filecontent = <FILE>; }
	close(FILE);
#	print "Line: $line \t => Category: $category\t Name: $name\n";
	$packages{$category}{$name}{version} = $version;
	my $license= "";
	if ($filecontent=~ /^LICENSE="([^"]*)"/msi){
		$license=$1;
	} else {
		$license = "No License Specified!";
	}
	$packages{$category}{$name}{license} = $license ;
	my $description = "";
	if ($filecontent=~ /^DESCRIPTION="([^"]*)"/msi){
		$description=$1;
		# lets clean up the descriptions to stop the xml parser barfing
		$description=~s/\&/\&amp\;/g;
		$description=~s/\</\&lt\;/g;
		$description=~s/\>/\&gt\;/g;
		$description=~s/([-a-zA-z\.0-9]+\@[-a-zA-z\.0-9]+)/\<mail link=\"$1\">$1\<\/mail\>/g;
		$packages{$category}{$name}{description} =$description;
	} else{
		$description=" No Description field found!";
	}
	my $homepage='';
	if ($filecontent=~ /^HOMEPAGE="([^"]*)"/msi){
		$homepage= $1;
		$packages{$category}{$name}{homepage} =$homepage;
	}else{
		$homepage = "NO Hompage defined";
	}

	$packages{$category}{$name}{depend} ="none";
	my $depend="";
	if ($filecontent=~ /^DEPEND="([^"]*)"/msi){
		$depend = $1;
		$depend=~s/\</\&lt\;/g;
		$depend=~s/\>/\&gt\;/g;
		my @depends = split('\n',$depend);
		my $depend_list="";
		foreach my $line (@depends){
			$depend_list .= "<li>$line</li>";
		}
		$depend="<ul>$depend_list</ul>";
	} else {
		$depend= "no Depend list found";
	}
	$packages{$category}{$name}{depend} = $depend ;
	$category_list{$category}="present";
}

##########################
# create the index of categories
##########################
open(FILE,">$xml_index")|| die "unable to open $xml_index:$!";
select FILE;
&print_list_header();
print qq|<section>
	<title>Package Categories</title>
	<body>
	<p>
	<table>
	<tr>
	<th>Category</th>
	</tr>
|;
my $side=1;
foreach my $category (sort keys %category_list){
	if ($side==1){
		print qq|<tr>
		<ti><uri link="/packages/$category/index.html">$category</uri></ti>
		|;
		$side=2;
	}elsif ($side==2) {
		print qq|
		<ti><uri link="/packages/$category/index.html">$category</uri></ti>
		|;
		$side=3;
	}else {
		print qq|
                <ti><uri link="/packages/$category/index.html">$category</uri></ti>
                </tr>
		|;
		$side=1;
	}
}
if ($side==2 or $side==3){
	print qq|
		</tr>
		|;
}
&print_footer();
close(FILE);
#######################
# create category-package index
#######################
foreach my $category (keys %category_list){
	my $workdir = $package_dir . $category;
	my $package_index = $workdir . "/index.xml";
	
	mkdir $workdir || warn "unable to create Directory $workdir: $!";
	open (FILE,">$package_index") || die "unable to open $package_index:$!";
	select FILE;
	&print_list_header();
	print qq|<section>
		<title>Package Category $category</title>
		<body>
		<p>
		<table>
		<tr>
			<th>Package</th>
			<th>Version</th>
		</tr>
	|;
	foreach my $name (sort keys %{ $packages{$category}} ){
		&print_entry($name,$category,$packages{$category}{$name}{'version'});
	}
&print_footer();
}
########################
# now we create the category descriptions
########################
foreach my $category (keys %category_list){
	my $workdir = $package_dir . $category;
	foreach my $name (keys %{ $packages{$category}} ){
		my $package_desc = $workdir . "/$name.xml";
		open (FILE,">$package_desc") || die "unable to open $package_desc:$!";
		select FILE;
		&print_list_header();
		print qq|<section>
			<title>$name Information</title>
			<body>
			<p>
			<table>
			<tr>
				<th>Package name</th>
				<ti>$name</ti>
			</tr>
			<tr>
				<th>Package version</th>
				<ti>$packages{$category}{$name}{'version'}</ti>
			</tr>
			<tr>	
				<th>Package Homepage</th>
				<ti><uri>$packages{$category}{$name}{'homepage'}</uri></ti>
			</tr>
			<tr>
				<th>Package Dependencies</th>
				<ti>$packages{$category}{$name}{'depend'}</ti>
			</tr>
			<tr>
				<th>Licensed under</th>
				<ti>$packages{$category}{$name}{'license'}</ti>
			</tr>
			<tr>
				<th>Package Description</th>
				<ti>$packages{$category}{$name}{'description'}</ti>
			</tr>
			<tr>
				<th>CVS Repository</th>
				<ti><uri link="http://www.gentoo.org/cgi-bin/viewcvs/gentoo-x86/$category/$name/">$name</uri></ti>
			</tr>
		|;
		&print_footer();
		close(FILE);
	}
}
exit;
#############
#misc subroutines
#############
sub print_list_header{
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
$year = $year + 1900;
my $date = "$mday $mon $year";
print qq|<?xml version='1.0'?>
<mainpage id="packages">
<title>Gentoo Linux Packages</title>
<author title="Grant Goodyear"><mail link="g2boojum\@gentoo.org">Grant Goodyear</mail></author>

<version>Current</version>
<date>$date</date>
<chapter>	|;

}
sub print_footer{
print q|</table>
        </p>
	</body>
	</section>
	</chapter>
	</mainpage>
	|;
}
sub print_entry{
	my $name = shift;
	my $category = shift;
	my $version = shift;
	print qq|
	<tr>
		<ti><uri link="/packages/$category/$name.html">$name</uri></ti>
		<ti>$version</ti>
	</tr>
	|;
}
