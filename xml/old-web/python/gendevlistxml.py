#! /usr/bin/env python
# genpkgxml.py

# Very simple program to generate "main-devlist.xml", an xml page
# containing a list of all Gentoo Linux developers.

# Note: this script expects two arguments containing input and output
# filenames.  The input filename is the filename of the
# text file that has, as each line, a tab-delimited set of fields 
# containing the developer's user name, actual name, and responsibilities
# for the XML data.  The associated file has as each line (tab delimited) the developer's
# user name, actual name, and responsibilities.  The output filename should be
# the filename of the generated xml output.

#import portage, string, os, os.path, time, sys
import time, sys

# xml boilerplate
header = """<?xml version='1.0' encoding="ISO-8859-15" ?>
<mainpage id="devlist">
<title>Gentoo Linux Developers</title>
<author title="Grant Goodyear"><mail link="g2boojum@gentoo.org">Grant Goodyear</mail></author>

<version>Current</version>
<date>%s</date>
<chapter>
<section>
<title>Gentoo Linux Roster of Developers</title>
<body>
""" % time.asctime(time.localtime())

tableheader = """<table>
	<tr>
		<th>Name</th>
		<th>User name</th>
		<th>Location</th>
		<th>Responsibilities</th>
	</tr>
"""
footer = """</table>
<note>Developers may be reached by sending e-mail to the developer's user
name @gentoo.org.  Many developers may be found on IRC (FreeNode) in #gentoo
using their user name as their IRC nick.</note>
</body>
</section>
</chapter>
</mainpage>
"""

def buildxml(devinfo):
	xml = header + tableheader
	for line in devinfo:
		# remove \n
		line = line[:-1]
		# separate into user name, name, location, responsibilities, web page
		mys=line.split(":")
		if len(mys)<5:
			print "error in: \""+line+"\", exiting."
			sys.exit(1)
		user,name,location,duties,web = line.split(":")[0:5]
		# generate the table entry for the current developer
		# commented out version w/ mail links because of spam robots.
		#tablexml = '\t<tr>\n\t\t<ti>%s</ti>\n\t\t<ti><mail link="%s@gentoo.org">%s</mail></ti>\n\t\t<ti>%s</ti>\n\t\t<ti>%s</ti>\n\t</tr>\n' \
		#	% (name,user,user,location,duties)
		if web:
			if web == "yes":
				url = "http://www.gentoo.org/~%s/" % user
			else:
				url = web
			tablexml = '\t<tr>\n' \
					   '\t\t<ti><uri link="%s">%s</uri></ti>\n' \
			           '\t\t<ti>%s</ti>\n' \
					   '\t\t<ti>%s</ti>\n' \
					   '\t\t<ti>%s</ti>\n' \
					   '\t</tr>\n' \
					      % (url,name,user,location,duties)
		else: #no web page
			tablexml = '\t<tr>\n' \
					   '\t\t<ti>%s</ti>\n' \
			           '\t\t<ti>%s</ti>\n' \
					   '\t\t<ti>%s</ti>\n' \
					   '\t\t<ti>%s</ti>\n' \
					   '\t</tr>\n' \
					      % (name,user,location,duties)
		xml += tablexml
	xml += footer
	return xml
	

if __name__ == "__main__":
	# check number of arguments
	if len(sys.argv) != 3:
		print "usage: python gendevlistxml.py inputname outputname"
		sys.exit(1)
	# get developer info
	txtfile = file(sys.argv[1], "r")
	devtxt = txtfile.readlines()
	txtfile.close()
	# generate the developer xml
	devxml = buildxml(devtxt)
	# write out the xml to a file
	xmlfile = file(sys.argv[2], "w")
	xmlfile.writelines(devxml)
	xmlfile.close()
