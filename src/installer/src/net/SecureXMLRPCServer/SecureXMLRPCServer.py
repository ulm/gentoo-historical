#!/usr/bin/python

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from SecureSocketServer import SecureSocketServer
import socket

"""
In order to use this, you must create a certificate
with the following command:
openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
"""

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

