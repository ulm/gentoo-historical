#!/usr/bin/python

import os
import posixpath
import BaseHTTPServer
import urllib
import cgi
import shutil
import mimetypes
from StringIO import StringIO
from threading import *
import socket
import SocketServer

last_visitor = ""

class GLIHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):

	def __init__(self, server_address):
		self.port = server_address[1]
		SocketServer.TCPServer.__init__(self, server_address, GLIHTTPRequestHandler)

class GLIHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	server_version = "GLIHTTP/0.1"

	def about(self):
		return "This is the about page"

	def aboot(self):
		return "This is the Canadian about page"

	def showargs(self):
		text = "These are the CGI params you passed:<br><br><pre>"
		text += str(self.args)
		return text

	def status(self):
		return "This is just a prototype, fool. There isn't anything to report"

	def lastvisitor(self):
		global last_visitor
		blah = "The last visitor was " + last_visitor
		last_visitor = self.address_string()
		return blah

	def parse_path(self):
		pathparts = self.path.split("?")
		self.path = pathparts[0]
		if len(pathparts) > 1:
			self.args = {}
			for arg in pathparts[1].split("&"):
				argparts = arg.split("=")
				if len(argparts) > 1:
					self.args[urllib.unquote(argparts[0])] = urllib.unquote(argparts[1])
				else:
					self.args[urllib.unquote(argparts[0])] = None

	def do_HEAD(self):
		"""Serve a HEAD request."""
		self.do_GET(head_only=True)

	def do_GET(self, head_only=False):
#		print "current thread: " + currentThread().getName()
		paths = { '/about': self.about, '/aboot': self.aboot, '/showargs': self.showargs, '/status': self.status, '/lastvisitor': self.lastvisitor }
		return_content = ""
		self.parse_path()
		if self.path in paths:
			return_content = paths[self.path]()
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.send_header("Content-Length", len(return_content))
			self.end_headers()
			self.wfile.write(return_content)
		else:
			path = self.translate_path(self.path)
			ctype = self.guess_type(path)
			try:
				f = open(path, 'rb')
			except IOError:
				self.send_error(404, "File not found")
				return None
			self.send_response(200)
			self.send_header("Content-type", ctype)
			self.send_header("Content-Length", str(os.fstat(f.fileno())[6]))
			self.end_headers()
			shutil.copyfileobj(f, self.wfile)
			f.close()

	def translate_path(self, path):
		"""Translate a /-separated PATH to the local filename syntax.

		Components that mean special things to the local file system
		(e.g. drive or directory names) are ignored.  (XXX They should
		probably be diagnosed.)

		"""
		path = posixpath.normpath(urllib.unquote(path))
		words = path.split('/')
		words = filter(None, words)
		path = os.getcwd()
		for word in words:
			drive, word = os.path.splitdrive(word)
			head, word = os.path.split(word)
			if word in (os.curdir, os.pardir): continue
			path = os.path.join(path, word)
		return path

	def copyfile(self, source, outputfile):
		shutil.copyfileobj(source, outputfile)

	def guess_type(self, path):
		base, ext = posixpath.splitext(path)
		if ext in self.extensions_map:
			return self.extensions_map[ext]
		ext = ext.lower()
		if ext in self.extensions_map:
			return self.extensions_map[ext]
		else:
			return self.extensions_map['']

	extensions_map = mimetypes.types_map.copy()
	extensions_map.update({
		'': 'application/octet-stream', # Default
		'.py': 'text/plain',
		'.c': 'text/plain',
		'.h': 'text/plain',
		})

	def log_message(self, format, *args):
		pass

def register():
	host = ''
	port = 8001
	buf = 1024
	addr = (host,port)
	# Create socket and bind to address
	UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	UDPSock.bind(addr)
	UDPSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	# Receive messages
	while 1:
		data, fromaddr = UDPSock.recvfrom(buf)
		if not data:
			print "Client has exited!"
#			break #Serve forever
			continue
		else:
			print "\nReceived message '" + data + "' from " + fromaddr[0] + ":" + str(fromaddr[1])
			
			if data == "GLIAutoInstall":	
				data = "GLIAutoInstall version 1.0"
			else:
				data = "This is the GLIAutoInstall Service. Please make you application aware of this."
			UDPSock.sendto(data, (fromaddr[0], fromaddr[1]))

	# Close socket
	UDPSock.close()
	sys.exit(0)
	return pid

def start_httpd():
	server_address = ('', 8000)
#	httpd = BaseHTTPServer.HTTPServer(server_address, GLIHTTPRequestHandler)
	httpd = GLIHTTPServer(server_address)
	httpd.serve_forever()

if __name__ == '__main__':
	httpd_thread = Thread(target=start_httpd)
	httpd_thread.setDaemon(True)
	httpd_thread.start()
	register()
