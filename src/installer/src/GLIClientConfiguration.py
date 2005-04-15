"""
Gentoo Linux Installer

$Id: GLIClientConfiguration.py,v 1.23 2005/04/15 06:26:43 codeman Exp $
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

	##
	# FIXME: what does this do?
	# @param cls Parameter description
	def shared_client_configuration(cls):
		if GLIClientConfiguration.SHARED_CLIENT_CONFIGURATION == None:
			GLIClientConfiguration.SHARED_CLIENT_CONFIGURATION = cls()

		return GLIClientConfiguration.SHARED_CLIENT_CONFIGURATION

	##
	# Initializes the ClientConfiguration.
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
		
		# This is the root mount point
		self._root_mount_point = "/mnt/gentoo"

		# Initialize some variables so we never reference a variable that never exists.
		self._dns_servers = ()
		self._network_type = None
		self._network_data = ()
		self._enable_ssh = True
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

	##
	# Parses the given filename populating the client_configuration.
	# @param filename the file to be parsed.  This should be a URI actually.
	def parse(self, filename):
		self._parser.parse(filename)

	##
	# Returns the architecture_template
	def get_architecture_template(self):
		return self._architecture_template
	
	##
	# Sets the architecture_template
	# @param xml_path not used here.
	# @param architecture_template the architecture to be installed
	# @param xml_attr not used here.
	def set_architecture_template(self, xml_path, architecture_template, xml_attr):
		self._architecture_template = architecture_template
	
	##
	# Returns the profile_uri
	def get_profile_uri(self):
		return self._profile_uri
	
	##
	# Sets the profile_uri for use in non-interactive installs
	# @param xml_path not used here.
	# @param profile_uri location of the profile
	# @param xml_attr not used here.
	def set_profile_uri(self, xml_path, profile_uri, xml_attr):
		if profile_uri != None and not GLIUtility.is_uri(profile_uri):
			raise GLIException("URIError", 'fatal', 'set_profile_uri',"The URI specified is not valid!")

		self._profile_uri = profile_uri

	##
	# Returns the number of steps completed.  This is not used because the CC does it now.
	def get_install_steps_completed(self):
		return self._install_steps_completed
	
	##
	# Sets the install_steps_completed to some new value? again not used.  CC does this.
	# @param xml_path not used here.
	# @param install_steps_completed some new install_steps_completed value
	# @param xml_attr not used here.
	def set_install_steps_completed(self, xml_path, install_steps_completed, xml_attr):
		self._install_steps_completed = install_steps_completed

	##
	# Adds to the list of completed steps a new step.  again not used. CC does this.
	# @param xml_path not used here.
	# @param install_step the step that has been completed
	# @param xml_attr not used here.
	def add_install_steps_completed(self, xml_path, install_step, xml_attr):
		self._install_steps_completed.append(install_step)

	##
	# Returns the current step percent?  totally unused and probably not functional.
	# FIXME: get rid of this!
	def get_current_step_percent(self):
		return self._current_step_percent
	
	##
	# Sets the current step percent?  totally unused and probably not functional.
	# FIXME: get rid of this!
	# @param xml_path not used here.
	# @param current_step_percent set a new percentage
	# @param xml_attr not used here.
	def set_current_step_percent(self, xml_path, current_step_percent, xml_attr):
		self._current_step_percent = current_step_percent

	##
	# Returns the description of the current step.  unused i think.
	def get_current_step_process_desc(self):
		return self._current_step_process_desc
	
	##
	# Sets the description of the current step.  unused.
	# @param xml_path not used here.
	# @param current_step_process_desc a description
	# @param xml_attr not used here.
	def set_current_step_process_desc(self, xml_path, current_step_process_desc, xml_attr):
		self._current_step_process_desc = current_step_process_desc

	##
	# Returns the log filename
	def get_log_file(self):
		return self._log_file
	
	##
	# Sets the log filename.
	# @param xml_path not used here.
	# @param log_file the name of the logfile for the CC to use.
	# @param xml_attr not used here.
	def set_log_file(self, xml_path, log_file, xml_attr):
		self._log_file = log_file

	##
	# Returns the root_mount_point
	def get_root_mount_point(self):
		return self._root_mount_point
	
	##
	# Sets the root_mount_point for the new system to be installed to
	# @param xml_path not used here.
	# @param root_mount_point new location for the root mount point
	# @param xml_attr not used here.
	def set_root_mount_point(self, xml_path, root_mount_point, xml_attr):
		self._root_mount_point = root_mount_point

	###############################################################
	#####################WHAT IS THIS DOING HERE????###############
	shared_client_configuration = classmethod(shared_client_configuration)
	###############################################################

	##
	# Sets the network configuration info for the livecd environment
	# @param xml_path not used here.
	# @param network_type the network type, either static or dhcp
	# @param xml_attr=None a tuple or set of attr of interface, ip, broadcast, netmask, and gateway.
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
			raise GLIException("InterfaceError", 'fatal', 'set_network_type', "Interface " + interface + " must be a valid device!")

		network_data = (interface, ip, broadcast, netmask, gateway)

		if network_type == 'static' and xml_attr == None:
			raise GLIException("NoInterfaceError", 'fatal','set_network_type',"No interface information specified!")

		self.set_network_data(network_data)
		self._network_type = network_type

	##
	# Returns the network type
	def get_network_type(self):
		return self._network_type

	##
	# Returns the network data (ip's and such)
	def get_network_data(self):
		return self._network_data

	##
	# Sets the network data using a dictionary.  Called from set_network_type.
	# @param network_info tuple with livecd network info.
	def set_network_data(self, network_info):
		interface = network_info[0]
		ip = network_info[1]
		broadcast = network_info[2]
		netmask = network_info[3]
		gateway = network_info[4]

		if not GLIUtility.is_eth_device(interface):
			raise GLIException("InterfaceError", 'fatal','set_network_data', "Interface " + interface + " must be a valid device!")
	
		if ip != None:
			if not GLIUtility.is_ip(ip):
				raise GLIException("IPAddressError", 'fatal','set_network_data', 'The specified IP ' + ip + ' is not a valid IP Address!')

		if gateway != None:
			if not GLIUtility.is_ip(gateway):
				raise GLIException("IPAddressError", 'fatal', 'set_network_data', "The gateway IP provided is not a valid gateway!!")

		if broadcast != None:
			if not GLIUtility.is_ip(broadcast):
				raise GLIException("IPAddressError", 'fatal','set_network_data', 'The specified broadcast is not a valid IP Address!')
		else:
			# Guess the broadcast... just in case (probably need the gateway..)
			pass

		if netmask != None:
			if not GLIUtility.is_ip(netmask):
				raise GLIException("IPAddressError", 'fatal','set_network_data', 'The specified netmask is not a valid IP Address!')
		else:
			# Guess the netmask... just in case (probably need the gateway..)
			pass

		self._network_data = network_info

	##
	# Sets the dns servers
	# @param xml_path not used here.
	# @param nameservers space-separated list of nameservers
	# @param xml_attr not used here.
	def set_dns_servers(self, xml_path, nameservers, xml_attr):
		if type(nameservers) == str:
			nameservers = nameservers.split(" ")
			dns = []
			for server in nameservers:
				dns.append(server)

		self._dns_servers = tuple(dns)

	##
	# Returns the list of dns servers
	# @param self Parameter description
	def get_dns_servers(self):
		return self._dns_servers

	##
	# Choosed whether or not to enable SSH.
	# @param xml_path not used here.
	# @param enable_ssh a True/False bool value here or a string
	# @param xml_attr not used here.
	def set_enable_ssh(self, xml_path, enable_ssh, xml_attr):
		if type(enable_ssh) == str:
			enable_ssh = GLIUtility.strtobool(enable_ssh)
		self._enable_ssh = enable_ssh

	##
	# Returns the choice of whether or not to enable SSH (True/False)
	# @param self Parameter description
	def get_enable_ssh(self):
		return self._enable_ssh

	##
	# Sets the root password on the livecd.  This is supposed to be given a hash.
	# @param xml_path not used here.
	# @param passwd a hashed password to be set on the livecd environment.
	# @param xml_attr not used here.
	def set_root_passwd(self, xml_path, passwd, xml_attr):
		self._root_passwd = passwd

	##
	# Returns the hash of the root password for the livecd environment
	def get_root_passwd(self):
		return self._root_passwd

	##
	# Sets whether or not to be an interactive install. (boolean)
	# @param xml_path not used here.
	# @param interactive True/False bool value or a string.
	# @param xml_attr not used here.
	def set_interactive(self, xml_path, interactive, xml_attr):
		if type(interactive) != bool:
			interactive = GLIUtility.strtobool(interactive)
		self._interactive = interactive

	##
	# Returns bool value on interactive install choice.
	# @param self Parameter description
	def get_interactive(self):
		return self._interactive

	##
	# Sets a list of modules to load on the livecd environment.
	# @param xml_path not used here.
	# @param modules string of modules
	# @param xml_attr not used here.
	def set_kernel_modules(self, xml_path, modules, xml_attr):
		self._kernel_modules = tuple(string.split(modules))

	##
	# Returns the list of kernel modules to load on the livecd environment.
	def get_kernel_modules(self):
		return self._kernel_modules

	##
	# Sets the FTP proxy URI
	# @param xml_path not used here.
	# @param proxy a URI
	# @param xml_attr not used here.
	def set_ftp_proxy(self, xml_path, proxy, xml_attr):
		self._ftp_proxy = proxy

	##
	# Returns the FTP proxy.
	# @param self Parameter description
	def get_ftp_proxy(self):
		return self._ftp_proxy

	##
	# Sets the HTTP proxy URI
	# @param xml_path not used here.
	# @param proxy a URI
	# @param xml_attr not used here.
	def set_http_proxy(self, xml_path, proxy, xml_attr):
		self._http_proxy = proxy

	##
	# Returns the HTTP proxy
	def get_http_proxy(self):
		return self._http_proxy

	##
	# Sets the RSYNC proxy URI
	# @param xml_path not used here.
	# @param proxy a URI
	# @param xml_attr not used here.
	def set_rsync_proxy(self, xml_path, proxy, xml_attr):
		self._rsync_proxy = proxy

	##
	# Returns the RSYNC proxy
	def get_rsync_proxy(self):
		return self._rsync_proxy

	##
	# Sets verbose mode or not.  currently not implemented.
	# @param xml_path not used here.
	# @param verbose bool or string
	# @param xml_attr not used here.
	def set_verbose(self, xml_path, verbose, xml_attr):
		if type(verbose) == str:
			verbose = GLIUtility.strtobool(verbose)

		self._verbose = verbose

	##
	# Returns verbose bool value
	def get_verbose(self):
		return self._verbose

	##
	# Serializes the Client Configuration into an XML format that is returned.
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
