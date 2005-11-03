from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from OpenSSL import SSL
import SocketServer
import socket

class SecureSocketServer(SocketServer.TCPServer, SocketServer.ThreadingMixIn):
	def __init__(self, addr, cert, requestHandler):
		SocketServer.TCPServer.__init__(self, addr, requestHandler)
		ctx = SSL.Context(SSL.SSLv23_METHOD)
		ctx.use_privatekey_file(cert)
		ctx.use_certificate_file(cert)

		tmpConnection = SSL.Connection(ctx, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
		self.socket = SecureSocketConnection(tmpConnection)

		self.server_bind()
		self.server_activate()

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

"""
This class is necessary because SSL.Connection
does not have a shutdown() method that accepts
one argument.
"""

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
