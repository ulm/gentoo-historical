#!/usr/bin/perl -w

############################################################
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
############################################################
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
# Build 4th Apr. 2003 by pjp
#
# added 
# 1.  index page for categories and individual pages for each category.
#
# 2.  changed categorys to categories 
#     (I thought it was awkward to read category and categorys)
#
# 3.  split code up into subroutines for easier readability.
#
# notes
# 1.  During testing, I noticed that -osomefile.xml doesn't parse correctly.
#
# Build 10 Apr. 2003 by pjp
#
# added
# 1.  create subdir for category pages if the dir doesn't exist.
#
############################################################

#
# main()
#

#
# $basedir	: base path for files
# $index_page	: the XML page listing icon categories with links to their pages
# $searchpath	: location of actual icon files
# $iconpath	: where the icons are accessed via the web page
# $index_header	: HTML header for the XML categories "index" page ($index_page)
# $index_footer	: HTML footer for index page
# %categories	: Unique 3 letter abbreviations (also part of icon filenames) for icon 
#	categories and a "description".
my $basedir = "/home/httpd/gentoo/xml/htdocs/dyn";
my $index_page = "$basedir/icons.xml";
my $searchpath = "/home/httpd/gentoo/xml/images/icons";
#
my $iconpath = "http://www.gentoo.org/images/icons/";

my $index_header = "<?xml version='1.0'?>
<?xml-stylesheet href=\"/xsl/guide.xsl\" type=\"text/xsl\"?>
<mainpage id=\"graphics\">
<title>Gentoo Linux Icons</title>
<author title=\"Gentoo PR Cooridnator\"><mail link=\"klieber\@gentoo.org\">Kurt Lieber</mail></author>
<version>1.0.3</version>
<date>".today()."</date>
<chapter>
<section>
<title>Gentoo Linux Icon Sets - index</title>
<body>
<table>\n";
my $index_footer;

