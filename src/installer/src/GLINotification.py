"""
Gentoo Linux Installer

Copyright 2004 Gentoo Technologies Inc.

$Id: GLINotification.py,v 1.1 2004/11/11 18:56:00 samyron Exp $
"""

class GLINotification:
	def __init__(self, type, data):
		self._type = type
		self._data = data

	def getData(self):
		return self._data

	def getType(self):
		return self._type

	def setData(self, data):
		self._data = data

	def setType(self, type):
		self._type = type

