"""
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
Gentoo Linux Installer

$Id: SecureSocketServer.py,v 1.2 2005/10/30 00:00:36 samyron Exp $
"""

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
