#!/usr/bin/python
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.

import sys, time, socket
sys.path.append("../..")
import GLIException
import GLIInstallProfile
import GLIClientConfiguration
import GLIClientController
import GLIUtility
import xmlrpclib
import dialog
import GLIGenDialog

def find_macip():
	device = None
	device_name = 'eth'
	for num in range(5):
		if GLIUtility.is_eth_device(device_name + str(num)):
			device = GLIUtility.get_eth_info(num)
			break
		else:
			raise GLIException("NetFeError", 'fatal', 'setup_network',"Was unable to find a network inferface.")
	return device[0], device[1]

def find_server():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('', 0))
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	s.settimeout(15)
	
	count = 1
	response = ""
	while count <= 3:
		print "Broadcasting for server...try " + str(count)
		s.sendto("GLIAutoInstall", ('255.255.255.255', 8001))
		response, fromaddr = s.recvfrom(1024)
		if response:
			print "Server found at " + str(fromaddr[0]) + " port " + str(fromaddr[1])
			break
		count = count + 1
	return fromaddr[0], int(fromaddr[1]) + 1

if __name__ == '__main__':
	args = {}
	i = 1
	pretend = False
	while i < len(sys.argv):
		if sys.argv[i] == "-s" or sys.argv[i] == "--server":
			i += 1
			tmpserver = sys.argv[i]
			tmpserverparts = tmpserver.split(":")
			if not len(tmpserverparts) == 2:
				print "Invalid argument for option " + sys.argv[i-1] + ". Terminating."
				sys.exit(0)
			args['server_ip'] = tmpserverparts[0]
			args['server_port'] = tmpserverparts[1]
		elif sys.argv[i] == "-p" or sys.argv[i] == "--pretend":
			pretend = True
		else:
			print "Invalid option " + sys.argv[i] + ". Terminating."
			sys.exit(0)
		i += 1

	local_mac, local_ip = find_macip()
	if 'server_ip' in args and 'server_port' in args:
		server_ip, server_port = args['server_ip'], args['server_port']
	else:
		server_ip, server_port = find_server()
	try:
		server = xmlrpclib.ServerProxy("https://" + server_ip + ":" + str(server_port))
		server.is_alive()
	except:
		print "Can't connect via HTTPS, trying HTTP..."
		server = xmlrpclib.ServerProxy("http://" + server_ip + ":" + str(server_port))
	registered = False
	try:
		registered = server.register_client(local_mac, local_ip)
		print "Registered with server with XMLRPC"
	except:
		pass
	if not registered:
		print "Could not register with server. Terminating."
		sys.exit(1)

	if pretend:
		print "In pretend mode...quitting"
		sys.exit(0)

	print "Waiting for client config and install profile from server"
	while 1:
		client_config = server.get_client_config(local_mac)
		install_profile = server.get_install_profile(local_mac)
		if install_profile and client_config:
			print "Received client config and install profile from server"
			break
		time.sleep(1)

	tmpfile = open("/tmp/client_config.xml", "w")
	tmpfile.write(client_config)
	tmpfile.close()
	
	tmpfile = open("/tmp/install_profile.xml", "w")
	tmpfile.write(install_profile)
	tmpfile.close()
	
	#STOP HERE BECAUSE WE ARE FAKING IT
	print "Wrote the temporary xml profiles."
	sys.exit(0)
#	break
#	pass
	
	client_config = GLIClientConfiguration.ClientConfiguration()
	client_config.parse("/tmp/client_config.xml")
	install_profile = GLIInstallProfile.InstallProfile()
	install_profile.parse("/tmp/install_profile.xml")
	cc = GLIClientController.GLIClientController(client_config, install_profile)
	
	#Start the backend threads
	cc.start_pre_install()
	
	#Begin the main engine
	cc.start_install()
	num_steps_completed = 1
	while 1:
		notification = cc.getNotification()
		if notification == None:
			time.sleep(1)
			continue
		ntype = notification.get_type()
		ndata = notification.get_data()
		if ntype == "exception":
			print str(ndata)
			server.update_client_status(local_mac, "Exception: " + str(ndata))
			sys.exit(0)
		elif ntype == "int":
			if ndata == GLIClientController.NEXT_STEP_READY:
				next_step_waiting = False
				next_step = cc.get_next_step_info()
				num_steps = cc.get_num_steps()
				print str(num_steps_completed) + " of " + str(num_steps) + ": " + next_step
				server.update_client_status(local_mac, str(num_steps_completed) + " of " + str(num_steps) + ": " + next_step)
				num_steps_completed += 1
				if cc.has_more_steps():
					cc.next_step()
				continue
			if ndata == GLIClientController.INSTALL_DONE:
				print "Install complete!"
				server.update_client_status(local_mac, "Install completed!")
				sys.exit(0)
