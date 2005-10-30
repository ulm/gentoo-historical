"""
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
Gentoo Linux Installer

$Id: SecureSocketConnection.py,v 1.2 2005/10/30 00:00:36 samyron Exp $

This class is necessary because SSL.Connection
does not have a shutdown() method that accepts
one argument.
"""

from OpenSSL import SSL

class SecureSocketConnection:
	"""
	Set __dict__["connection"] to be the Connection object.
	"""
	def __init__(self, connection):
		self.__dict__["connection"] = connection

	"""
	This simulates referencing Connection.name
	"""
	def __getattr__(self, name):
		return getattr(self.__dict__["connection"], name)

	"""
	According to the Python Language Reference Section 3.3.2, 
	__setattr__() should insert the name/value pair into the
	instance attribute dictionary. In this case, we don't want
	to put the name/value pair directly into our instance
	dictionary, instead, we store it in the Connection's instance
	dictionary.
	"""
	def __setattr__(self, name, value):
		setattr(self.__dict__["connection"], name, value)

	def shutdown(self, how=1):
		self.__dict__["connection"].shutdown()

	"""
	We need to provide this method so that accept() returns a
	SecureSocketConnection object instead of a Connection object.
	"""
	def accept(self):
		connection, address = self.__dict__["connection"].accept()
		return (SecureSocketConnection(connection), address)
