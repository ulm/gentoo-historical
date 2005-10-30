#!/usr/bin/python

"""
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
Gentoo Linux Installer

$Id: SecureXMLRPCServer.py,v 1.2 2005/10/30 00:00:36 samyron Exp $


In order to use this, you must create a certificate
with the following command:
openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
"""

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from SecureSocketServer import SecureSocketServer
import socket

class SecureXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
	def setup(self):
		self.connection = self.request
		self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
		self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)

class SecureXMLRPCServer(SecureSocketServer, SimpleXMLRPCServer):
	def __init__(self, address, cert, handler=SecureXMLRPCRequestHandler, logRequests=1):
		self.logRequests = logRequests
		SecureSocketServer.__init__(self, address, cert, handler)
		self.funcs = {}

