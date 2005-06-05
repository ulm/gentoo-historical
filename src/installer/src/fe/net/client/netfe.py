#!/usr/bin/python
##
#The sole point of this script is to kick off a GLIInstall. This script requires the 'netbe.py' configured 
#and setup on the local net in order to run. Also the network should up and running when this script is 
#invoked. No other dependancies are required for this script.
#
#Script steps:
#	1. Assume the network is up and running
#	2. Send a UDP request to the broadcast address.
#	3. Server will respond.
#	4. The client will connect to the server using XMLRPC and request a GLIClientConfig and a InstallProfile
#	5. Next the client will start the install, logging all events to the server
#
#Note: If the install server does not have a clientconf or installprofile we will allow the user to generate 
#one and upload it.


#Begin Imports
import sys, time, socket
sys.path.append("../../..")
import GLIException
import GLIInstallProfile
import GLIClientConfiguration
import GLIClientController
import GLIUtility
import xmlrpclib
import dialog
import GLIGenDialog
#End Imports

#Dialog constants used in the main line code. All objects should declare these internally.
DLG_OK = 0
DLG_YES = 0
DLG_CANCEL = 1
DLG_NO = 1
DLG_ESC = 2
DLG_ERROR = 3
DLG_EXTRA = 4
DLG_HELP = 5

##
#Class that defines the proper methods to call to have a user generate the Client Configuration
#for a network based install. This is used so that the dialogfe and this one can share some common
#code.
class CFDialog(GLIGenDialog.GLIGenCF):
	##
	#Calls the proper  chain of Dialog functions to make a ClientConfig.
	def __init__(self):
		GLIGenCF.__init__(self) #Make sure to call parent class for good initialization.
		if self._d.yesno("We are unable to find a Client Configuration for you. Would you like to generate one instead?") == self._DLG_YES:
			self._set_arch_template()
			self._set_logfile()
			self._set_root_mount_point()
			self._set_client_networking()
			self._set_livecd_password()
			self._set_enable_ssh()
			self._set_client_kernel_modules()
		else:
			raise GLIException('NetFeError', 'fatal', 'UserGen.__init__', "Unable to find or generate a CLient Configuration.")

##
#Class that defines the proper methods to call to have a user generate the Install Profile for a network 
#based install. This is used so that the dialogfe and this one can share some common
#code.
class IPDialog(GLIGenDialog.GLIGenIP):
	##
	#Since the steps are rather hard to break apart and are the same nomatter the install, we just
	#call the dialog library after wrapping it with a question.
	def __init__(self):
		if self._d.yesno("We are unable to find an Install Profile for you. Would you like to generate one instead?") == self._DLG_YES:
			GLIGenIP.__init__(self)
		else:
			raise GLIException('NetFeError', 'fatal', 'UserGen.__init__', "Unable to find or generate a Install Profile.")

##
#Sends a UDP packet  to a specified address. Any response that is sent is returned.
#@param message The data that shall be sent in the UDP packet.
#@param bw_addr The broadcast address to send the packet to. This could technically
#	be any ip address, but it will not work properly if it isn't. Also unusual errors are 
#	generally the result of a bad broadcast address.
#@param port The port number to send the message over.
#@return Returns the response from the network, the ip address of the response and 
#	the port of the response.
def udp_broadcast(message, bw_addr, port):
	#Setup the socket for broadcast.
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('', 0))
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	s.settimeout(15)
	
	retry_max = 3
	count = 0
	response = ""
	
	while 1:
		s.sendto(message, (bw_addr, port))
		response, fromaddr = s.recvfrom(1024)
		count = count + 1
		if response:
			break
		if count >= retry_max:
			raise GLIException("NetFeError", 'fatal', 'udp_broadcast',"Was unable to find a network broadcast server.")
		time.sleep(2)
	return response, str(fromaddr[0]), str(fromaddr[1])

##
#This function discovers the mac address and ip address of the local client.
#Note: This should be deprecated soon. It relies on the faulty is_eth_device.
#@return mac address and ip address of client
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

##
#This attempts to find a netbe server via UDP broadcasts
#@param port that the rpc server should be on, the UDP
#	server should have a negative one port offset.
#@return the rpc/udp server's ip address
def find_server(main_port):
	discovery_port = main_port - 1
	device = None
	device_name = 'eth'
	for num in range(5):
		if GLIUtility.is_eth_device(device_name + str(num)):
			device = GLIUtility.get_eth_info(num)
			break
		else:
			raise GLIException("NetFeError", 'fatal', 'setup_network',"Was unable to find a network inferface.")

	response, server_ip, server_port = udp_broadcast("GLIAutoInstall", device[3], discovery_port)
	return server_ip

