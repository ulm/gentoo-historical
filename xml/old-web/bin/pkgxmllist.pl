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

#now to grab the descriptons and stuff

foreach my $line (@package_list){
	my ($name,$version,$category) = split(":",$line);
	$version =~s/(.*)-r0/$1/;
	my $ebuild = "$portage_root/$category/$name/$name-$version.ebuild";
	open(FILE,"$ebuild")|| die "unable to open $ebuild:$!";
	my $description; { local $/ = undef; $description = <FILE>; }
	close(FILE);
	$description=~/^DESCRIPTION="[^"]*"/msi;
	%packages = {
		"$category" => {
			"$name"=>{	
				version => $version,
				description =>$description,
			},
		},
	};
}
&print_list_header();

foreach my $category (keys %packages){
	print qq|<section>
		<title>Package Category $category</title>
		<body>
		<p>
		<table>
		<tr>
			<th>Package</th>
			<th>Version</th>
			<th>Category</th>
		</tr>
	|;
	foreach my $name (keys %{ $packages{$category}} ){
		&print_entry($name,$category,$packages{$category}{version});
	}
	print q|
	</table>
	</p>
	</body>
	</section>
	|;
}

&print_footer();
exit;
#############
#misc subroutines
#############
sub print_list_header{
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
$year = $year + 1900;
my $date = "$mday $mon $year";
print q|
<?xml version='1.0'?>
<mainpage id="packages">
<title>Gentoo Linux Packages</title>
<author title="Grant Goodyear"><mail link="g2boojum@gentoo.org">Grant Goodyear</mail></author>

<version>Current</version>
<date>$date</date>
	|;

}
sub print_footer{
print q|
	</chapter>
	</mainpage>
	|;
}
sub print_entry{
	my $name = shift;
	my $category = shift;
	$category =~ /(.*)-r0$/;
	my $version = shift;
	print qq|
	<tr>
		<ti><uri link="/packages/$category/$name">$name</ti>
		<ti>$version</ti>
		<ti>$category</ti>
	</tr>
	|;
}
