"""
Gentoo Linux Installer

$Id: GLIClientConfiguration.py,v 1.7 2004/08/09 17:30:44 samyron Exp $
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
		self._profile_uri = profile_uri

	def get_install_steps_completed(self):
		return self._install_steps_completed
	
	def set_install_steps_completed(self, install_steps_completed):
		self._install_steps_completed = install_steps_completed

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

	def set_network_info(self, type):
		if type == 'specified':
			attr = self._xml_current_attr
			ip = broadcast = netmask = interface = ""

			for attrName in attr.getNames():
				if attrName == 'ip':
					ip = str(attr.getValue(attrName))
				elif attrName == 'broadcast':
					broadcast = str(attr.getValue(attrName))
				elif attrName == 'netmask':
					netmask = str(attr.getValue(attrName))
				elif attrName == 'interface':
					interface = str(attr.getValue(attrName))

			self._network_data = (interface, ip, broadcast, netmask)

		self._network_type = type

	def get_network_type(self):
		return self._network_type

	def get_network_info(self):
		return self._network_data

	def set_dns_servers(self, nameservers):
		nameservers = nameservers.split(" ")
		dns = []
		for server in nameservers:
			dns.append(server)

		self._dns_servers = tuple(dns)

	def get_dns_servers(self):
		return self._dns_servers

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
					'client-configuration/network-setup': self.set_network_info,
					'client-configuration/dns-servers': self.set_dns_servers
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
					'log-file': self.get_log_file
				}
		data = "<client-configuration>"

		for key in fntable.keys():
			data += "<%s>%s</%s>" % (key, fntable[key](), key)

		# Special Cases
		net_type = self.get_network_type()
		if net_type == "specified":
			net_info = self.get_network_info()
			data +=  "<network-setup interface=\"%s\" ip=\"%s\" broadcast=\"%s\" netmask=\"%s\">%s</network-setup>" % (net_info[0], net_info[1], net_info[2], net_info[3], net_type)
		else:
			data += "<network-setup>%s</network-setup>" % net_type
	

		data += "<dns-servers>%s</dns-servers>" % string.join(self.get_dns_servers())

		data += "</client-configuration>"

		import xml.dom.minidom
		dom = xml.dom.minidom.parseString(data)
                return dom.toprettyxml()

