#! /usr/bin/env python
# genpkglist.py

# Program generates a list of current packages and writes them to stdout.

import genpkgxml
pkglist = genpkgxml.getcurrentpkgs()
for item in pkglist:
	print "%s/%s-%s-%s" % (item[3],item[0],item[1],item[2])


