#!/usr/bin/perl
#
# script for building a XML page from a given path through
# the name of the files
# 
# Expected Filename: l33t_XXX_iconname.png
# 
# XXX reflects the category
#
# usage: icon2xml > outputfile.xml
#
# Build 26th Feb. 2003 by Fir3fly
# 
# Build 9th Mar. 2004 by klieber - minor path modifications
#
# Build 9th Mar. 2003 by Fir3fly
# 
# added 
# 1.  have the script output to a file instead of having to specific '>/path/to/icons.xml'
#
# 2.  can you also update the tarball inside the script as well?  So:
# 	rm $searchpath/icons.tar.bz2
# 	tar -cjf $searchpath/icons.tar.bz2 $searchpath
#
# 3.  have also updated the size of the tarball that gets displayed in the xml file
#
# Build 12th Mar. 2003 by Fir3fly
# 
# added 
# 1.  Date format adapted to gentoo.org web standart
#
# 2.  Added verification if there are actual new icons before generating a new page/tar
#
if ($#ARGV < 0)
	{
    #
    # define default output file here
	$outfile = "index.xml";
	
	} else {
	$option1 = $ARGV[0];
	$parameter1 = $ARGV[1];	
	if ($option1 =~ /-h|--help/ || $parameter1 !~ /./){print "\nusage: icon2xml [-o outputfile.xml]\n\n"; exit;}
	if ($option1 =~ /-o/){$outfile = $parameter1;}
	}
#
#
$searchpath = "/home/httpd/gentoo/xml/images/icons/";
#$searchpath = ".";
#
# icon path 
#
$iconpath = "http://www.gentoo.org/images/icons/";
#
# html tags
#
@timenow = localtime(time);
@month = ( 'Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez');
$today = $timenow[3]." ".$month[($timenow[4])]." ".($timenow[5]+1900);

$header = "<?xml version='1.0'?>
<?xml-stylesheet href=\"/xsl/guide.xsl\" type=\"text/xsl\"?>
<mainpage id=\"graphics\">
<title>Gentoo Linux Icons</title>
<author title=\"Gentoo PR Cooridnator\"><mail link=\"klieber\@gentoo.org\">Kurt Lieber</mail></author>
<version>1.0.3</version>
<date>$today</date>
<chapter>
<section>
<title>Gentoo Linux Icon Sets</title>
<body>
<table>\n";
#
#
#
%categorys =  (
	 'LOG' => 'Logos' ,
	 'DEV' => 'Devices',
	 'DES' => 'Desktop',
	 'CDR' => 'CD Burning',
	 'TER' => 'Terminals',
	 'GAM' => 'Games',
	 'BRO' => 'Browsers',
	 'MAI' => 'Email Programs',
	 'NEW' => 'News Readers',
	 'REM' => 'Remote Control',
	 'P2P' => 'Peer to Peer',
	 'IMS' => 'Instant Messaging',
	 'FTP' => 'FTP Clients',
	 'MED' => 'Media Players',
	 'IMA' => 'Image Viewers',
	 'GRA' => 'Graphic Editors',
	 'TXT' => 'Text Editors',
	 'OFF' => 'Office Suites &amp; Tools',
	 'FIN' => 'Financial',
	 'EMU' => 'Emulators',
	 'WIN' => 'Windows',
	 'DVP' => 'Development',
	 'GNO' => 'Miscellaneous GNOME',
	 'KDE' => 'Miscellaneous KDE',
	 'UTI' => 'Miscellaneous Utilities',
	 'AUD' => 'Miscellaneous Audio',
	 'UNK' => 'Uncategorized',
	 'CLR' => 'Clear',
	 'PUR' => 'Purple',
	 'HUG' => 'Huge',
	);
#
# get filenames
#

opendir(DIR, $searchpath);
	    @files = grep(!/^\.\.?$/,readdir(DIR));
		closedir(DIR);
#
# sorting
#	     
@files = sort (grep /l33t_/, @files);
#
# Check if there are new icons since last time
#
if (-e "$outfile") {
if (-e "$searchpath/.iconlist.old")
	{
	open (LAST, "$searchpath/.iconlist.old");
	@oldiconlist = <LAST>;
	close (LAST);
	if (@oldiconlist == @files) {exit}
	}}

#
#
#
foreach $line (@files) {
	($current_category = $line) =~ m/(.{4})_(.{3})_(.+)/g;
	push @{$categorised_filenames{$2}}, $line;
	}
#
# open output file
#
open (OUT, ">$outfile") || die "unable to open $outfile";
#
# start XML page
#
print OUT $header;
#
#
foreach $category (sort (keys(%categorys))) 
	{
	#
	# init category
	#
	print OUT "<tr><th>$categorys{$category} ($category)</th></tr>\n\n<tr><ti><table>\n";
		#
		# divide by 5 icons per line
		#
		
		$divide = 5;
		$i = 0;
		foreach $filename (@{$categorised_filenames{$category}}) 
			{
			if ($i == 0) {print OUT "<tr>\n"}
			if ($i != 0 && $i / $divide == (int $i / $divide)) { print OUT "</tr><tr>\n";}
			print OUT "<ti><fig link=\"$iconpath$filename\"/></ti>\n";
			$i++;
			}
		print OUT "</tr>\n";
	#
	# exit category
	#
	print OUT "</table></ti></tr>\n";
	}
#
# removing old tarball
# 
if (-e "$searchpath/icons.tar.bz2" ) {unlink ("$searchpath/icons.tar.bz2") || print "Removal of old tarball not successful";}
#
# create new tarball
#
#system `tar -cjf $searchpath/icons.tar.bz2 $searchpath/*.png`;
#
# get size of tarball
#
$getsizeof = "$searchpath/icons.tar.bz2";
@tarstat = stat $getsizeof;
$tarsize = int ($tarstat[7]/1024)."kb" ;
#
# exit XML page
#
$footer = "</table>
<note>A tarball of all of these icons may be downloaded <uri link=\"".$iconpath."icons.tar.bz2\">here</uri> ($tarsize)</note>
<p>The initial design for these icons was provided by port001\@w0r.mine.nu.  Further additions were made to the icon set by forum users DuF, Hi-Fi, L-Chamber, bud1979, dufnutz, linux4god, slapcat, iKiddo and zypher.</p>	
<p>Users interested in extending the icon set can obtain the original files in 
<uri link=\"".$iconpath."photoshop-base-l33t.psd\">Photoshop</uri> or
<uri link=\"".$iconpath."gimp-base-l33t.xcf\">GIMP</uri> format.  Instructions and discussions regarding this icon set can be found on the <uri link=\"http://forums.gentoo.org/viewtopic.php?t=31958\">Gentoo Forums</uri>.</p>
</body>
</section>
</chapter>
</mainpage>\n";
#
#
print OUT $footer;
#
# Generate new iconlist
#
open (NEW, ">$searchpath/.iconlist.old") || print "cannot create $searchpath/.iconlist.old";
	foreach $newicon (@files) {print NEW $newicon."\n";}
	close (NEW);
