#!/usr/bin/env python
import sys, time, urllib2, libxml2
from datetime import datetime

DEV_LIST = 'http://www.gentoo.org/proj/en/devrel/roll-call/userinfo.xml'
PACKAGE_LINK = 'http://packages.gentoo.org/packages/?category=%s;name=%s'
ATTIC_LINK = 'http://sources.gentoo.org/viewcvs.py/gentoo-x86/%s/%s/?hideattic=0'
OUTPUT_CHARSET = 'utf-8'

def parse(logfile):
	
	# Read the log file
	
	pkgs = {'added': [], 'removed': []}
	log = open(logfile)
	for i in log:
		i = i.strip()
		if i.startswith('Added'):
			cur = pkgs['added']
		elif i.startswith('Removed'):
			cur = pkgs['removed']
		elif not i:
			break
		else:
			cur.append(i)
	log.close()
	
	# Parse the information
	
	for op in ('added', 'removed'):
		for idx, pkg in enumerate(pkgs[op]):
			pkg = pkg.split(',')
			cp = tuple(pkg[0].split('/'))
			dev = pkg[2]
			dt = datetime(*(time.strptime(pkg[3], '%Y-%m-%d %H:%M:%S')[0:6]))
			pkgs[op][idx] = (cp, dev, dt)
	
	return pkgs

def developers():
	
	html = urllib2.urlopen(DEV_LIST).read()
	doc = libxml2.htmlParseDoc(html, 'utf-8')
	rows = doc.xpathEval('//table[@class = "ntable"]/tr')
	devs = {}
	
	for i in rows[1:]:
		tds = i.xpathEval('td')
		devs[tds[0].content] = tds[1].content.decode('utf-8')
	
	doc.freeDoc()
	return devs
	

def write(data, devs, attic=False):
	
	sections = {'added': 'Addition', 'removed': 'Removal'}
	for s in sections:
		
		print '<section>'
		print '<title>%s:</title>' % (sections[s] + 's')
		print '<body>'
		print ''
		
		print '<table>'
		print ''
		print '<tr>'
		print '<th>Package:</th>'
		print '<th>%s date:</th>' % sections[s]
		print '<th>Contact:</th>'
		print '</tr>'
		print ''
		
		for pkg in data[s]:
			print '<tr>'
			ldata = (PACKAGE_LINK % pkg[0], '/'.join(pkg[0]))
			if s == 'added':
				print '<ti><uri link="%s">%s</uri></ti>' % ldata
			else:
				if attic:
					ldata = (ATTIC_LINK % pkg[0], '/'.join(pkg[0]))
					print '<ti><uri link="%s">%s</uri></ti>' % ldata
				else:
					print '<ti>%s</ti>' % ldata[1]
			print '<ti>%s</ti>' % pkg[2].strftime('%d %b %Y')
			mdata = (pkg[1], devs[pkg[1]].encode(OUTPUT_CHARSET))
			print '<ti><mail link="%s@gentoo.org">%s</mail></ti>' % mdata
			print '</tr>'
			print ''
		
		print '</table>'
		print ''
		
		print '</body>'
		print '</section>'
		print ''


if __name__ == '__main__':
	if len(sys.argv) < 2 or len(sys.argv) > 3:
		print 'Usage: gwn_adds_removes.py <log-file> [--attic]'
	else:
		data = parse(sys.argv[1])
		devs = developers()
		attic = len(sys.argv) == 3 and sys.argv[2] == '--attic'
		write(data, devs, attic)
