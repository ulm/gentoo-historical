"""
Gentoo Linux Installer

Copyright 2004 Gentoo Technologies Inc.

$Id: GLINotification.py,v 1.3 2005/04/14 15:44:03 agaffney Exp $
"""

class GLINotification:
	##
	# Brief description of function
	# @param self Parameter description
	# @param type Parameter description
	# @param data Parameter description
	def __init__(self, type, data):
		self._type = type
		self._data = data

	##
	# Brief description of function
	# @param self Parameter description
	def get_data(self):
		return self._data

	##
	# Brief description of function
	# @param self Parameter description
	def get_type(self):
		return self._type

	##
	# Brief description of function
	# @param self Parameter description
	# @param data Parameter description
	def set_data(self, data):
		self._data = data

	##
	# Brief description of function
	# @param self Parameter description
	# @param type Parameter description
	def set_type(self, type):
		self._type = type

