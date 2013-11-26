#!/usr/bin/python

import urllib2
from bs4 import BeautifulSoup
import sys, re, os, time

foundone = 0
glsa_list = []
package_list = []
description_list = []
bug_list = []

def getglsas(table):
	global foundone, glsa_list, package_list, description_list, bug_list
	rows = table.findAll('tr')
	for tr in rows:
		cols = tr.findAll('td')
		passt = 0
		glsanum = ''
		package = ''
		description = ''
		bugnum = ''
		for td in cols:
			if passt == 0:
				if td.a:
					# Fetch GLSA id and reconstruct the href
					glsanum = str(td.a).split()
					if str(date_from) in str(glsanum[2]):
						foundone = 1
						glsanum = glsanum[0] + " " + \
						glsanum[1] + glsanum[2] + glsanum[3]
						glsa_list.append(glsanum)
					else:
						return
					passt += 1
				else:
					# Ignore table headers
					passt = 0

			elif passt == 1:
				# Ignore severity
				passt += 1

			elif passt == 2:
				# Fetch package name and construct href
				package = str(td.string).strip()
				package = "<a href=\"http://packages.gentoo.org/package/%s\">%s</a>" % (package, package)
				package_list.append(package)
				passt += 1

			elif passt == 3:
				# Fetch description
				description = str(td.string).strip()
				description_list.append(description)
				passt += 1

			elif passt == 4:
				# Fetch Bug number and recontruct the href
				if td.a:
					bugnum = str(td.a).split()
					bugnum = bugnum[0] + " " + \
					bugnum[1] + bugnum[2] + bugnum[3]
					bug_list.append(bugnum)
				passt = 0
if __name__ == '__main__':
	# get dates from command line, else use now (time.time())
	starttime = time.gmtime(time.time() - (60 * 60 * 24 * 1))
	endtime = time.gmtime(time.time() + (60 * 60 * 24 * 31))
	# Format the string to what we expect
	date_to = time.strftime("%Y%m", endtime)
	date_from = time.strftime("%Y%m", starttime)
	glsas =	urllib2.urlopen("http://www.gentoo.org/security/en/glsa/index.xml?passthrough=1").read()
	soup = BeautifulSoup(glsas)
	table = soup.findAll('table')
	# There is probably a better way to fetch the table with the GLSAs
	table = table[2]
	print "Looking for GLSAs from %s to %s\n\n" % (date_from, date_to)
	getglsas(table)

	if foundone:
		print "\n\nFound %s GLSAs\n" % len(glsa_list)

	print "Copy and paste the following text to the GMN Security section\n\n"

	print "<h1>Security</h1>"
	if not foundone:
		print "No GLSAs have been released this month! You are safe :)"
	else:
		print "The following <a title=\"GLSAs\" " + \
		"href=\"http://www.gentoo.org/security/en/glsa/index.xml\">GLSAs</a> " + \
		"have been released by the <a title=\"Security Team\" " + \
		"href=\"http://wiki.gentoo.org/wiki/Project:Security\">Security Team" + \
		"</a>"
		print "[table tablesorter=\"1\" id=\"glsas\"]"
		print "GLSA, Package, Description, Bug"
		for x in range(0,len(glsa_list)):
			print glsa_list[x] + ", " + package_list[x] + \
			", " + description_list[x] + ", " + bug_list[x]
		print "[/table]"
	sys.exit(0)
