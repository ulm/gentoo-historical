"""
Gentoo Linux Installer

$Id: GLIClientConfiguration.py,v 1.18 2004/10/08 20:55:17 samyron Exp $
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

import string, re, GLIUtility, SimpleXMLParser
from GLIException import *

class ClientConfiguration:

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
		self._network_type = None
		self._network_data = ()
		self._enable_ssh = False
		self._root_passwd = ""
		self._interactive = True
		self._kernel_modules = ()
		self._ftp_proxy = ""
		self._http_proxy = ""
		self._rsync_proxy = ""
		self._verbose = True

		parser = SimpleXMLParser.SimpleXMLParser()

		parser.addHandler('client-configuration/architecture-template', self.set_architecture_template)
		parser.addHandler('client-configuration/profile-uri', self.set_profile_uri)
		parser.addHandler('client-configuration/root-mount-point', self.set_root_mount_point)
		parser.addHandler('client-configuration/log-file', self.set_log_file)
		parser.addHandler('client-configuration/network', self.set_network_type)
		parser.addHandler('client-configuration/dns-servers', self.set_dns_servers)
		parser.addHandler('client-configuration/enable-ssh', self.set_enable_ssh)
		parser.addHandler('client-configuration/root-passwd', self.set_root_passwd)
		parser.addHandler('client-configuration/interactive', self.set_interactive)
		parser.addHandler('client-configuration/kernel-modules', self.set_kernel_modules)
		parser.addHandler('client-configuration/ftp-proxy', self.set_ftp_proxy)
		parser.addHandler('client-configuration/http-proxy', self.set_http_proxy)
		parser.addHandler('client-configuration/rsync-proxy', self.set_rsync_proxy)
		parser.addHandler('client-configuration/verbose', self.set_verbose)

		self._parser = parser

	def parse(self, filename):
		self._parser.parse(filename)

	def get_architecture_template(self):
		return self._architecture_template
	
	def set_architecture_template(self, xml_path, architecture_template, xml_attr):
		self._architecture_template = architecture_template
	
	def get_profile_uri(self):
		return self._profile_uri
	
	def set_profile_uri(self, xml_path, profile_uri, xml_attr):
		if profile_uri != None and not GLIUtility.is_uri(profile_uri):
			raise URIError('fatal', 'set_profile_uri',"The URI specified is not valid!")

		self._profile_uri = profile_uri

	def get_install_steps_completed(self):
		return self._install_steps_completed
	
	def set_install_steps_completed(self, xml_path, install_steps_completed, xml_attr):
		self._install_steps_completed = install_steps_completed

	def add_install_steps_completed(self, xml_path, install_step, xml_attr):
		self._install_steps_completed.append(install_step)

	def get_current_step_percent(self):
		return self._current_step_percent
	
	def set_current_step_percent(self, xml_path, current_step_percent, xml_attr):
		self._current_step_percent = current_step_percent

	def get_current_step_process_desc(self):
		return self._current_step_process_desc
	
	def set_current_step_process_desc(self, xml_path, current_step_process_desc, xml_attr):
		self._current_step_process_desc = current_step_process_desc

	def get_log_file(self):
		return self._log_file
	
	def set_log_file(self, xml_path, log_file, xml_attr):
		self._log_file = log_file

	def get_proc_temp_log(self):
		return self._proc_temp_log
	
	def set_proc_temp_log(self, xml_path, proc_temp_log, xml_attr):
		self._proc_temp_log = proc_temp_log

	def get_root_mount_point(self):
		return self._root_mount_point
	
	def set_root_mount_point(self, xml_path, root_mount_point, xml_attr):
		self._root_mount_point = root_mount_point

	shared_client_configuration = classmethod(shared_client_configuration)

	def set_network_type(self, xml_path, network_type, xml_attr=None):

		interface = ip = broadcast = netmask = gateway = None

		if type(xml_attr) == tuple:
			interface = xml_attr[0]
			ip = xml_attr[1]
			broadcast = xml_attr[2]
			netmask = xml_attr[3]
			gateway = xml_attr[4]
		else:
			for key in xml_attr.keys():
				if key == 'interface':
					interface = str(xml_attr.get('interface'))
				elif key == 'ip':
					ip = str(xml_attr.get('ip'))
				elif key == 'broadcast':
					broadcast = str(xml_attr.get('broadcast'))
				elif key == 'netmask':
					netmask = str(xml_attr.get('netmask'))
				elif key == 'gateway':
					gateway = str(xml_attr.get('gateway'))

		if not GLIUtility.is_eth_device(interface):
			raise InterfaceError('fatal', 'set_network_type', "Interface " + interface + " must be a valid device!")

		network_data = (interface, ip, broadcast, netmask, gateway)

		if network_type == 'static' and xml_attr == None:
			raise NoInterfaceError('fatal','set_network_type',"No interface information specified!")

		self.set_network_data(network_data)
		self._network_type = network_type

	def get_network_type(self):
		return self._network_type

	def get_network_data(self):
		return self._network_data

	def set_network_data(self, network_info):
		interface = network_info[0]
		ip = network_info[1]
		broadcast = network_info[2]
		netmask = network_info[3]
		gateway = network_info[4]

		if not GLIUtility.is_eth_device(interface):
			raise InterfaceError('fatal','set_network_data', "Interface " + interface + " must be a valid device!")
	
		if ip != None:
			if not GLIUtility.is_ip(ip):
				raise IPAddressError('fatal','set_network_data', 'The specified IP ' + ip + ' is not a valid IP Address!')

		if gateway != None:
			if not GLIUtility.is_ip(gateway):
				raise IPAddressError('fatal', 'set_network_data', "The gateway IP provided is not a valid gateway!!")

		if broadcast != None:
			if not GLIUtility.is_ip(broadcast):
				raise IPAddressError('fatal','set_network_data', 'The specified broadcast is not a valid IP Address!')
		else:
			# Guess the broadcast... just in case (probably need the gateway..)
			pass

		if netmask != None:
			if not GLIUtility.is_ip(netmask):
				raise IPAddressError('fatal','set_network_data', 'The specified netmask is not a valid IP Address!')
		else:
			# Guess the netmask... just in case (probably need the gateway..)
			pass

		self._network_data = network_info

	def set_dns_servers(self, xml_path, nameservers, xml_attr):
		if type(nameservers) == str:
			nameservers = nameservers.split(" ")
			dns = []
			for server in nameservers:
				dns.append(server)

		self._dns_servers = tuple(dns)

	def get_dns_servers(self):
		return self._dns_servers

	def set_enable_ssh(self, xml_path, enable_ssh, xml_attr):
		if type(enable_ssh) == str:
			enable_ssh = GLIUtility.strtobool(enable_ssh)
		self._enable_ssh = enable_ssh

	def get_enable_ssh(self):
		return self._enable_ssh

	def set_root_passwd(self, xml_path, passwd, xml_attr):
		self._root_passwd = passwd

	def get_root_passwd(self):
		return self._root_passwd

	def set_interactive(self, xml_path, interactive, xml_attr):
		if type(interactive) != bool:
			interactive = GLIUtility.strtobool(interactive)
		self._interactive = interactive

	def get_interactive(self):
		return self._interactive

	def set_kernel_modules(self, xml_path, modules, xml_attr):
		self._kernel_modules = tuple(string.split(modules))

	def get_kernel_modules(self):
		return self._kernel_modules

	def set_ftp_proxy(self, xml_path, proxy, xml_attr):
		self._ftp_proxy = proxy

	def get_ftp_proxy(self):
		return self._ftp_proxy

	def set_http_proxy(self, xml_path, proxy, xml_attr):
		self._http_proxy = proxy

	def get_http_proxy(self):
		return self._http_proxy

	def set_rsync_proxy(self, xml_path, proxy, xml_attr):
		self._rsync_proxy = proxy

	def get_rsync_proxy(self):
		return self._rsync_proxy

	def set_verbose(self, xml_path, verbose, xml_attr):
		if type(verbose) == str:
			verbose = GLIUtility.strtobool(verbose)

		self._verbose = verbose

	def get_verbose(self):
		return self._verbose

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
					'verbose': self.get_verbose,
				}
		data = "<client-configuration>"

		for key in fntable.keys():
			data += "<%s>%s</%s>" % (key, fntable[key](), key)

		# Special Cases
		net_type = self.get_network_type()
		if net_type == "static":
			net_info = self.get_network_data()
			data +=  "<network interface=\"%s\" ip=\"%s\" broadcast=\"%s\" netmask=\"%s\" gateway=\"%s\">%s</network>" % (net_info[0], net_info[1], net_info[2], net_info[3], net_info[4], net_type)
			data += "<dns-servers>%s</dns-servers>" % string.join(self.get_dns_servers())
		elif net_type == "dhcp":
			net_info = self.get_network_data()
			interface = None

			if len(net_info) > 0:
				interface = net_info[0]

			if interface != None:
				data += "<network interface=\"%s\">dhcp</network>" % interface
			else:
				data += "<network>dhcp</network>"
		else:
			data += "<network>%s</network>" % net_type
	
		data += "<kernel-modules>%s</kernel-modules>" % string.join(self.get_kernel_modules())

		data += "</client-configuration>"

		import xml.dom.minidom
		dom = xml.dom.minidom.parseString(data)
                return dom.toprettyxml()

