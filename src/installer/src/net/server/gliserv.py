#!/usr/bin/python

import sys
sys.path.append("../..")
import os
import posixpath
import BaseHTTPServer
import urllib
import shutil
import mimetypes
from StringIO import StringIO
from threading import *
import socket
import SocketServer
import SimpleXMLRPCServer
import mimetools
import GLIServerProfile
import traceback

class SharedInfo(object):

	__shared_state = { 'client_state': {}, 'last_visitor': "", 'clients': [], 'profiles': [], 'install_profile': None, 'client_profile':None, 'temp_use': "" }

	def __init__(self):
		self.__dict__ = self.__shared_state

class Params(dict):

	def __getitem__(self, item):
		try:
			return dict.__getitem__(self, item)
		except KeyError:
			return ""

class GLIHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):

	def __init__(self, server_address):
		self.port = server_address[1]
		SocketServer.TCPServer.__init__(self, server_address, GLIHTTPRequestHandler)

class GLIHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	server_version = "GLIHTTP/0.1"

	def __init__(self, request, client_address, parent):
		self.shared_info = SharedInfo()
		self.headers_out = []
		BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, parent)

	def get_exception(self):
		etype, value, tb = sys.exc_info()
		s = traceback.format_exception(etype, value, tb)
		content = "<pre>"
		for line in s:
			content += line
		content += "</pre>"
		return content

	def wrap_in_template(self, content):
		f = open("template.html", 'rb')
		lines = f.readlines()
		f.close()
		for i in range(len(lines)):
			if lines[i] == "Main content\n":
				lines[i] = content
		return "".join(lines)
		
	def wrap_in_webgli_template(self, content):
		f = open("webgli_template.html", 'rb')
		lines = f.readlines()
		f.close()
		for i in range(len(lines)):
			if lines[i] == "Main content\n":
				lines[i] = content
		return "".join(lines)

	def status(self):
		return self.wrap_in_template("This is just a prototype, fool. There isn't anything to report")

	def lastvisitor(self):
		blah = "The last visitor was " + self.shared_info.last_visitor
		self.shared_info.last_visitor = self.address_string()
		return self.wrap_in_template(blah)

	def showclients(self):
		content = """
		<h2>Clients</h2>
		<table width="100%" cellpadding="0" cellpadding="0">
		<tr>
		  <td><u>Name</u></td>
		  <td><u>MAC</u></td>
		  <td><u>Current IP</u></td>
		  <td><u>Post-install IP</u></td>
		  <td><u>Profile</u></td>
		  <td><u>Install progress</u></td>
		</tr>
		"""
		for client in self.shared_info.clients:
			client_info = [client['name'], client['mac'], 'N/A', client['ip'], client['profile'], 'N/A']
			if client['mac'] in self.shared_info.client_state:
				client_info[2] = self.shared_info.client_state[client['mac']]['ip']
				client_info[5] = self.shared_info.client_state[client['mac']]['install_status']
			content += """
			<tr>
			  <td>%s</td>
			  <td>%s</td>
			  <td>%s</td>
			  <td>%s</td>
			  <td>%s</td>
			  <td>%s</td>
			</tr>
			""" % tuple(client_info)
		content += """
		</table>
		"""
		return self.wrap_in_template(content)

	def parse_path(self):
		self.get_params = Params()
		self.post_params = Params()
		pathparts = self.path.split("?")
		self.path = pathparts[0]
		if len(pathparts) > 1:
			args = pathparts[1]
			for arg in args.split("&"):
				argparts = arg.split("=")
				name = urllib.unquote(argparts[0])
				if len(argparts) > 1:
					data = urllib.unquote(argparts[1])
					if name in self.get_params:
						if isinstance(self.get_params[name], str):
							self.get_params[name] = [self.get_params[name]]
						self.get_params[name].append(data)
					else:
						self.get_params[name] = data
				else:
					self.get_params[name] = ""
		else:
			self.args = ""

	def valid_boundary(self, s, _vb_pattern="^[ -~]{0,200}[!-~]$"):
		import re
		return re.match(_vb_pattern, s)

	def parse_content_type(self, line):
		plist = map(lambda x: x.strip(), line.split(';'))
		key = plist.pop(0).lower()
		pdict = {}
		for p in plist:
			i = p.find('=')
			if i >= 0:
				name = p[:i].strip().lower()
				value = p[i+1:].strip()
				if len(value) >= 2 and value[0] == value[-1] == '"':
					value = value[1:-1]
					value = value.replace('\\\\', '\\').replace('\\"', '"')
				pdict[name] = value
		return key, pdict

	def do_HEAD(self):
		"""Serve a HEAD request."""
		self.do_GET(head_only=True)

	def do_POST(self, head_only=False):
		self.parse_path()
		maxlen = 0
		ctype = self.headers.getheader('content-type')
		if ctype == 'application/x-www-form-urlencoded':
			clength = self.headers.getheader('content-length')
			if clength:
				try:
					bytes = int(clength)
				except ValueError:
					pass
			if maxlen and clength > maxlen:
				raise ValueError, 'Maximum content length exceeded'
			self.args = self.rfile.read(bytes)
			if self.args:
				for arg in self.args.split("&"):
					argparts = arg.split("=")
					name = urllib.unquote(argparts[0])
					if len(argparts) > 1:
						data = urllib.unquote(argparts[1])
						if name in self.post_params:
							if isinstance(self.post_params[name], str):
								self.post_params[name] = [self.post_params[name]]
							self.post_params[name].append(data)
						else:
							self.post_params[name] = data
					else:
						self.post_params[name] = ""
		else:
			# parse_multipart in /usr/lib/python2.4/cgi.py
			ctype, pdict = self.parse_content_type(self.headers.getheader('content-type'))
			boundary = ""
			if 'boundary' in pdict:
				boundary = pdict['boundary']
			if not self.valid_boundary(boundary):
				raise ValueError,  ('Invalid boundary in multipart form: %r' % (boundary,))

			nextpart = "--" + boundary
			lastpart = "--" + boundary + "--"
			partdict = Params()
			terminator = ""

			while terminator != lastpart:
				bytes = -1
				data = None
				if terminator:
					# At start of next part.  Read headers first.
					headers = mimetools.Message(self.rfile)
					clength = headers.getheader('content-length')
					if clength:
						try:
							bytes = int(clength)
						except ValueError:
							pass
					if bytes > 0:
						if maxlen and bytes > maxlen:
							raise ValueError, 'Maximum content length exceeded'
						data = self.rfile.read(bytes)
					else:
						data = ""
				# Read lines until end of part.
				lines = []
				while 1:
					line = self.rfile.readline()
					if not line:
						terminator = lastpart # End outer loop
						break
					if line[:2] == "--":
						terminator = line.strip()
						if terminator in (nextpart, lastpart):
							break
					lines.append(line)
				# Done with part.
				if data is None:
					continue
				if bytes < 0:
					if lines:
						# Strip final line terminator
						line = lines[-1]
						if line[-2:] == "\r\n":
							line = line[:-2]
						elif line[-1:] == "\n":
							line = line[:-1]
						lines[-1] = line
						data = "".join(lines)
				line = headers['content-disposition']
				if not line:
					continue
				key, params = self.parse_content_type(line)
				if key != 'form-data':
					continue
				if 'name' in params:
					name = params['name']
				else:
					continue
				if name in partdict:
					if isinstance(partdict[name], str):
						partdict[name] = [partdict[name]]
					partdict[name].append(data)
				else:
					partdict[name] = data
			self.post_params = partdict
		self.common_handler(head_only)

	def do_GET(self, head_only=False):
		self.parse_path()
		self.common_handler(head_only)

	def common_handler(self, head_only):
		paths = {
				  'ProfileHandler': [ '/loadprofile', '/loadprofile2', '/saveprofile', '/saveprofile2' ],
				  'WebGLIHandler': ['/webgli', '/webgli/', 
						'/webgli/ClientConfig', '/webgli/saveclientconfig',
						'/webgli/NetworkMounts', '/webgli/savenetmounts',
						'/webgli/Partitioning', '/webgli/savepartitions',
						'/webgli/StageSelection', '/webgli/savestage',
						'/webgli/PortageTree', '/webgli/saveportage',
						'/webgli/GlobalUSE', '/webgli/saveglobaluse',
						'/webgli/LocalUSE', '/webgli/savelocaluse',
						'/webgli/ConfigFiles', '/webgli/saveconfigfiles',
						'/webgli/Kernel', '/webgli/savekernel',
						'/webgli/Bootloader', '/webgli/savebootloader',
						'/webgli/Timezone', '/webgli/savetimezone',
						'/webgli/Networking', '/webgli/savenetworking',
						'/webgli/Daemons', '/webgli/savedaemons',
						'/webgli/ExtraPackages', '/webgli/savepackages',
						'/webgli/Services', '/webgli/saveservices',
						'/webgli/Users', '/webgli/saveusers',
						'/webgli/Review', '/webgli/savereview', 
						'/webgli/URIBrowser',
						'/webgli/loadprofile', '/webgli/loadprofile2',
						'/webgli/saveprofile', '/webgli/saveprofile2'		],
		          'Welcome': [ '/welcome' , '/showargs'],
		          'Clients': [ '/showclients' ]
		        }
		return_content = ""
		for path in paths:
			if self.path in paths[path]:
				module = path
				# Horrible hack until I figure out a better way to skip to sending the content
				while 1:
					try:
						content_module = __import__("handlers/" + module)
						module_obj = getattr(content_module, module)(self.get_params, self.post_params, self.headers_out, self.shared_info)
					except AttributeError:
						return_content = "Caught %s (%s) in module. Traceback:\n%s" % (sys.exc_info()[0], sys.exc_info()[1], self.get_exception())
