#!/usr/bin/env python
import re

def ebuild_name_check(name):
	
	# Category
	cat = r'[\w0-9-]+'
	# Name
	nam = r'[+a-zA-Z0-9-]+'
	# Version
	ver = r'(\d+\.)*\d+[a-z]?'
	# Suffix
	suf = r'(_(alpha\d*|beta\d*|pre\d*|rc\d*|p\d+))?'
	# Revision
	rev = r'(-r\d+)?'
	
	# Handle either a path to the ebuild, or cat/pkg-ver string
	if re.search('\.ebuild$', name):
		if re.match(cat+'/'+nam+'/'+nam+'-'+ver+suf+rev+'\.ebuild$' , name):
			return 1
	else:
		if re.match(cat+'/'+nam+'-'+ver+suf+rev+'$' , name):
			return 1
	return 0



print ebuild_name_check("net-im/gaim/gaim-1..2.ebuild")
print ebuild_name_check("net-im/gaim-0.59.8-r1")
