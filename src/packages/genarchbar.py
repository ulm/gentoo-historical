#!/usr/bin/python -OO


"""genarchbar.py"""

import config
import os

def genarchbar(base=config.FEHOME,arch='',branch=''):
	if arch == '':
		switch = 'selected'
	else:
		switch = 'unselected'
	if switch == 'selected':
		colspan = len(config.ARCHLIST)
	else:
		colspan = len(config.ARCHLIST) - 2
	s = ('<table class="archnav" border="0" cellpadding="0" cellspacing="0">\n'
		'<tr><td colspan="%s" class="%s"><a href="%s">all platforms</a></td>\n' 
		% (colspan,switch,base))
	if arch != '':
		if branch == 'stable':
			switch = 'selected'
			click = os.path.join("archs",arch)
		else:
			switch = 'unselected'
			click = os.path.join("archs",arch,"stable")
		s = '''%s<td class="%s"><a href="%s%s/">stable</a></td>''' % (s,switch,base,click)
		if branch == 'testing':
			switch = 'selected'
			click = os.path.join("archs",arch)
		else:
			switch = 'unselected'
			click = os.path.join("archs",arch,"testing")
		s = '''%s<td class="%s"><a href="%s%s/">testing</a></td></tr>\n''' % (s,switch,base,click)
	s = '''%s<tr>''' % s
	percent = 100/len(config.ARCHLIST)
	for arch2 in config.ARCHLIST:
		if arch2 == arch:
			switch = 'selected'
			click = ''
		else:
			switch = 'unselected'
			click = os.path.join("archs",arch2)
		s = ('%s<td class="%s" width="%s%%"><a href="%s%s/">%s</a></td>\n' 
			% (s,switch,percent,base,click,arch2))

	s = '''%s</tr>\n</table>\n\n''' % s
	return s

if __name__ == '__main__':
	symlinks = ['altmenu.html','head.html','index.shtml','menu.html']
	for arch in [''] + config.ARCHLIST:
		for branch in ('','stable','testing'):
			outdir = os.path.join(config.LOCALHOME,"archs",arch,branch)
			os.system('mkdir -p "%s"' % outdir)
			if arch != '':
				for l in symlinks:
					command ='ln -s %s/archs/%s %s/' % (
					config.LOCALHOME,l,outdir)
					print command
					os.system(command)
			outfile = os.path.join(outdir,"archnav.html")
			s = genarchbar(config.FEHOME,arch,branch)
			open(outfile,'w').write(s)

