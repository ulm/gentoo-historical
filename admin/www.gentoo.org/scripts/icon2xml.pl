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
if ($ARGV[0] =~ /./ ) {print "\nusage: icon2xml > outputfile.xml\n\n"; exit;}
$searchpath = "/home/httpd/gentoo/xml/images/icons/";
#
# icon path 
#
$iconpath = "http://www.gentoo.org/images/icons/";
#
# html tags
#


$header = "<?xml version='1.0'?>
<?xml-stylesheet href=\"/xsl/guide.xsl\" type=\"text/xsl\"?>
<mainpage id=\"graphics\">
<title>Gentoo Linux Icons</title>
<author title=\"Gentoo PR Cooridnator\"><mail link=\"klieber\@gentoo.org\">Kurt Lieber</mail></author>
<version>1.0.1</version>
<date>23 Feb 2003</date>
<chapter>
<section>
<title>Gentoo Linux Icon Sets</title>
<body>
<table>\n";
$footer = "</table>
<note>A tarball of all of these icons may be downloaded <uri link=\"http://www.gentoo.org/images/icons.tar.bz2\">here</uri> (1.4MB)</note>
<p>The initial design for these icons was provided by port001\@w0r.mine.nu.  Further additions were made to the icon set by forum users DuF, Hi-Fi, L-Chamber, bud1979, dufnutz, linux4god, slapcat, iKiddo and zypher.</p>	
<p>Users interested in extending the icon set can obtain the original files in 
<uri link=\"http://www.gentoo.org/images/icons/photoshop-base-l33t.psd\">Photoshop</uri> or
<uri link=\"http://www.gentoo.org/images/icons/gimp-base-l33t.xcf\">GIMP</uri> format.  Instructions and discussions regarding this icon set can be found on the <uri link=\"http://forums.gentoo.org/viewtopic.php?t=31958\">Gentoo Forums</uri>.</p>
</body>
</section>
</chapter>
</mainpage>\n";
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
#
#
foreach $line (@files) {
	($current_category = $line) =~ m/(.{4})_(.{3})_(.+)/g;
	push @{$categorised_filenames{$2}}, $line;
	}
#
# start XML page
#
print $header;
#
#
foreach $category (sort (keys(%categorys))) 
	{
	#
	# init category
	#
	#print "\nnew category: ".$categorys{$category}."\n";
	print "<tr><th>$categorys{$category}</th></tr>\n\n<tr><ti><table>\n";
		#
		# divide by 5 icons per line
		#
		
		$divide = 5;
		$i = 0;
		foreach $filename (@{$categorised_filenames{$category}}) 
			{
			if ($i == 0) {print "<tr>\n"}
			if ($i != 0 && $i / $divide == (int $i / $divide)) { print "</tr><tr>\n";}
			print "<ti><fig link=\"$iconpath$filename\"/></ti>\n";
			$i++;
			}
		print "</tr>\n";
	#
	# exit category
	#
	print "</table></ti></tr>\n";
	}
#
# exit XML page
#
print $footer;
