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
# Directories

my $portage_root='/usr/portage/';
my $xml_index='../xml/pkg_index.xml';
my $package_dir='../xml/packages/';
#hashes
my %packages =();
my %category_list=();

################
# Slurp in the list of pkages, their version and category, 
# There's no reason this couldn't use Imbed::python, but this was quicker
################
my $pkg_input = `python ../python/genpkglist.py`|| die "Unable to get package list:$!\n";
my @package_list= split ('\n',$pkg_input);

#now to grab the descriptons and stuff

foreach my $line (@package_list){
	my ($name,$version,$category) = split(":",$line);
	$version =~s/(.*)-r0/$1/;
	
	# I know we're re-creating this from the information when we could just pull it directly from portage
	# however it does add a degree of sanity checking

	my $ebuild = "$portage_root/$category/$name/$name-$version.ebuild";
	
	##############
	# Slurp in the ebuild, all in one go :)
	##############
	open(FILE,"$ebuild")|| die "unable to open $ebuild:$!";
	my $filecontent; { local $/ = undef; $filecontent = <FILE>; }
	close(FILE);
 	##############
	# Some people have put \" in an ebuild to escape "'s when shown, so let's keep them, but we need to move them out of the way
	##############
	$filecontent =~ s/\\\"/-c-/g;
	
	##############
	# start populating the hash, version first, as we know we have that.
	# we could do this earlier
	##############
	$packages{$category}{$name}{version} = $version;
	
	##############
	# Get the license from the ebuild, falling back to a default explanation if unsuccessful
	##############
	my $license= "";
	if ($filecontent=~ /^LICENSE="([^"]*)"/msi){
		$license=$1;
	} else {
		$license = "No License Specified!";
	}
	$packages{$category}{$name}{license} = $license ;
	
	##############
	# Ditto with the DESCRIPTION field, (this _will_ break if someone has put "'s in the desc, (see xemacs for an example)
	# We do a little more work here,.. to defang any embedded tags, and to pull out and format email accounts, 
	##############
	my $description = "";
	if ($filecontent=~ /^DESCRIPTION="([^"]*)"/msi){
		$description=$1;
		################
		# lets move the -c-'s back to "'s
		$description=~ s/-c-/\"/g;

		# lets clean up the descriptions to stop the xml parser barfing
		$description=~s/\&/\&amp\;/g;
		$description=~s/\</\&lt\;/g;
		$description=~s/\>/\&gt\;/g;
		$description=~s/([-a-zA-z\.0-9]+\@[-a-zA-z\.0-9]+)/\<mail link=\"$1\">$1\<\/mail\>/g;
		$packages{$category}{$name}{description} =$description;
	} else{
		$description=" No Description field found!";
	}
	
	#############
	# Get the HOMEPAGE location
	#############
	my $homepage='';
	if ($filecontent=~ /^HOMEPAGE="([^"]*)"/msi){
		$homepage= $1;
		$packages{$category}{$name}{homepage} =$homepage;
	}else{
		$homepage = "NO Hompage defined";
	}
	
	#############
	# Grab the dependancies and build an unordered list out of them
	#############
	$packages{$category}{$name}{depend} ="none";
	my $depend="";
	my $rdepend="";
	if ($filecontent=~ /^DEPEND="([^"]*)"/msi){
		$depend = $1;
		$depend=~s/\</\&lt\;/g;
		$depend=~s/\>/\&gt\;/g;
		my @depends = split('\n',$depend);
		my $depend_list="";
		foreach my $line (@depends){
			if ($line eq '${RDEPEND}'){$rdepend="present"; next};
			$depend_list .= "<li>$line</li>";
		}
		$depend="<ul>$depend_list</ul>";
	} else {
		$depend= "no Depend list found";
	}
	$packages{$category}{$name}{depend} = $depend ;
	###########
	# Check for and create run-time dependancies
	###########
	if ($rdepend eq "present"){
		if ($filecontent=~ /^RDEPEND="([^"]*)"/msi){
			$rdepend= $1;
			$rdepend=~s/\</\&lt\;/g;
			$rdepend=~s/\>/\&gt\;/g;
			my @rdepends = split('\n',$rdepend);
			my $rdepend_list="";
			foreach my $line (@rdepends){
				next if ($line eq '');
				$rdepend_list .= "<li>$line</li>";
			}
			$rdepend="<ul>$rdepend_list</ul>";
		}
		$packages{$category}{$name}{rdepend} = $rdepend;
	} else {
		$packages{$category}{$name}{rdepend} = "No Run-Time Dependancies";
	}



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
my $side=1; # a counter to let us know which coloumn we're in
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
				<th>Run-Time Dependencies</th>
				<ti>$packages{$category}{$name}{'rdepend'}</ti>
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
