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
from threading import Thread
import socket
import SocketServer
import mimetools
import GLIServerProfile
import time
import base64
import traceback
import cgi
import re
from GLIException import GLIException
try:
	from SecureXMLRPCServer import SecureSocketServer
except:
	pass

debug = False
pyhtml_mtimes = {}
pyhtml_cache = {}
needauth = False
webuser = "gli"
webpass = "gli"
progname = None

class SharedInfo(object):

	__shared_state = { 'client_state': {}, 'last_visitor': "", 'clients': [], 'profiles': [], 'install_profile': None, 'client_profile':None, 'temp_use': "", 'devices':None, 'drive_to_partition':"", 'error_message': "", 'advanced_mode': True }

	def __init__(self):
		self.__dict__ = self.__shared_state

class Params(dict):

	def __getitem__(self, item):
		try:
			return dict.__getitem__(self, item)
		except KeyError:
			return ""

class GLIHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	server_version = "GLIHTTP/0.1"

	def __init__(self, request, client_address, parent):
		self.shared_info = SharedInfo()
		self.headers_out = []
		BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, parent)

	def get_exception(self):
		etype, value, tb = sys.exc_info()
		s = traceback.format_exception(etype, value, tb)
		content = ""
		for line in s:
			content += line
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

	def redirect(self, url):
		raise GLIException("GLIHTTPRedirect", 'notice', "redirect", url)

	def first_substring(self, somestring, *substrings):
		result = (None, len(somestring))
		for substring in substrings:
			index = somestring.find(substring)
			if index > -1 and index < result[1]:
				result = (substring, index)
		return result[0]

	def process_html(self, htmlfile):
		openrun, closerun = '<?', '?>'
		openprint, closeprint = '<%', '%>'
		openblock, closeblock = '<:', ':>'
		output = [
		          "class TempHandler(object):",
		          "\tdef __init__(self):",
		          "\t\tpass",
		          "\tdef redirect(self, url):",
		          "\t\traise Exception('redirect:' + url)",
		          "\tdef handle(self, get_params, post_params, headers_out, shared_info):",
		          "\t\treturn_content = ''",
		         ]
		indentlevel = 2
		incodeblock = False
		printre = re.compile(r"(^.+: |^\s+|^)print ")
		f = open(htmlfile, "r")
		html = f.readlines()
		f.close()
#		for i, line in enumerate(html):
		while len(html):
			line = html.pop(0)
#			line = line.strip()
			if line.endswith("\n"):
				line = line[:-1]
			while line:
				if incodeblock:
					if line.startswith(closerun):
						incodeblock = False
						line = line.split(closerun, 1)[1]
						continue
#					if line.endswith("\n"):
#						line = line[:-1]
					line = printre.sub(r'\1return_content += ', line)
					output.append('\t' * indentlevel + line)
					break
				else:
#					line = line.strip()
					if line.startswith(openrun):
						if line.find(closerun) == -1:
							incodeblock = True
							break
						else:
							tmpline = line.split(openrun, 1)[1].split(closerun, 1)[0].strip()
							line = line.split(closerun, 1)[1]
							if tmpline.startswith("include "):
								path = self.translate_path(tmpline[8:])
								f = open(path, 'r')
								morehtml = f.readlines()
								f.close()
								html = morehtml + html
								line = ""
								break
							tmpline = printre.sub(r'\1return_content += ', tmpline)
							output.append('\t' * indentlevel + tmpline)
					elif line.startswith(openprint):
						tmpline = line.split(openprint, 1)[1].split(closeprint, 1)[0].strip()
						line = line.split(closeprint, 1)[1]
#						tmpline = 'return_content += cgi.escape(%s)' % tmpline
						tmpline = 'return_content += %s' % tmpline
						if not line:
							tmpline += ' + "\\n"'
						output.append('\t' * indentlevel + tmpline)
					elif line.startswith(openblock):
						line = line.split(openblock, 1)[1].strip()
						if line == "else:":
							indentlevel -= 1
						if line.startswith("elif "):
							indentlevel -= 1
						output.append('\t' * indentlevel + line)
						indentlevel += 1
						break
					elif line.startswith(closeblock):
						indentlevel -= 1
						line = line.split(closeblock, 1)[1]
					else:
						substring = self.first_substring(line, openrun, openprint, openblock)
						if not substring:
							tmpline = line
							line = ""
						else:
							tmpline = line.split(substring, 1)[0]
							line = substring + line.split(substring, 1)[1]
