#!/usr/bin/env python
import re

enc_cat = r'[\w0-9-]+'                                # Category
enc_nam = r'([+a-z0-9-]+)'                            # Name
enc_ver = r'((?:\d+\.)*\d+[a-z]?)'                    # Version
enc_suf = r'(_(alpha\d*|beta\d*|pre\d*|rc\d*|p\d+))?' # Suffix
enc_rev = r'(-r\d+)?'                                 # Revision

enc_string=enc_cat+'/'+enc_nam+'-'+enc_ver+enc_suf+enc_rev
ebuild_name_re=re.compile(enc_string+'$', re.I)
ebuild_filename_re=re.compile(enc_string+'\.ebuild$', re.I)

def ebuild_name_check(name):
	
	
	# Handle either a path to the ebuild, or cat/pkg-ver string
	if re.search('\.ebuild$', name):
		if ebuild_filename_re.match(name):
			return 1
	else:
		if ebuild_name_re.match(name):
			return 1
	return 0

print ebuild_name_check("net-im/gaim/gaim-1..2.ebuild")
print ebuild_name_check("net-im/gaim-0.59.8-r1")

print ebuild_name_check("net-im/gaim-cvs-0.59.8-r200303s4")
print ebuild_name_check("net-im/gaim-0-r1")

print ebuild_name_check("net-im/gaim-01.2..3.4.5.6.7.8-r1")
print ebuild_name_check("net-im/gaim-0")

print ebuild_name_check("net-im/gaim-0-r1")
