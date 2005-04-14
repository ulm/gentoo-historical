"""
Gentoo Linux Installer

$Id: GLILocalization.py,v 1.4 2005/04/14 15:44:03 agaffney Exp $
Copyright 2004 Gentoo Technologies Inc.


This module is used for reading and returning localized errors and informative
messages.

"""

import codecs
import os

class Localization:

	messages = None
	lang = None

	##
	# Brief description of function
	# @param self Parameter description
	# @param filename Parameter description
	# @param lang=None Parameter description
	def __init__(self, filename, lang=None):
		self.messages = {}
		self.lang = lang or os.getenv("LANG") # maybe LC_ALL
		file = codecs.open(filename, "r", "utf-8")
		for line in file.readlines():
			line = line.strip()
			parts = line.split('\t')
			if not parts[0] in self.messages: self.messages[parts[0]] = {}
			self.messages[parts[0]][parts[1]] = parts[2]

	##
	# Brief description of function
	# @param self Parameter description
	# @param message Parameter description
	def get_localized_message(self, message):
		if message in self.messages and self.lang in self.messages[message]:
			return self.messages[message][self.lang]
		else:
			return None
