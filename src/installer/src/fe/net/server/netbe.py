#!/usr/bin/python
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
"""
This script will setup two servers and then run forever.
The first is a udp discovery server. Its job it to tell any clients where
the other server is. Also it can send out a client config file to allow static
ip address boxes to use the service as well.
The second server is a XMLRPC server that will serve config files and allow network
based logging. 

Files are searched for via the pxe naming standard.
Example:
005070E808D0
  005070E808
  005070E8
  005070
  0050
  00
  default
  
Naming conventions of the config directory are as follows:

config_dir
	|
	005070E808D0.cc.xml	#Client Config File
	005070E808D0.ip.xml	#Install Profile File
	005070E808D0.log	#Log for that mac
	main.log			#Main log
"""
import sys,os,socket,shelve
sys.path.append("../../..")
import SimpleXMLRPCServer
import xmlrpclib
import GLIUtility
import GLIClientController
from GLIException import *

#The XMLRPC class
class GLINetBe:
	def __init__(self, loc):
		self._path = loc
		
	def _find_config(self, mac, extension):
		mac.replace(':','')
		while not GLIUtility.is_file(mac + extension):
				if mac != mac[:2]:
					mac = mac[:2]
				else:
					mac = 'default'
					break
		try:
			f = open(mac + extension)
		except:
			raise GLIException('NetBeError', 'fatal', 'GLINetBe._find_config', 'We are unable to find a config file.')
		return f
		
	def get_client_config(self, mac):
		try:
			f = self._find_config(mac, '.cc.xml')
			data = file.read()
		except:
			return xmlrpclib.Fault("GLIMissingConfig","The server does not have a GLICLientConfiguration for you. Check with the server admin.")
		file.close()
		return data
	
	def set_client_config(self, mac, cc):
		file = open(self._path + mac + '.cc.xml', 'w')
		file.write(cc)
		file.close()
		return True		
	
	def get_install_profile(self, mac):
		try:
			f = self._find_config(mac, '.cc.xml')
			data = file.read()
		except:
			return xmlrpclib.Fault("GLIMissingConfig","The server does not have a InstallProfile for you. Check with the server admin.")
		file.close()
		return data
	
	def set_install_profile(self, mac, ip):
		file = open(self._path + mac + '.ip.xml', 'w')
		file.write(ip)
		file.close()
		return True
		
	def log_event(self, mac, data):
		file = open(self._path + mac + ".log", "a")
		file.write(data)
		file.close()
		file = open(self._path + "main.log", "a")
		file.write(data)
		file.close()

#start network discovery service
def register(local_port, cc_path):
	pid = os.fork()
	if pid == 0:
		host = ''
		port = local_port - 1 #It will send out the information on a port one less than the RPCServer's port
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
				break #Serve forever
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
				
#start XMLRPCServer
def rpc_start(port, db_loc):
	pid = os.fork()
	if pid == 0:
		#start XMLRPCServer
		server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", port))
		server.register_introspection_functions()
		server.register_instance(GLINetBe(db_loc))
		server.serve_forever()
		sys.exit(0)
	return pid

if __name__ == '__main__':
	local_port = 12345
	loc = "/tmp/install/" #Where all the config files are
	if not os.path.isdir(loc):
		print "You must specify a valid directory!"
		sys.exit(0)
	
	pid1 = register(local_port, loc)
	pid2 = rpc_start(local_port, loc)

	#Wait for the child processes to exit
	os.waitpid(pid1,0)
	os.waitpid(pid2,0)
