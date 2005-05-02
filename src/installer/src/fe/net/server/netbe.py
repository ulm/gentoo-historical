#!/usr/bin/python
"""
This script will setup two servers and then run forever.
The first is a udp discovery server. Its job it to tell any clients where
the other server is. Also it can send out a client config file to allow static
ip address boxes to use the service as well.
The second server is a XMLRPC server that will serve config files and allow network
based logging. Naming conventions are as follows:

config_dir
	|
	192.168.0.3.cc.xml	#Client Config File
	192.168.0.3.ip.xml	#Install Profile File
	192.168.0.3.log		#Log for that ip
	main.log		#Main log
It is also recommended that if you don't use dhcp that you make a symbolic link of the
computer's mac address to the ip version of the cc.xml file. Otherwise the box will not
be able to start the install.
Ex. 01:23:45:67:89:ab.cc.xml -> 192.168.0.3.cc.xml
"""
import sys,os,socket,shelve
sys.path.append("../..")
import SimpleXMLRPCServer
import xmlrpclib
import GLIUtility
import GLIClientController

#The XMLRPC class
class GLINetBe:
	def __init__(self, loc):
		self._path = loc
		
	def get_client_config(self, ip):
		if not GLIUtility.is_file(self._path + ip + ".cc.xml"):
			return xmlrpclib.Fault("GLIMissingConfig","The server does not have a GLICLientConfiguration for you. Check with the server admin.")
		file = open(self._path + ip + ".cc.xml", "r")
		data = file.read()
		file.close()
		return data
		
	def get_install_profile(self, ip):
		if not GLIUtility.is_file(self._path + ip + ".ip.xml"):
			return xmlrpclib.Fault("GLIMissingConfig","The server does not have a InstallProfile for you. Check with the server admin.")
		file = open(self._path + ip + ".ip.xml", "r")
		data = file.read()
		file.close()
		return data
		
	def log_event(self, ip, data):

		file = open(self._path + ip + ".log", "a")
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
				
				if data == "GLIInstallAuto":	
					file = open(cc_path + fromaddr[0] + "cc.xml", "r")
					data = file.read()
					file.close()
				elif data == "PING":
					data = "PONG"
				else:
					data = "GLIClientConfiguration not found!"
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
