#! /usr/bin/env python
# genpkglist.py

# Program generates a list of current packages and writes them to stdout.

import genpkgxml
for item in genpkgxml.getcurrentpkgs():
	print "%s:%s-%s:%s" % (item[0],item[1],item[2],item[3])


