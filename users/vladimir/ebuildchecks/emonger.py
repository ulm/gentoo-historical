#!/usr/bin/env python
import re




def ebuild_name_check(name):
	cat = r'[\w0-9-]+'
	nam = r'([a-zA-Z0-9-]+)'
	ver = r'[\d\.]+[a-z]?'
	suf = r'(_(alpha|beta|pre|rc|p)\d*)?'
	rev = r'(-r\d+)?'
	if re.search('\.ebuild$', name):
		if re.match(cat+'/'+nam+'/'+nam+'-'+ver+suf+rev+'\.ebuild$' , name):
			return 1
	else:
		if re.match(cat+'/'+nam+'-'+ver+suf+rev+'$' , name):
			return 1
	return 0



print ebuild_name_check("net-im/gaim/gaim-0.59.8-r1.ebuild")
print ebuild_name_check("net-im/gaim-0.59.8-r1")
