"""
Gentoo Linux Installer

$Id: GLISayWhat.py,v 1.1 2005/02/18 07:15:01 agaffney Exp $
Copyright 2004 Gentoo Technologies Inc.


This module is used for reading and returning localized errors and informative
messages.

"""

import codecs
import os

class SayWhat:

	messages = None

	def __init__(self, filename):
		self.messages = {}
		file = codecs.open(filename, "r", "utf-8")
		for line in file.readlines():
			parts = line.split('\t')
			if not parts[0] in self.messages: self.messages[parts[0]] = {}
			self.messages[parts[0]][parts[1]] = parts[2]

	def get_localized_message(self, message, lang=None):
		localized_message = None

		if not lang:
			lang = os.getenv("LANG") # maybe LC_ALL
		if message in self.messages and lang in self.messages[message]:
			localized_message = self.messages[message][lang]
		return localized_message
