#!/usr/bin/perl
print "XML-QA-checker called.  If you have troubles,\\ contact pylon\@gentoo.org or swift\@gentoo.org\n";
foreach ( @ARGV ) {
	if ( $_ =~ /\.xml$/ and -e $_ ) {
		print "Checking $_ ... \n";
		unless ( system( "XML_CATALOG_FILES=\"/etc/xml/guidexml\" xmllint --valid --noout $_" ) == 0 ) {
			exit(1);
		}
	}
}