##
#Asks for the uri of the rpc server for installation.
#@param A Dialog object
#@return Uri  of the server
def ask_server(dialog):
	code, uri = dialog.inputbox("We were unable to autodiscover the server. Plaese enter the uri of the server:")
	if code != DLG_OK: 
		raise GLIException("Unable to connect to a server.")
	elif not GLIUtility.is_uri(uri):
		d.msgbox("You must pass a valid uri.")
	else:
		return uri

#Start of the command line invoked program.
if __name__ == '__main__':
	#Default port
	main_port = 12345
	
	d = dialog.Dialog()
	d.setBackgroundTitle("Gentoo Linux Installer")
	d.infobox("Welcome to The Gentoo Linux Installer. This is a TESTING release. If your system dies a horrible, horrible death, don't come crying to us (okay, you can cry to klieber).", height=10, width=50, title="Welcome")
	time.sleep(1) #Sleep so the user can see the screen.
	
	#First the client's mac and ip address
	local_mac, local_ip = find_macip()
	
	d.infobox("We are now attempting to autodiscover the install server. If this fails you will be asked for the server's uri.")
	time.sleep(1)
	try:
		server_ip = find_server(main_port)
		if server_ip == local_ip:
			server_ip = '127.0.0.1'
		server_uri = "http://" + server_ip + ":" + str(main_port)
	except:
		server_uri = ask_server(d)
	
	#Next setup the RPC Client
	server = xmlrpclib.ServerProxy(server_uri)
		
	#If we cant find the configuration files, start the dialog fe and generate them.
	d.infobox("We are now going to get the Client Configuration from the server.")
	client_config = server.get_client_config(local_mac)
	if not GLIUtility.is_realstring(client_config):
		clco = CFDialog()
		client_config = clco.serialize()
		server.set_client_config(local_mac, client_config)
	
	#Same with the install profile
	d.infobox("We are now going to get the Install Profile from the server.")
	install_profile = server.get_install_profile(local_mac)
	if not GLIUtility.is_realstring(install_profile):
		ip = IPDialog()
		install_profile = ip.serialize()
		server.set_install_profile(local_mac, install_profile)
	
	#Write out the client_config and install_profile
	r_file = open("/tmp/cli_conf.xml","w")
	r_file.write(client_config)
	r_file.close()
	
	r_file = open("/tmp/ins_prof.xml","w")
	r_file.write(install_profile)
	r_file.close()
	
	#Instanciate the GLI engine pass it the client config and install profile objects
	client_conf = GLIClientConfiguration.ClientConfiguration()
	client_conf.parse("/tmp/gli.conf")
	client_conf.set_interactive(None, True, None)
	install_prof = GLIInstallProfile.InstallProfile()
	install_prof.parse("/tmp/ins_prof.xml")
	cc = GLIClientController.GLIClientController(client_conf,install_prof)
	
	#Start the backend threads
	cc.start_pre_install()
	
	#Begin the main engine
	cc.start_install()
	d.gauge_start("Installation Started!", title="Installation progress")
	num_steps_completed = 1
	while 1:
		notification = cc.getNotification()
		if notification == None:
			time.sleep(1)
			continue
		type_r = notification.get_type()
		data_r = notification.get_data()
		if type_r == "exception":
			server.log_event(local_ip, "Exception: " + data_r)
			print data_r
		elif type_r == "int":
			if data_r == GLIClientController.NEXT_STEP_READY:
				next_step_waiting = False
				next_step = cc.get_next_step_info()
				num_steps = cc.get_num_steps()
				i = (num_steps_completed*100)/num_steps
				d.gauge_update(i, "On step %d of %d. Current step: %s" % (num_steps_completed, num_steps, next_step), update_text=1)
				server.log_event(local_ip, "On step " + num_steps_completed + " of " + num_steps + ". Current step: " + next_step)
				num_steps_completed += 1
				if cc.has_more_steps():
					cc.next_step()
				continue
			if data_r == GLIClientController.INSTALL_DONE:
				server.log_event(local_ip, "Install completed!")
				d.gauge_update(100, "Install completed!", update_text=1)
				d.gauge_stop()
				print "Install done!"
				sys.exit(0)
