#!/usr/bin/env python
# Authored by Alec Warner <antarus@gentoo.org>
# Released under the GPL Version 2
# Copyright Gentoo Foundation 2006

# Changelog: Initial release 2006/10/27

doc = """
# Purpose: This script analyzes the cvs history file in an attempt to locate package
# additions and removals.  It takes 3 arguments; two of which are optional.  It needs
# the path to the history file to read.  If a start_date is not provided it will read
# the entire file and match any addition/removal.  If you provide a start date it will
# only match thins that are after that start_date.  If you provide an end date you can
# find matches over date ranges.  If an end date is not provided it defaults to now()
"""

import sys, os, re, time, datetime

new_package = re.compile("^A(.*)\|.*gentoo-x86\/(.*)\/(.*)\|.*\|ChangeLog$")
removed_package = re.compile("^R(.*)\|.*gentoo-x86\/(.*)\/(.*)\|.*\|ChangeLog$")

class record(object):
	def __init__(self, who, date, cp, op ):
		"""
		    Who is a string
		    date is a unix timestamp
		    cp is a category/package
		    op is "added" or "removed"
		"""
		self.who = who
		self.date = datetime.datetime.fromtimestamp( date ) 
		self.package = cp
		self.op = op

	def __str__( self ):
		#return "Package %s was %s by %s on %s" % (self.package, self.op, self.who, self.date)
		return "%s,%s,%s,%s" % (self.package, self.op, self.who, self.date)

def main():
	if (len(sys.argv) < 2):
		usage()
		sys.exit(1)

	args = sys.argv[1:]
	history_file = args[0]
	# Robin requested I let one specify stdin
	if history_file == "-":
		history = sys.stdin
	else:
		history = open( history_file )

	if len(args) >= 2: 
		start_date = int(args[1])
		#start_date = time.strptime( start_date, "%d/%m/%Y")
		#start_date = time.mktime( start_date )
	else:
		start_date = 0 # no real start date then.

	if len(args) >= 3:
		end_date = int(args[2])
		#end_date = time.strptime( end_date, "%d/%m/%Y")
		#end_date = time.mktime( end_date )
	else:
		end_date = time.time()

	try:
		
		lines = history.readlines()
	except (IOError, OSError), e:
		print "Failed to open History file!"
		raise e

	removals = []
	adds = []
	for line in lines:
		match = new_package.match( line )
		if match:
			t = match.groups()[0]
			split = t.split("|")
			t = split[0]
			who = split[1]
			try:
				t = int(t, 16)
			except e:
				print "Failed to convert hex timestamp to integer"
				raise e

			if t < end_date and t > start_date:
				rec = record( who, t, match.groups()[1] + "/" + match.groups()[2], "added" )
				adds.append( rec )
				continue
			else:
				continue # date out of range
		match = removed_package.match( line )

		if match:
			t = match.groups()[0]
			split = t.split("|")
			t = split[0]
			who = split[1]
			try:
				t = int(t, 16)
			except e:
				print "Failed to convert hex timestamp to integer"
				raise e
			if t < end_date and t > start_date:
				rec = record( who, t, match.groups()[1] + "/" + match.groups()[2], "removed" )
				removals.append( rec )
				continue
			else:
				continue # date out of range
	print "Removed Packages:"
	for pkg in removals:
		print pkg

	print "Added Packages:"
	for pkg in adds:
		print pkg
	print
	print "Done."

def usage():
	print sys.argv[0] + " <history file> [start date] [end date]"
	print "Start date defaults to '0'."
	print "End date defaults to 'now'."
	print "Both dates should be specified as UNIX timestamps"
	print "(seconds since 1970-01-01 00:00:00 UTC)"
	print doc

if __name__ == "__main__":
	main()