#						return_content = "Unable to load module '%s'" % module
						break
					try:
						function_obj = getattr(module_obj, 'handle')
					except AttributeError:
						return_content = "Cannot find function handle() in module '%s'" % module
						break
					try:
						self.headers_out, return_content = function_obj(self.path)
					except:
						return_content = "Caught %s (%s) in module. Traceback:\n%s" % (sys.exc_info()[0], sys.exc_info()[1], self.get_exception())
						break
					break
#				return_content = self.wrap_in_template(return_content)
				self.send_response(200)
				if not self.headers_out:
					self.headers_out.append(("Content-type", "text/html"))
				self.headers_out.append(("Content-Length", len(return_content)))
				for header in self.headers_out:
					self.send_header(header[0], header[1])
				self.end_headers()
				self.wfile.write(return_content)
				return
		# No code handler...look for actual file
		path = self.translate_path(self.path)
		if path.endswith("/"):
			path += "index.html"
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
		path = os.getcwd() + "/html/"
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

class GLINetBe:

	def __init__(self, loc):
		self._path = loc
		self.shared_info = SharedInfo()
		
	def register_client(self, mac, ip):
		self.shared_info.client_state[mac] = { 'ip': ip, 'install_status': "waiting for server", 'start_install': True }
		for client in self.shared_info.clients:
			if client['mac'] == mac: break
		else:
			self.shared_info.clients.append({ 'name': "", 'ip': "", 'mac': mac, 'profile': "" })
		return True

	def get_client_config(self, mac):
		if not self.shared_info.client_state[mac]['start_install']:
			return ""
		for client in self.shared_info.clients:
			if client['mac'] == mac:
				if not client['profile']:
					return None
				for profile in self.shared_info.profiles:
					if profile['name'] == client['profile']:
						tmpfile = open(profile['ccxmlfile'], "r")
						xml = "".join(tmpfile.readlines())
						tmpfile.close()
						return xml
		return ""

	def get_install_profile(self, mac):
		if not self.shared_info.client_state[mac]['start_install']:
			return ""
		for client in self.shared_info.clients:
			if client['mac'] == mac:
				if not client['profile']:
					return None
				for profile in self.shared_info.profiles:
					if profile['name'] == client['profile']:
						tmpfile = open(profile['ipxmlfile'], "r")
						xml = "".join(tmpfile.readlines())
						tmpfile.close()
						return xml
		return ""

	def update_client_status(self, mac, status):
		self.shared_info.client_state[mac]['install_status'] = status
		return True

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

def start_xmlrpc():
	server = SimpleXMLRPCServer.SimpleXMLRPCServer(('', 8002))
	server.register_introspection_functions()
	server.register_instance(GLINetBe("/tmp"))
	server.serve_forever()

if __name__ == '__main__':
	httpd_thread = Thread(target=start_httpd)
	httpd_thread.setDaemon(True)
	httpd_thread.start()
	xmlrpc_thread = Thread(target=start_xmlrpc)
	xmlrpc_thread.setDaemon(True)
	xmlrpc_thread.start()
	register()
