"""
Gentoo Linux Installer

Copyright 2004 Gentoo Technologies Inc.

$Id: GLINotification.py,v 1.4 2005/04/16 03:12:27 agaffney Exp $
"""

##
# This class provides a wrapper for passing data from the backend to the frontend
class GLINotification:
	##
	# Initialization function for GLINotification
	# @param type String specifying the type of data contained in the next parameter
	# @param data Data to pass
	def __init__(self, type, data):
		self._type = type
		self._data = data

	##
	# Retrieves data
	def get_data(self):
		return self._data

	##
	# Retrieves data type
	def get_type(self):
		return self._type

	##
	# Sets data
	# @param data Data (duh)
	def set_data(self, data):
		self._data = data

	##
	# Sets data type
	# @param type Type (duh)
	def set_type(self, type):
		self._type = type

