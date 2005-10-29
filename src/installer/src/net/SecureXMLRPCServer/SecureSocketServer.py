from OpenSSL import SSL
import SocketServer
import socket
from SecureSocketConnection import SecureSocketConnection

class SecureSocketServer(SocketServer.TCPServer):
	def __init__(self, addr, cert, requestHandler):
		SocketServer.TCPServer.__init__(self, addr, requestHandler)
		ctx = SSL.Context(SSL.SSLv23_METHOD)
		ctx.use_privatekey_file(cert)
		ctx.use_certificate_file(cert)

		tmpConnection = SSL.Connection(ctx, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
		self.socket = SecureSocketConnection(tmpConnection)

		self.server_bind()
		self.server_activate()