#						tmpline = 'return_content += r"""%s"""' % tmpline
						tmpline = 'return_content += %r' % tmpline
						if not line:
							tmpline += ' + "\\n"'
						output.append('\t' * indentlevel + tmpline)
		output += ["\t\treturn return_content"]
		return "\n".join(output)

	def status(self):
		return self.wrap_in_template("This is just a prototype, fool. There isn't anything to report")

	def lastvisitor(self):
		blah = "The last visitor was " + self.shared_info.last_visitor
		self.shared_info.last_visitor = self.client_address[0]
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
		if needauth:
			authed = False
			if self.headers.getheader('authorization'):
				username, password = base64.decodestring(self.headers.getheader('authorization').split(" ")[-1]).split(":")
				if username == webuser and password == webpass:
					authed = True
			if not authed:
				self.send_response(401)
				self.send_header("WWW-Authenticate", 'Basic realm="GLI"')
				self.end_headers()
				self.wfile.write("<h1>401 Not Authorized</h1>You must supply the correct username and password to access this resource")
				return
		return_content = ""
		if debug:
			print time.ctime() + " - " + self.client_address[0] + " - " + self.path
			print "get_params: " + str(self.get_params)
			print "post_params: " + str(self.post_params)
			print "----------------------------------------------------"
		# No code handler...look for actual file
		path = self.translate_path(self.path)
		if os.path.exists(path):
			if path.endswith("/"):
				for index_file in ["index.pyhtml", "index.html"]:
					if os.path.exists(path + index_file):
						path += index_file
		if path.endswith(".pyhtml"):
			while 1:
				try:
					try:
						mtime = os.stat(path)[8]
					except OSError:
						pass
					if path in pyhtml_mtimes and mtime == pyhtml_mtimes[path]:
						tmpcode = pyhtml_cache[path]
					else:
						try:
							tmpcode = self.process_html(path)
						except IOError:
							self.send_response(404)
							self.end_headers()
							self.wfile.write("<h2>404 Not Found</h2>The resource you were looking for does not exist")
							return
						except Exception, e:
							if debug:
								print "Caught %s (%s) while trying to process '%s'. Traceback:\n<pre>\n%s</pre>" % (sys.exc_info()[0], sys.exc_info()[1], path, self.get_exception())
							return_content = "Caught %s (%s) while trying to process '%s'. Traceback:\n<pre>\n%s</pre>" % (sys.exc_info()[0], sys.exc_info()[1], path, self.get_exception())
							break
					exec tmpcode
					tmphandler = TempHandler()
					return_content = tmphandler.handle(self.get_params, self.post_params, self.headers_out, self.shared_info)
				except Exception, e:
					errmsg = str(e)
					if errmsg.split(":")[0] == "redirect":
						self.send_response(302)
						self.send_header("Location", errmsg.split(":", 1)[1])
						self.end_headers()
						return
					if debug:
						print "Caught %s (%s) while trying to process '%s'. Traceback:\n<pre>\n%s</pre>" % (sys.exc_info()[0], sys.exc_info()[1], path, self.get_exception())
					return_content = "Caught %s (%s) while trying to process '%s'. Traceback:\n<pre>\n%s</pre><br>Generated code:\n<pre>\n%s</pre>" % (sys.exc_info()[0], sys.exc_info()[1], path, self.get_exception(), cgi.escape(tmpcode))
				break
			self.send_response(200)
			for header in self.headers_out:
				if header[0] == "Content-type": break
			else:
				self.headers_out.append(("Content-type", "text/html"))
			self.headers_out.append(("Content-Length", len(return_content)))
			for header in self.headers_out:
				self.send_header(header[0], header[1])
			self.end_headers()
			if not head_only:
				self.wfile.write(return_content)
		else:
			ctype = self.guess_type(path)
			try:
				f = open(path, 'rb')
			except IOError:
				self.send_error(404, "File not found")
				return None
			filestat = os.stat(path)
			filesize = filestat[6]
			filemtime = filestat[8]
			self.send_response(200)
			self.send_header("Content-type", ctype)
			self.send_header("Content-Length", str(filesize))
			self.send_header("Last-Modified", time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(filemtime)))
			self.end_headers()
			if not head_only:
				shutil.copyfileobj(f, self.wfile)
			f.close()

	def translate_path(self, path):
		return os.getcwd() + "/html/" + urllib.unquote(path)

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

class GLIHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):

	def __init__(self, server_address):
		self.port = server_address[1]
		SocketServer.TCPServer.__init__(self, server_address, GLIHTTPRequestHandler)
try:
	class GLISecureHTTPServer(SecureSocketServer, BaseHTTPServer.HTTPServer):

		def __init__(self, server_address):
			self.port = server_address[1]
			SecureSocketServer.__init__(self, server_address, 'server.pem', GLISecureHTTPRequestHandler)

	class GLISecureHTTPRequestHandler(GLIHTTPRequestHandler):

		def setup(self):
			self.connection = self.request
			self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
			self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)
except:
	pass


class GLINetBe:

	def __init__(self, loc):
		self._path = loc
		self.shared_info = SharedInfo()
		
	def register_client(self, mac, ip):
		self.shared_info.client_state[mac] = { 'ip': ip, 'install_status': "waiting for server", 'start_install': False }
		for client in self.shared_info.clients:
			if client['mac'] == mac: break
		else:
			self.shared_info.clients.append({ 'hostname': "", 'current_ip': ip, 'mac': mac, 'profile': "" , 'post_ip': "", 'status': "waiting for server"})
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
						#INJECT THE CUSTOM CLIENT SETTNGS HERE
						return xml
		return ""

	def update_client_status(self, mac, status):
		self.shared_info.client_state[mac]['install_status'] = status
		return True

	def is_alive(self):
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
				data = "This is the GLIAutoInstall Service. Please make your application aware of this."
			UDPSock.sendto(data, (fromaddr[0], fromaddr[1]))

	# Close socket
	UDPSock.close()
	sys.exit(0)
	return pid

def start_httpd():
	server_address = ('', 8000)
	try:
		httpd = GLISecureHTTPServer(server_address)
	except:
		print "Couldn't do HTTPS for web server, falling back to HTTP..."
		httpd = GLIHTTPServer(server_address)
	httpd.serve_forever()

def start_xmlrpc():
	try:
		from SecureXMLRPCServer import SecureXMLRPCServer
		server = SecureXMLRPCServer(('', 8002), 'server.pem')
	except:
		print "Couldn't do HTTPS for XMLRPC, falling back to HTTP..."
		from SimpleXMLRPCServer import SimpleXMLRPCServer
		server = SimpleXMLRPCServer(('', 8002))
	server.register_introspection_functions()
	server.register_instance(GLINetBe("/tmp"))
	server.serve_forever()

def usage():
	print
	print "Usage:"
	print "  " + progname + " [-h|--help] [[-d|--debug]] [[-a|--auth] <user>:<password>]"
	print
	print "Options:"
	print "  -h|--help     That should be quite obvious"
	print
	print "  -d|--debug    Enable debug mode. This currently prints get_params and"
	print "                post_params for each request"
	print
	print "  -a|--auth     Require basic HTTP auth to access the web interface. The"
	print "                arguments <user> and <password> are required."
	sys.exit(1)

if __name__ == '__main__':
	progname = sys.argv.pop(0)
	while len(sys.argv) >= 1:
		arg = sys.argv.pop(0)
		if arg == "-d" or arg == "--debug":
			debug = True
		elif arg == "-a" or arg == "--auth":
			if len(sys.argv) >= 1:
				auth = sys.argv.pop(0)
				auth = auth.split(":")
				if not len(auth) == 2:
					print "The authentication credentials must be specified at <user>:<password>"
					usage()
				webuser, webpass = auth
				needauth = True
			else:
				print "The --auth option required an additional argument"
				usage()
		elif arg == "-h" or arg == "--help":
			usage()
		else:
			print "You have supplied an invalid argument"
			usage()
	httpd_thread = Thread(target=start_httpd)
	httpd_thread.setDaemon(True)
	httpd_thread.start()
	xmlrpc_thread = Thread(target=start_xmlrpc)
	xmlrpc_thread.setDaemon(True)
	xmlrpc_thread.start()
	register()
