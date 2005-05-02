#!/usr/bin/python
"""
The sole point of this script is to kick off a GLIInstall. This script requires the 'netbe.py' configured and setup on the local net in order to run. No other dependancies are required for this script.
Script steps:
	1. Bring up network with dhcp or use udp broadcast to grab the client config file.
	2. Send a UDP request to the broadcast address.
	3. The server will check the ip making the request and sent it the location of the server
	4. The client will connect to the server using XMLRPC and request a GLIClientConfig and a InstallProfile
	5. Next the client will start the install, logging all events to the server
"""
import sys, time, socket
sys.path.append("../..")
import GLIException
import GLIInstallProfile
import GLIClientConfiguration
import GLIClientController
import GLIUtility

def udp_broadcast(message, bw_addr, port):
	#Setup the socket for broadcast.
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('', 0))
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	retry_max = 10
	count = 0
	response = ""
	
	while 1:
		s.sendto(message, (bw_addr, port))
		response, fromaddr = s.recvfrom(1024)
		count = count + 1
		if response:
			break
		if count >= retry_max:
			raise GLIException("NoBroadcastServer", 'fatal', 'udp_broadcast',"Was unable to find a network broadcast server.")
		time.sleep(2)
	return response, str(fromaddr[0]), str(fromaddr[1])
	
def setup_network(main_port):
	discovery_port = main_port - 1
	device = None
	device_name = ""
	for num in range(5):
		device = GLIUtility.get_eth_info(num)
		if device:
			device_name = 'eth' + str(num) 
			break
		else:
			raise GLIException("NoInterfaceError", 'fatal', 'setup_network',"Was unable to find a network inferface.")

	#First try to come up as a dhcp client. This is the preferred way of starting the network.
	if device:
		status = GLIUtility.spawn("dhcpcd -n " + device_name, quiet=True)
	else:
		status = GLIUtility.spawn("dhcpcd -n", quiet=True)

	#If dhcp couldn't start we will try to use UDP broadcast to the server. Then we will pull the
	#config file and setup whatever networking is defined for us.
	if not GLIUtility.exitsuccess(status):
		GLIUtility.set_ip(device_name, '0.0.0.0', '255.255.255.255', '0.0.0.0')
		
		#Grab the config from the server. Pass it the MAC address so the server can identify you.
		#as well as the broadcast address and port you want to check on.
		response, server_ip, port = udp_broadcast("GLI CC " + device[0], device[3], discovery_port)
		if response == "GLI CC not found!":
			raise GLIException("GLIMissingConfig","The server does not have a GLICLientConfiguration for you. Check with the server admin.")
		else:
			#Write the Client Config to a temp file, so it can be read in and parsed
			file = open("/tmp/gli.conf","w")
			file.write(response)
			file.close()
		
			#Instanciate a ClientController and tell it to setup the network
			client_config = GLIClientConfiguration.GLIClientConfiguration()
			client_config.parse("/tmp/gli.conf")
			cc = GLIClientController.GLIClientController(client_config)
			cc.configure_networking()
	response, server_ip, server_port = udp_broadcast("PING", device[3], discovery_port)
	return server_ip
		
			
if __name__ == '__main__':
	main_port = 12345
	
	#First things first check for network existance and setup the network; the server ip will be returned
	server_ip = setup_network(main_port)
	local_ip = socket.gethostbyname(socket.gethostname())
	
	#Next setup the RPC Client
	server = ServerProxy("http://" + server_ip + ":" + main_port)
	
	#Grab the Client Configuration and Install Profile
	client_config = ""
	install_profile = ""
	try:
		client_config = server.get_client_config(local_ip)
		install_profile = server.get_install_profile(local_ip)
	except Error, v:
		raise GLIException("GLIMissingConfig", v )
	
	#Write out the client_config and install_profile
	file = open("/tmp/gli.conf","w")
	file.write(client_config)
	file.close()
	
	file = open("/tmp/ins_prof.xml","w")
	file.write(install_profile)
	file.close()
	
	#Instanciate the GLI engine
	client_conf = GLIClientConfiguration.GLIClientConfiguration()
	client_conf.parse("/tmp/gli.conf")
	client_conf.set_interactive(None, True, None)
	install_prof = GLIInstallProfile.GLIInstallProfile()
	install_prof.parse("/tmp/ins_prof.xml")
	cc = GLIClientController.GLIClientController(client_conf,install_prof)
	
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
		type = notification.get_type()
		data = notification.get_data()
		if type == "exception":
			server.log_event(local_ip, "Exception: " + data)
		elif type == "int":
			if data == GLIClientController.NEXT_STEP_READY:
				next_step_waiting = False
				next_step = cc.get_next_step_info()
				num_steps = cc.get_num_steps()
				server.log_event(local_ip, "On step " + num_steps_completed + " of " + num_steps + ". Current step: " + next_step)
				num_steps_completed += 1
				if cc.has_more_steps():
					cc.next_step()
				continue
			if data == GLIClientController.INSTALL_DONE:
				server.log_event(local_ip, "Install completed!")
				print "Install done!"
				sys.exit(0)