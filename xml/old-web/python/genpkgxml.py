#! /usr/bin/env python
# genpkgxml.py

# Very simple program to generate "main-packages.xml", an xml page
# containing a list of all "current" packages, where "current" means the
# most up-to-date version that isn't masked.

# Note: this script expects a single argument containing a target filename
# for the XML data.

import portage, string, os, os.path, time, sys


# xml boilerplate
header = """<?xml version='1.0'?>
<mainpage id="packages">
<title>Gentoo Linux Packages</title>
<author title="Grant Goodyear"><mail link="g2boojum@gentoo.org">Grant Goodyear</mail></author>

<version>Current</version>
<date>%s</date>
""" % time.asctime(time.localtime())

tableheader = """<table>
	<tr>
		<th>Package</th>
		<th>Version</th>
		<th>Category</th>
	</tr>
"""
footer = """</table>
</body>
</section>
</chapter>
</mainpage>
"""

# get a sorted list of "current" packages, where each
# list entry is [<PN>, <PV>, <PR>, <category>]
def getcurrentpkgs():
	tree = portage.portagetree()
	currentlist = []
	for node in tree.getallnodes():
		best = tree.dep_bestmatch(node)
		cat, PN, PV, PR = portage.catpkgsplit(best)
		currentlist.append([PN, PV, PR, cat])
	currentlist.sort()
	return currentlist

# take a package (a [PN, PV, PR, category] list) and return the table entry
# for that package:
# <name> <version> <category>
def getpkgentry(pkg):
	pkgentry = "\t<tr>\n"
	pkgentry += "\t\t<ti>%s</ti>\n" % pkg[0].lower()
	pkgentry += "\t\t<ti>%s</ti>\n" % pkg[1]
	pkgentry += "\t\t<ti>%s</ti>\n" % pkg[3]
	pkgentry += "\t</tr>\n"
	return pkgentry
	

if __name__ == "__main__":
	# xml file to be generated
	out = file(sys.argv[1], "w")
	pkglist = getcurrentpkgs()
	out.write(header)
	out.write("<chapter>\n")
	out.write("<section>\n")
	out.write("<title>Today's list of %d Gentoo Packages</title>\n" % len(pkglist))
	out.write("<body>\n")
	out.write(tableheader)
	for pkg in pkglist:
		pkgentry = getpkgentry(pkg)
		out.write(pkgentry)
	out.write(footer)