my %categories =  (
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


usage() if defined $ARGV[0];

open (INDEX_FILE, ">$index_page") || die "unable to open $index_page";

print INDEX_FILE $index_header;
print INDEX_FILE "<tr><th>Categories</th></tr>\n";

prep_filenames();
make_xml_pages();
rm_tarball();
new_tarball();

# footer for index page only
$index_footer = "</table>
<note>A tarball of all of these icons may be downloaded <uri link=\"".$iconpath."icons.tar.bz2\">here</uri> (".size_tarball().")</note>
<p>The initial design for these icons was provided by port001\@w0r.mine.nu.  Further additions were made to the icon set by several other forum users.</p>	
Instructions and discussions regarding this icon set can be found on the <uri link=\"http://forums.gentoo.org/viewtopic.php?t=31958\">Gentoo Forums</uri>.</p>
</body>
</section>
</chapter>
</mainpage>\n";

print INDEX_FILE $index_footer;
close INDEX_FILE;

exit;
#
# exit main()
#

#
# Check for usage if user supplies arguments.
#
sub usage {
	my ($option1, $parameter1);

	$option1 = $ARGV[0];
	$parameter1 = $ARGV[1];	

	if ($option1 =~ /-h|--help/ || $parameter1 !~ /./) {
		print "\nusage: icon2xml [-o outputfile.xml]\n\n";
		exit;
	}
	if ($option1 =~ /-o/) {
		$index_page = $parameter1;
	}
} # usage()

#
# return date in "dd mmm yyyy" format
#
sub today {
	my (@timenow, @month, $today);

	@timenow = localtime(time);
	@month = ( 'Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez');
	$today = $timenow[3]." ".$month[($timenow[4])]." ".($timenow[5]+1900);
	
	return $today;
} # today

#
# process icon filenames for use in creating XML pages.
#
# get filenames
#
# sort filenames
#
sub prep_filenames {
	my (@files, $line, $current_category);

	opendir(DIR, $searchpath);
		@files = grep(!/^\.\.?$/,readdir(DIR));
		closedir(DIR);
	@files = sort (grep /l33t_/, @files);

	foreach my $line (@files) {
		(my $current_category = $line) =~ m/(.{4})_(.{3})_(.+)/g;
		push @{$categorised_filenames{$2}}, $line;
	}
} # prep_filenames()

#
# remove tarball of icon images
#
sub rm_tarball {
	if (-e "$searchpath/icons.tar.bz2" ) {
		unlink ("$searchpath/icons.tar.bz2") || print "Removal of old tarball not successful";
	}
} # rm_tarball()

#
# make a new tarball of icon files
#
sub new_tarball {
	`tar -vj --directory=/home/httpd/gentoo/xml/images/icons/ --create -f /home/httpd/gentoo/xml/images/icons/icons.tar.bz2 ./`;
} # new_tarball()

#
# return size of tarball in kb (1024)
#
sub size_tarball {
	my ($getsizeof, @tarstat, $tarsize);

	if (-e "$searchpath/icons.tar.bz2" ) {
		$getsizeof = "$searchpath/icons.tar.bz2";
		@tarstat = stat $getsizeof;
		$tarsize = int ($tarstat[7]/1024)."kb";
	} else {
		$tarsize = "0kb";
	}

	return $tarsize;
} # size_tarball()

#
# Create subdirectory for category pages if it doesn't exist.
#
# For each category:
# 	- add an entry to the categories index page.
# 	- create it's XML page.
#
# Icons ($icon_filename) will be displayed 5 per line in the category page
#
# $catdir			: output location for category XML files
# $category_header1	: HTML header for category pages - split for readability
# $category_header2	: HTML header for category pages
# $category_footer	: HTML footer for category pages
# $category_page	: path and filename for current category XML page
# $category_title	:
#
sub make_xml_pages {
	my ($category, $category_page, $category_title, $icon_filename);
	my ($divide, $i);
	my $catdir = "$basedir/icons";
	my $category_header1 = "<?xml version='1.0'?>
<?xml-stylesheet href=\"/xsl/guide.xsl\" type=\"text/xsl\"?>
<mainpage id=\"graphics\">
<title>Gentoo Linux Icons</title>
<author title=\"Gentoo PR Cooridnator\"><mail link=\"klieber\@gentoo.org\">Kurt Lieber</mail></author>
<version>1.0.3</version>
<date>".today()."</date>
<chapter>
<section>
<title>Gentoo Linux Icon Sets - ";
	my $category_header2 = "</title>
<body>
<table>\n";	
	my $category_footer = "</table>
<p><uri link=\"/dyn/icons.xml\">Return to Icon Sets - index</uri></p>
</body>
</section>
</chapter>
</mainpage>\n";	

	if (!-e $catdir) {	mkdir($catdir) || die "Couldn't create $catdir"; }
	elsif (!-d $catdir) { die "$catdir already exists, but isn't a directory"; }

	foreach $category (sort (keys(%categories))) {
		$category_page = "$catdir/$category.xml";
		open (CATEGORY_FILE, ">$category_page") || die "unable to open $category_page";

		$category_title = "$categories{$category} ($category)";
		print INDEX_FILE "<tr><ti><uri link=\"icons/$category.xml\">$category_title</uri></ti></tr>\n";
		print CATEGORY_FILE "$category_header1$category_title$category_header2";
		print CATEGORY_FILE "<tr><th>$category_title</th></tr>\n\n<tr><ti><table>\n";

		$divide = 5;
		$i = 0;
		foreach $icon_filename (@{$categorised_filenames{$category}}) {
			if ($i == 0) {print CATEGORY_FILE "<tr>\n"}
			if ($i != 0 && $i / $divide == (int $i / $divide)) {
				print CATEGORY_FILE "</tr><tr>\n";
			}
			print CATEGORY_FILE "<ti><fig link=\"$iconpath$icon_filename\"/></ti>\n";
			$i++;
		}
		print CATEGORY_FILE "</tr>\n";
		print CATEGORY_FILE "</table></ti></tr>\n";		
		print CATEGORY_FILE $category_footer;
		close CATEGORY_FILE;
	}
} # make_xml_pages();
