#!/usr/bin/env python
import sys, time, urllib2, libxml2
from datetime import datetime

DEV_LIST = 'http://www.gentoo.org/proj/en/devrel/roll-call/userinfo.xml'
PACKAGE_LINK = 'http://packages.gentoo.org/package/%s/%s'
ATTIC_LINK = 'http://sources.gentoo.org/viewcvs.py/gentoo-x86/%s/%s/?hideattic=0'
OUTPUT_CHARSET = 'utf-8'

def remove_profile_line(logfile):
	outfile = open(logfile, "r")
	data = []
	for line in outfile:
		if not line.lstrip().startswith("profile"):
			data.append(line)
	outfile.close()
	f = open(logfile, "w")
	f.writelines(data)
	f.close

def parse(logfile):
	# Read the log file
	cur = []
	pkgs = {'added': [], 'removed': []}
	log = open(logfile)
	for i in log:
		i = i.strip()
		if i.startswith('Added'):
			cur = pkgs['added']
		elif i.startswith('Removed'):
			cur = pkgs['removed']
		elif i.startswith('Done.'):
			break
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
		devs[tds[0].content] = tds[0].content.decode('utf-8')

	doc.freeDoc()
	return devs


def write(data, devs):
	sections = {'added': 'Addition', 'removed': 'Removal'}
	print "<h1>Package Removals/Additions</h1>"
	for s in sections:
		if s == 'added':
			print "<h2>Additions</h2>"
			print "[table]"
			print "Package, Developer, Date"
		else:
			print "<h2>Removals</h2>"
			print "[table]"
			print "Package, Developer, Date"
		for datafile in data:
			for pkg in datafile[s]:
				ldata = (PACKAGE_LINK % pkg[0], '/'.join(pkg[0]))
				if s == 'removed':
					ldata = (ATTIC_LINK % pkg[0], '/'.join(pkg[0]))
				#who = (devs[pkg[1]].encode(OUTPUT_CHARSET), pkg[1])
				who = devs[pkg[1]]
				# date format suitable for GMN posts
				when = pkg[2].strftime('%d %b %Y')
				# You should copy this to the raw html code in the
				# blog post
				print '<a href="%s">%s</a>, %s, %s' % (ldata[0], ldata[1], who, when)
		print "[/table]"

if __name__ == '__main__':
	for i in range(0, len(sys.argv)-1):
		remove_profile_line(sys.argv[i+1])
	data = []
	if len(sys.argv) < 2:
		print 'Usage: gwn_adds_removes.py <log-files>'
	else:
	        devs = developers()
		for i in range(0, len(sys.argv)-1):
			data.append(parse(sys.argv[i+1]))
		write(data, devs)
