"""
Gentoo Linux Installer

Copyright 2004 Gentoo Technologies Inc.

$Id: GLINotification.py,v 1.2 2004/11/22 00:42:02 agaffney Exp $
"""

class GLINotification:
	def __init__(self, type, data):
		self._type = type
		self._data = data

	def get_data(self):
		return self._data

	def get_type(self):
		return self._type

	def set_data(self, data):
		self._data = data

	def set_type(self, type):
		self._type = type

