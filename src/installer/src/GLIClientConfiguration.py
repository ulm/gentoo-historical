"""
Gentoo Linux Installer

$Id: GLIClientConfiguration.py,v 1.12 2004/08/25 19:38:10 samyron Exp $
Copyright 2004 Gentoo Technologies Inc.

The GLIClientConfiguration module contains the ClientConfiguration class
which is a singleton class that represents configuration data that is
used by the installer client during installation. Data that is part of
the actual install is contained in GLIInstallProfile.

Usage:

	from GLIClientConfiguration import ClientConfiguration

	conf = ClientConfiguration.shared_client_configuration()

	conf.root_mount_point('/mnt/gentoo/')
	conf.architecture_template('x86')

"""

import xml.sax, string, GLIUtility
from GLIException import *

class ClientConfiguration(xml.sax.ContentHandler):

	SHARED_CLIENT_CONFIGURATION = None

	def shared_client_configuration(cls):
		if GLIClientConfiguration.SHARED_CLIENT_CONFIGURATION == None:
			GLIClientConfiguration.SHARED_CLIENT_CONFIGURATION = cls()

		return GLIClientConfiguration.SHARED_CLIENT_CONFIGURATION

	def __init__(self):
		self._architecture_template = None
		self._profile_uri = ""
	
		# This contains a list of all the install steps completed
		# It is used for dependency checking
		self._install_steps_completed = []
	
		# This allows InstallTemplate to communicate back to the controller
		# The controller can poll this information to inform the user
		# This gives a percentange of the step that is completed
		self._current_step_percent = 0
		# This is a string describing what the step is currently doing
		self._current_step_process_desc = ""

		# This is the full path to the logfile
		self._log_file = "/var/log/installer.log"
		
		# Current process temporary log (for parsing)
		self._proc_temp_log = "/tmp/proc.tmp.log"

		# This is the root mount point
		self._root_mount_point = "/mnt/gentoo"

		# Initialize some variables so we never reference a variable that never exists.
		self._dns_servers = ()
		self._network_type = ""
		self._network_data = ()
		self._default_gateway = ()
		self._enable_ssh = False
		self._root_passwd = ""
		self._interactive = True
		self._kernel_modules = ()
		self._ftp_proxy = ""
		self._http_proxy = ""
		self._rsync_proxy = ""

		# Internal SAX state info
		self._xml_elements = [];
		self._xml_current_data = ""
		self._xml_current_attr = None

	def get_architecture_template(self):
		return self._architecture_template
	
	def set_architecture_template(self, architecture_template):
		self._architecture_template = architecture_template
	
	def get_profile_uri(self):
		return self._profile_uri
	
	def set_profile_uri(self, profile_uri):
		if profile_uri != None and not GLIUtility.is_uri(profile_uri):
			raise URIError('fatal', 'set_profile_uri',"The URI specified is not valid!")

		self._profile_uri = profile_uri

	def get_install_steps_completed(self):
		return self._install_steps_completed
	
	def set_install_steps_completed(self, install_steps_completed):
		self._install_steps_completed = install_steps_completed

	def add_install_steps_completed(self, install_step):
		self._install_steps_completed.append(install_step)

	def get_current_step_percent(self):
		return self._current_step_percent
	
	def set_current_step_percent(self, current_step_percent):
		self._current_step_percent = current_step_percent

	def get_current_step_process_desc(self):
		return self._current_step_process_desc
	
	def set_current_step_process_desc(self, current_step_process_desc):
		self._current_step_process_desc = current_step_process_desc

	def get_log_file(self):
		return self._log_file
	
	def set_log_file(self, log_file):
		self._log_file = log_file

	def get_proc_temp_log(self):
		return self._proc_temp_log
	
	def set_proc_temp_log(self, proc_temp_log):
		self._proc_temp_log = proc_temp_log

	def get_root_mount_point(self):
		return self._root_mount_point
	
	def set_root_mount_point(self, root_mount_point):
		self._root_mount_point = root_mount_point

	shared_client_configuration = classmethod(shared_client_configuration)

	def set_network_type(self, network_type, attr=None):
		if attr == None:
			attr = self._xml_current_attr

		if network_type == 'static' and attr != None:
			ip = broadcast = netmask = interface = ""

			if type(attr) != tuple:
				for attrName in attr.keys():
					if attrName == 'ip':
						ip = str(attr.get(attrName))
					elif attrName == 'broadcast':
						broadcast = str(attr.get(attrName))
					elif attrName == 'netmask':
						netmask = str(attr.get(attrName))
					elif attrName == 'interface':
						interface = str(attr.get(attrName))

				attr = (interface, ip, broadcast, netmask)

			self.set_network_data(attr)

		elif network_type == 'static':
			raise NoInterfaceError('fatal','set_network_type',"No interface information specified!")

		elif network_type == "dhcp" and attr != None:
			if type(attr) != tuple:
				if 'interface' in attr.getNames():
					interface = str(attr.get('interface'))
					if not GLIUtility.is_eth_device(interface):
						raise InterfaceError('fatal', 'set_network_type', "Interface " + interface + " must be a valid device!")
					else:
						self._network_data = (interface, None, None, None)
			else:
				self._network_data = attr


		self._network_type = network_type

	def get_network_type(self):
		return self._network_type

	def get_network_info(self):
		return self._network_data

	def set_network_data(self, network_info):
		interface = network_info[0]
		ip = network_info[1]
		broadcast = network_info[2]
		netmask = network_info[3]

		if not GLIUtility.is_eth_device(interface):
			raise InterfaceError('fatal','set_network_data', "Interface " + interface + " must be a valid device!")
	
		if ip != None:
			if not GLIUtility.is_ip(ip):
				raise IPAddressError('fatal','set_network_data', 'The specified IP is not a valid IP Address!')

		if broadcast != None:
			if not GLIUtility.is_ip(broadcast):
				raise IPAddressError('fatal','set_network_data', 'The specified broadcast is not a valid IP Address!')

		if netmask != None:
			if not GLIUtility.is_ip(netmask):
				raise IPAddressError('fatal','set_network_data', 'The specified netmask is not a valid IP Address!')

		self._network_data = network_info

	def set_default_gateway(self, gateway, interface=""):
		"""
		This sets the default gateway to a tuple of the format:
		(<interface>, <gateway ip address>)
		"""

		if interface == "":
			if self._xml_current_attr != None and self._xml_current_attr.has_key('interface'):
				interface = self._xml_current_attr.getValue('interface')

		if interface[0:3] not in ('eth', 'ppp', 'wla'):
			raise DefaultGatewayError('fatal','set_default_gateway', "Invalid interface!")

		if not GLIUtility.is_ip(gateway):
			raise IPAddressError('fatal', 'set_default_gateway', "The IP Provided is not valid!")

		self._default_gateway = (interface, gateway)

	def get_default_gateway(self):
		return self._default_gateway

	def set_dns_servers(self, nameservers):
		if type(nameservers) == str:
			nameservers = nameservers.split(" ")
			dns = []
			for server in nameservers:
				dns.append(server)

		self._dns_servers = tuple(dns)

	def get_dns_servers(self):
		return self._dns_servers

	def set_enable_ssh(self, enable_ssh):
		if type(enable_ssh) == str:
			enable_ssh = GLIUtility.strtobool(enable_ssh)
		self._enable_ssh = enable_ssh

	def get_enable_ssh(self):
		return self._enable_ssh

	def set_root_passwd(self,passwd):
		self._root_passwd = passwd

	def get_root_passwd(self):
		return self._root_passwd

	def set_interactive(self, interactive):
		if type(interactive) != bool:
			interactive = GLIUtility.strtobool(interactive)
		self._interactive = interactive

	def get_interactive(self):
		return self._interactive

	def set_kernel_modules(self, modules):
		self._kernel_modules = tuple(string.split(modules))

	def get_kernel_modules(self):
		return self._kernel_modules

	def set_ftp_proxy(self, proxy):
		self._ftp_proxy = proxy

	def get_ftp_proxy(self):
		return self._ftp_proxy

	def set_http_proxy(self, proxy):
		self._http_proxy = proxy

	def get_http_proxy(self):
		return self._http_proxy

	def set_rsync_proxy(self, proxy):
		self._rsync_proxy = proxy

	def get_rsync_proxy(self):
		return self._rsync_proxy

	def startElement(self, name, attr): 
		"""
		XML SAX start element handler

		Called when the SAX parser encounters an XML openning element.
		"""

		self._xml_elements.append(name)
		self._xml_current_attr = attr
		self._xml_current_data = ""

	def endElement(self, name):
		fntable = 	{ 	'client-configuration/architecture-template': self.set_architecture_template,
					'client-configuration/profile-uri': self.set_profile_uri,
					'client-configuration/root-mount-point': self.set_root_mount_point,
					'client-configuration/log-file': self.set_log_file,
					'client-configuration/network-setup': self.set_network_type,
					'client-configuration/dns-servers': self.set_dns_servers,
					'client-configuration/default-gateway': self.set_default_gateway,
					'client-configuration/enable-ssh': self.set_enable_ssh,
					'client-configuration/root-passwd': self.set_root_passwd,
					'client-configuration/interactive': self.set_interactive,
					'client-configuration/kernel-modules': self.set_kernel_modules,
					'client-configuration/ftp-proxy': self.set_ftp_proxy,
					'client-configuration/http-proxy': self.set_http_proxy,
					'client-configuration/rsync-proxy': self.set_rsync_proxy,
				}

		path = self._xml_element_path()
		
		if self._xml_current_data != '':
			if path in fntable.keys():
				fntable[path](self._xml_current_data)
				
		# Keep the XML state
		self._xml_current_data = ""
		self._xml_current_attr = None  
		self._xml_elements.pop()

	def characters(self, data):
		"""
		XML SAX character data handler
        
		Called when the SAX parser encounters character data.
		"""
                                        
		# This converts data to a string instead of being Unicode
		# Maybe we should use Unicode strings instead of normal strings?
		self._xml_current_data += string.strip(str(data))

	def _xml_element_path(self):
		"""
		Return path to current XML node
		"""
                
		return string.join(self._xml_elements, '/')

	def parse(self, path):
		"""
		Parse serialized configuration file.
		"""                     
		xml.sax.parse(path, self)

	def serialize(self):
		fntable =	{	'architecture-template': self.get_architecture_template,
					'mount-point': self.get_root_mount_point,
					'profile-uri': self.get_profile_uri,
					'log-file': self.get_log_file,
					'enable-ssh': self.get_enable_ssh,
					'root-passwd': self.get_root_passwd,
					'interactive': self.get_interactive,
					'ftp-proxy': self.get_ftp_proxy,
					'http-proxy': self.get_http_proxy,
					'rsync-proxy': self.get_rsync_proxy,
				}
		data = "<client-configuration>"

		for key in fntable.keys():
			data += "<%s>%s</%s>" % (key, fntable[key](), key)

		# Special Cases
		net_type = self.get_network_type()
		if net_type == "static":
			net_info = self.get_network_info()
			data +=  "<network-setup interface=\"%s\" ip=\"%s\" broadcast=\"%s\" netmask=\"%s\">%s</network-setup>" % (net_info[0], net_info[1], net_info[2], net_info[3], net_type)
			gateway = self.get_default_gateway()
			data += "<default-gateway interface=\"%s\">%s</default-gateway>" % (gateway[0], gateway[1])
			data += "<dns-servers>%s</dns-servers>" % string.join(self.get_dns_servers())
		elif net_type == "dhcp":
			net_info = self.get_network_info()
			interface = None

			if len(net_info) > 0:
				interface = net_info[0]

			if interface != None:
				data += "<network-setup interface=\"%s\">dhcp</network-setup>" % interface
			else:
				data += "<network-setup>dhcp</network-setup>"
		else:
			data += "<network-setup>%s</network-setup>" % net_type
	
		data += "<kernel-modules>%s</kernel-modules>" % string.join(self.get_kernel_modules())

		data += "</client-configuration>"

		import xml.dom.minidom
		dom = xml.dom.minidom.parseString(data)
                return dom.toprettyxml()

