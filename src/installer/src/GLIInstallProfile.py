"""
Gentoo Linux Installer

$Id: GLIInstallProfile.py,v 1.12 2004/08/11 15:07:20 samyron Exp $
Copyright 2004 Gentoo Technologies Inc.

The GLI module contains all classes used in the Gentoo Linux Installer (or GLI).
"""

import string
import xml.sax
import os
import GLIUtility

class InstallProfile(xml.sax.ContentHandler):
	"""
	An object representation of a profile.

	InstallProfile is an object representation of a parsed installation
	profile file.
	"""

	def __init__(self):
		# Configuration information - profile data
		self._cron_daemon_pkg = ""
		self._logging_daemon_pkg = ""
		self._boot_loader_mbr = True
		self._boot_loader_pkg = ""
		self._kernel_modules = []
		self._kernel_config_uri = ""
		self._kernel_initrd = False
		self._kernel_bootsplash = False
		self._kernel_source_pkg = ""
		self._users = []
		self._root_pass_hash = ""
		self._time_zone = ""
		self._stage_tarball_uri = ""
		self._install_stage = 1
		self._portage_tree_sync_type = "sync"
		self._portage_tree_snapshot_uri = ""
		self._domainname = "localdomain"
		self._hostname = "localhost"
		self._nisdomainname = ""
		self._partition_tables = {}
		self._network_interfaces = {}
		self._make_conf = {}
		self._rc_conf = {}
		self._ignore_install_step_depends = False
		self._install_rp_pppoe = False
		self._filesystem_tools = ()
		self._install_pcmcia_cs = False
		self._dns_servers = ()
		self._default_gateway = ''

		# Internal SAX state info
		self._xml_elements = [];
		self._xml_current_data = ""
		self._xml_current_attr = None

	def startElement(self, name, attr):
		"""
		XML SAX start element handler

		Called when the SAX parser encounters an XML openning element.
		"""

		self._xml_elements.append(name)
		self._xml_current_attr = attr
		self._xml_current_data = ""

	def endElement(self, name):
		"""
		XML SAX end element handler

		Called when the SAX parser encounters an XML closing element.
		"""
		# Instead of using 19 if/elif statements, use a jump table (well, pseudo jump table)
		fntable = 	{	'gli-profile/cron-daemon': self.set_cron_daemon_pkg,
					'gli-profile/logging-daemon': self.set_logging_daemon_pkg,
					'gli-profile/boot-loader_mbr': self.set_boot_loader_mbr,
					'gli-profile/boot-loader': self.set_boot_loader_pkg,
					'gli-profile/kernel-config': self.set_kernel_config_uri,
					'gli-profile/kernel-initrd': self.set_kernel_initrd,
					'gli-profile/kernel-bootsplash': self.set_kernel_bootsplash,
					'gli-profile/kernel-source': self.set_kernel_source_pkg,
					'gli-profile/root-pass-hash': self.set_root_pass_hash,
					'gli-profile/time-zone': self.set_time_zone,
					'gli-profile/stage-tarball': self.set_stage_tarball_uri,
					'gli-profile/install-stage': self.set_install_stage,
					'gli-profile/portage-tree-sync': self.set_portage_tree_sync_type,
					'gli-profile/portage-snapshot': self.set_portage_tree_snapshot_uri,
					'gli-profile/domainname': self.set_domainname,
					'gli-profile/hostname': self.set_hostname,
					'gli-profile/nisdomainname': self.set_nisdomainname,
					'gli-profile/ignore-depends': self.set_ignore_install_step_depends,
					'gli-profile/install-rp-pppoe': self.set_install_rp_pppoe,
					'gli-profile/filesystem-tools': self.set_filesystem_tools_pkgs,
					'gli-profile/install-pcmcia-cs': self.set_install_pcmcia_cs,
					'gli-profile/dns-servers': self.set_dns_servers,
					'gli-profile/default-gateway': self.set_default_gateway,
				}

		path = self._xml_element_path()

		if self._xml_current_data != '':
			# This is a normal case
			if path in fntable.keys():
				fntable[path](self._xml_current_data)
			else:
				# Handle the special cases
				if path == 'gli-profile/kernel-modules/module':
					self._add_kernel_module(self._xml_current_data)
				elif path == 'gli-profile/users/user':
					self.add_user(self._xml_current_data, self._xml_current_attr)
				elif path == 'gli-profile/make-conf/variable':
					self.make_conf_add_var(self._xml_current_data, self._xml_current_attr)
				elif path == 'gli-profile/rc-conf/variable':
					self.rc_conf_add_var(self._xml_current_data, self._xml_current_attr)
				elif path == 'gli-profile/network-interfaces/device':
					self.add_network_interface(self._xml_current_data, self._xml_current_attr)

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
		Parse serialized profile file.

		Parse the serialized installer profile file at 'path'. This
		will create and use a SAX parser to handle all the details. This
		class (GLI.InstallProfile) happens to be the SAX content handler
		subclass that will be used.
		"""

		xml.sax.parse(path, self)

	def get_cron_daemon_pkg(self):
		"returns cron_daemon_pkg"
		return self._cron_daemon_pkg

	def set_cron_daemon_pkg(self, cron_daemon_pkg):
		"cron_daemon_pkg is a string to determine which cron daemon to install and configure (ie. 'vixie-cron')"
		
		# Check data type
		if type(cron_daemon_pkg) != str:
			raise "CronDaemonPKGError", "Input must be type 'string'!"
		
		self._cron_daemon_pkg = cron_daemon_pkg

	def get_logging_daemon_pkg(self):
		"returns logging_daemon_pkg"
		return self._logging_daemon_pkg

	def set_logging_daemon_pkg(self, logging_daemon_pkg):
		"logging_daemon_pkg is a string to determine which logging daemon to install and configure (ie. 'sysklogd')"
		
		# Check data type
		if type(logging_daemon_pkg) != str:
			raise "LoggingDaemonPKGError", "Input must be type 'string'!"

		self._logging_daemon_pkg = logging_daemon_pkg

	def get_boot_loader_mbr(self):
		"returns boot_loader_mbr"
		return self._boot_loader_mbr

	def set_boot_loader_mbr(self, boot_loader_mbr):
		"boot_loader_mbr is a bool. True installs boot loader to MBR.  False installs boot loader to the boot or root partition."
		
		# Check data type
		if type(boot_loader_mbr) != bool:
			if type(boot_loader_mbr) == str:
				boot_loader_mbr = GLIUtility.strtobool(boot_loader_mbr)
			else:
				raise "BootLoaderMBRError", "Input must be type 'bool'!"
		
		self._boot_loader_mbr = boot_loader_mbr

	def get_boot_loader_pkg(self):
		"returns boot_loader_pkg"
		return self._boot_loader_pkg

	def set_boot_loader_pkg(self, boot_loader_pkg):
		"boot_loader_pkg is a string to decide which boot loader to install. (ie. 'grub')"
		
		# Check data type
		if type(boot_loader_pkg) != str:
			raise "BootLoaderPKG", "Input must be type 'string'!"

		self._boot_loader_pkg = boot_loader_pkg

	def get_kernel_modules(self):
		"returns kernel_modules"
		return self._kernel_modules

	def _add_kernel_module(self, kernel_module):
		"Add a kernel module to the list of kernel modules"

		if type(kernel_module) != str:
			raise "KernelModuleError", "The kernel module must be a string!"

		self._kernel_modules.append(kernel_module)
		
	def set_kernel_modules(self, kernel_modules):
		"kernel_modules is a tuple of strings containing names of modules to automatically load at boot time. (ie. '( 'ide-scsi', )')"
		
		# Check type
		if type(kernel_modules) != tuple:
			raise "KernelModulesError", "Must be a tuple!"
		
		self._kernel_modules = []
	
		# Check tuple data type
		for module in kernel_modules:
			self._add_kernel_module(module)

	def get_kernel_config_uri(self):
		"returns kernel_config_uri"
		return self._kernel_config_uri

	def set_kernel_config_uri(self, kernel_config_uri):
		"kernel_config_uri is a string that is the path to the kernel config file you wish to use.  Can also be a http:// or ftp:// path."
		
		# Check type
		if type(kernel_config_uri) != str:
			raise "KernelConfigURIError", "Must be a string!"

		# Check validity
		if not GLIUtility.is_uri(kernel_config_uri):
			raise "KernelConfigURIError", "Invalid URI!"

		self._kernel_config_uri = kernel_config_uri

	def get_kernel_initrd(self):
		"returns kernel_initrd"
		return self._kernel_initrd

	def set_kernel_initrd(self, kernel_initrd):
		"kernel_initrd is a bool to determine whether or not to build an initrd kernel.  False builds a non-initrd kernel. (overwritten by kernel_bootsplash; needs genkernel non-initrd support not yet present)"

		# Check type
		if type(kernel_initrd) != bool:
			if type(kernel_initrd) == str:
				kernel_initrd = GLIUtility.strtobool(kernel_initrd)
			else:
				raise "KernelInitRDError", "Must be a bool!"
		
		self._kernel_initrd = kernel_initrd

	def get_kernel_bootsplash(self):
		"returns kernel_bootsplash"
		return self._kernel_bootsplash

	def set_kernel_bootsplash(self, kernel_bootsplash):
		"kernel_bootsplash is a bool to determine whether or not to install bootsplash into the kernel.  True builds in bootsplash support to the initrd.  WARNING: kernel_source_pkg must contain a kernel with bootsplash support or the bootsplash will not appear.  If you set this to true, it will build an initrd kernel even if you chose false for kernel_initrd!"
		
		# Check type
		if type(kernel_bootsplash) != bool:
			if type(kernel_bootsplash) == str:
					kernel_bootsplash = GLIUtility.strtobool(kernel_bootsplash)
			else:
				raise "KernelBootsplashError", "Must be a bool!"
		
		self._kernel_bootsplash = kernel_bootsplash

	def get_kernel_source_pkg(self):
		"returns kernel_source_pkg"
		return self._kernel_source_pkg

	def set_kernel_source_pkg(self, kernel_source_pkg):
		"kernel_source_pkg is a string to define which kernel source to use.  (ie. 'gentoo-sources')"
		
		# Check type
		if type(kernel_source_pkg) != str:
			raise "KernelSourcePKGError", "Must be a string!"
		
		self._kernel_source_pkg = kernel_source_pkg

	def get_users(self):
		"returns users"
		return self._users

	def add_user(self, username='', attr=None):
		"""
		This will take a username (that is a string) and a set of attributes and it will verify everything is valid
		and convert it into a 7-tuple set. Then it adds this tuple into the users list.
		username and hash are manditory. All other attributes are optional. Or this method will
		take a 7-tuple set, verify it's correctness and then append it to the _users list.
		All items are strings except <uid>, which is an integer, and groups, which is a tuple. 

		The finished tuples look like this:
		( <user name>, <password hash>, (<tuple of groups>), <shell>, <home directory>, <user id>, <user comment> )

		"""
		hash = ''
		shell = None
		groups = None
		shell = None
		homedir = None
		uid = None
		comment = None

		if type(username) == tuple:
			if len(username) != 7:
				raise "UserError", "Wrong format for user tuple!"

			username_tmp = username[0]
			hash = username[1]
			groups = username[2]
			shell = username[3]
			homedir = username[4]
			uid = username[5]
			comment = username[6]
			username = username_tmp

			if type(groups) != tuple:
				if groups != None:
					groups = tuple(groups.split(','))
		else:
			for attrName in attr.getNames():
				if attrName == 'groups':
					groups = tuple(str(attr.getValue(attrName)).split(','))
				elif attrName == 'shell':
					shell = str(attr.getValue(attrName))
				elif attrName == 'hash':
					hash = str(attr.getValue(attrName))
				elif attrName == 'homedir':
					homedir = str(attr.getValue(attrName))
				elif attrName == 'uid':
					uid = int(attr.getValue(attrName))
				elif attrName == 'comment':
					comment = str(attr.getValue(attrName))

		allowable_nonalphnum_characters = '_-'

		if not GLIUtility.is_realstring(username):
			raise "UserError", "username must be a non-empty string"

		if username[0] not in (string.lowercase + string.uppercase):
			raise "UsersError", "A username must start with a letter!"

		for x in username:
			if x not in (string.lowercase + string.uppercase + string.digits + allowable_nonalphnum_characters):
				raise "UsersError", "A username must contain only letters, numbers, or these symbols: " + allowable_nonalphnum_characters

		for user in self._users:
			if username == user[0]:
				raise "UserError", "This username already exists!"

		if (hash == None) or (hash == ''):
			raise "UserError", "A password hash must be given for every user!"

		self._users.append((username,hash,groups,shell,homedir,uid,comment))

	def remove_user(self, username):
		"""
		Remove "username" from the _users list.
		"""
		for user in self._users:
			if username == user[0]:
				self._users.remove(user)
				break

	def set_users(self, users):
		"""
		users is a tuple(user) of tuple's. This sets _users to this set of tuples.
		"""
		self._users = []

		if users != None:
			for user in users:
				self.add_user(user)

	def get_root_pass_hash(self):
		"returns root_pass_hash"
		return self._root_pass_hash

	def set_root_pass_hash(self, root_pass_hash):
		"root_pass_hash is a string containing an md5 password hash to be assinged as the password for the root user."
		
		# Check type
		if type(root_pass_hash) != str:
			raise "RootPassHashError", "Must be a string!"
		
		self._root_pass_hash = root_pass_hash

	def get_time_zone(self):
		"returns time_zone"
		return self._time_zone

	def set_time_zone(self, time_zone):
		"time_zone is a string defining the time zone to use.  Time zones are found in /usr/share/zoneinfo/.  Syntax is 'UTC' or 'US/Eastern'."
		
		# Check type
		if type(time_zone) != str:
			raise "TimeZoneError", "Must be a string!"
			
		self._time_zone = time_zone

	def get_stage_tarball_uri(self):
		"returns stage_tarball_uri"
		return self._stage_tarball_uri

	def set_stage_tarball_uri(self, stage_tarball_uri):
		"stage_tarball_uri is a string that is the full path to the tarball you wish to use. (ie. 'file:///path/to/mytarball.tar.bz2')"

		# Check type
		if type(stage_tarball_uri) != str:
			raise "StageTarballURIError", "Must be a string!"

		# Check validity
		if not GLIUtility.is_uri(stage_tarball_uri):
			raise "CustomStage3TarballURIError", "Invalid URI!"
		
		self._stage_tarball_uri = stage_tarball_uri

	def get_install_stage(self):
		"returns install_stage"
		return self._install_stage

	def set_install_stage(self, install_stage):
		"install_stage is a integer to define which stage install to use.  Appropriate stages are 1-3."
		
		# Check type
		if type(install_stage) != int:
			if type(install_stage) == str:
				install_stage = int(install_stage)
		else:
			raise "InstallStageError", "Must be an integer!"
		
		# Check for stage bounds
		if 0 < install_stage < 4:
			self._install_stage = install_stage
		else:
			raise "InstallStageError", "install_stage must be 1-3!"

	def get_portage_tree_sync_type(self):
		"returns portage_tree_sync"
		return self._portage_tree_sync_type

	def set_portage_tree_sync_type(self, portage_tree_sync):
		"portage_tree_sync is a bool to determine whether or not to run 'emerge sync' to get the latest portage tree."
		
		# Check type
		if type(portage_tree_sync) != str:
			raise "PortageTreeSyncError", "Must be a string!"

		if string.lower(portage_tree_sync) not in ('sync', 'webrsync', 'custom'):
			raise "PortageTreeSyncError", "Invalid Input!"

		self._portage_tree_sync_type = string.lower(portage_tree_sync)

	def get_portage_tree_snapshot_uri(self):
		"returns portage_tree_snapshot_uri"
		return self._portage_tree_snapshot_uri

	def set_portage_tree_snapshot_uri(self, portage_tree_snapshot_uri):
		"portage_tree_snapshot_uri is a string defining the path to a portage tree snapshot. (ie. 'file:///mnt/cdrom/snapshots/portage-*.tar.bz2')"
		
		# Check type
		if type(portage_tree_snapshot_uri) != str:
			raise "PortageTreeSnapshotURIError", "Must be a string!"

		# Check validity
		if not GLIUtility.is_uri(portage_tree_snapshot_uri):
			raise "PortageTreeSnapshotURIError", "Invalid URI!"
		
		self._portage_tree_snapshot_uri = portage_tree_snapshot_uri

	def get_domainname(self):
		"returns domainname"
		return self._domainname

	def set_domainname(self, domainname):
		"domainname is a string containing the domainname for the new system. (ie. 'mydomain.com'; NOT FQDN)"
		
		# Check type
		if type(domainname) != str:
			raise "DomainnameError", "Must be a string!"
		
		self._domainname = domainname

	def get_hostname(self):
		"returns hostname"
		return self._hostname

	def set_hostname(self, hostname):
		"hostname is a string containing the hostname for the new system. (ie. 'myhost'; NOT 'myhost.mydomain.com')"

		# Check type
		if type(hostname) != str:
			raise "HostnameError", "Must be a string!"

		self._hostname = hostname

	def get_nisdomainname(self):
		"returns nisdomainname"
		return self._nisdomainname

	def set_nisdomainname(self, nisdomainname):
		"nisdomainname is a string containing the NIS domainname for the new system."
		
		# Check type
		if type(nisdomainname) != str:
			raise "NISDomainnameError", "Must be a string!"
			
		self._nisdomainname = nisdomainname
		
	def get_partition_tables(self):
		"returns partition_tables"
		return self._partition_tables

	def set_partition_tables(self, partition_tables):
		"""
		Sets the partition tables.  A partition is a multi level dictionary in the following format:
		{ <device (local)>: <partition table>, <device (nfs)>: <mount point> }
		
		<device (local)> is a string containing the path to the local file. (ie. '/dev/hda')
		<device (nfs)> is a string containing the ip address of the nfs mount. (ie. '192.168.1.2')
		
		<partition table> is a dictionary in the following format:
			{ <minor>: ( <size in mb>, <type>, <mount point> ) }
		
		ie. partition_tables['/dev/hda'][1] would return ( 64, 'ext3', '/boot' )

		Types are as follows:
		string: <device>, <type>, <mount point>
		integer: <minor>, <size in mb>
		
		Current <type> options include:
		ext2, ext3, reiserfs, xfs, jfs, swap, extended, resize, others?
		
		There will be a method in the partitioning code to make sure that the current parition_tables can actually be implemented.
		Should we call that function to test the culpability of our potential partitioning scheme?
		Should we create a method in the Controller to take raw variables and put them in the proper structure?
		Are all filesystems supported by all arches?
		"""
		
		if type(partition_tables) != dict:
			raise "PartitionTableError", "Invalid data type! partition_tables is a dict..."
		
		for device in partition_tables:
		
			# If the device is a valid local device...
			if GLIUtility.is_device(device):
			
				# We should check to make sure device is in /proc/partitions
				# If it is in /proc/partitions, it is a partitionable device
			
				# ... then loop through each minor to check data
				for minor in partition_tables[device]:

					# Make sure that the <minor> is an integer or can be converted to one
					try:
						int(minor)
					except:
						raise "ParitionTableError", "The minor you specified (" + minor + ") is not an integer!"
					
					# Make sure that a minor number is valid
					if minor < 1:
						raise "ParitionTableError", "The minor you specified (" + minor + ") is not a valid minor!"
				
					# Make sure that <size>, <type> and <mount point> are all set
					if len(partition_tables[device][minor]) != 3:
						raise "ParitionTableError", "The number of attributes for minor " + minor + " is incorrect!"
					
					# Make sure that the <size> is an integer or can be converted to one
					try:
						int(partition_tables[device][minor][0])
					except:
						raise "ParitionTableError", "The size you specified (" + partition_tables[device][minor][0] + ") is not an integer!"

			# Else, if the device is a valid remote device (hostname or ip)
			elif GLIUtility.is_ip(device) or GLIUtility.is_hostname(device):
			
				# Make sure that only the mount point is set
				if type(partition_tables[device]) != str:
					raise "ParitionTableError", "Invalid mount point for nfs mount (device: " + device + ")!"

			# If the device is not a local or remote device, then it is invalid
			else:
				raise "PartitionTableError", "The device you specified (" + device + ") is not valid!"

		# If all the tests clear, then set the variable
		self._partition_tables = partition_tables


	def get_network_interfaces(self):
		"Returns network_interfaces"
		return self._network_interfaces
		
	def add_network_interface(self, device, attr):
		"""
		This adds an ethernet device to the _network_interfaces dictionary.
		The format of this dictionary is:
		{ <eth_device> : (options tuple), ... }

		The format of the options tuple is:
		( <ip address>, <broadcast>, <netmask> )

		If the user wants to use DHCP, the <ip address> will be set to 'dhcp'
		and broadcast and netmask will both be set to None.

		Aliases are no longer needed in the tuple because they can be treated like
		an individual interface. GLIUtility.is_eth_device will recogniz
		"""
		options = None
		ip = broadcast = netmask = None
		dhcp = True

		if type(device) != str:
			raise "NetworkInterfacesError", "Invalid or unimplimented device type (" + device + ")!"
	
		if not GLIUtility.is_eth_device(device):
			raise "NetworkInterfacesError", "Invalid or unimplimented device type (" + device + ")!"

		if type(attr) == tuple:
			ip = attr[0]
			broadcast = attr[1]
			netmask = attr[2]
			if ip != 'dhcp':
				dhcp = False
		else:
			if "ip" in attr.getNames():
				for attrName in attr.getNames():
					if attrName == 'ip':
						ip = str(attr.getValue(attrName))
					elif attrName == 'broadcast':
						broadcast = str(attr.getValue(attrName))
					elif attrName == 'netmask':
						netmask = str(attr.getValue(attrName))
				dhcp = False

		if not dhcp:
			if not GLIUtility.is_ip(ip):
				raise "NetworkInterfacesError", "The ip address you specified for " + device + " is not valid!"
			if not GLIUtility.is_ip(broadcast):
				raise "NetworkInterfacesError", "The broadcast address you specified for " + device + " is not valid!"
			if not GLIUtility.is_ip(netmask):
				raise "NetworkInterfacesError", "The netmask address you specified for " + device + " is not valid!"
			options = (ip, broadcast, netmask)
		else:
			options = ('dhcp', None, None)

		self._network_interfaces[device] = options

	def set_network_interfaces(self, network_interfaces):
		"""
		This method sets the network interfaces diction to network_interfaces.
		This method uses the function add_network_interfaces to do all of the
		real work.
		"""
		
		# Check type
		if type(network_interfaces) != dict:
			raise "NetworkInterfacesError", "Must be a dictionary!"

		self._network_interfaces = {}
		for device in network_interfaces:
			self.add_network_interface(device, network_interfaces[device])

	def serialize(self):
		"""
		This method serializes the configuration data and output a nice XML document.

		NOTE: this method currently does not serialize: _partition_tables or _kernel_modules

		"""
		import xml.dom.minidom
		xmldoc = ""
		xmltab = {	'cron-daemon':		self.get_cron_daemon_pkg,
				'logging-daemon':	self.get_logging_daemon_pkg,
				'boot-loader_mbr':	self.get_boot_loader_mbr,
				'boot-loader':		self.get_boot_loader_pkg,
				'kernel-config':	self.get_kernel_config_uri,
				'kernel-initrd':	self.get_kernel_initrd,
				'kernel-bootsplash':	self.get_kernel_bootsplash,
				'kernel-source':	self.get_kernel_source_pkg,
				'root-pass-hash':	self.get_root_pass_hash,
				'time-zone':		self.get_time_zone,
				'custom-stage3-tarball':self.get_stage_tarball_uri,
				'install-stage':	self.get_install_stage,
				'portage-tree-sync':	self.get_portage_tree_sync_type,
				'portage-snapshot':	self.get_portage_tree_snapshot_uri,
				'domainname':		self.get_domainname,
				'hostname':		self.get_hostname,
				'nisdomainname':	self.get_nisdomainname,
				'ignore-depends':	self.get_ignore_install_step_depends,
				'install-rp-pppoe':	self.get_install_rp_pppoe,
				'install-pcmcia-cs':	self.get_install_pcmcia_cs,
				'default-gateway':	self.get_default_gateway,
		}

		xmldoc += "<?xml version=\"1.0\"?>"

		xmldoc += "<gli-profile>"

		# Normal cases
		for key in xmltab.keys():
			xmldoc += "<%s>%s</%s>" % (key, xmltab[key](), key)

		# Other cases
		if self.get_users() != []:
			xmldoc += "<users>"
			users = self.get_users()
			for user in users:
				attrstr = ""
				username = user[0]

				if user[1] != None:
					attrstr += "hash=\"%s\" " % user[1]
				if user[2] != None:
					attrstr += "groups=\"%s\" " % string.join(user[2],',')
				if user[3] != None:
					attrstr += "shell=\"%s\" " % user[3]
				if user[4] != None:
					attrstr += "homedir=\"%s\" " % user[4]
				if user[5] != None:
					attrstr += "uid=\"%s\" " % user[5]
				if user[6] != None:
					attrstr += "comment=\"%s\" " % user[6]

				xmldoc += "<user %s>%s</user>" % (string.strip(attrstr), username)
			xmldoc += "</users>"

		if self.get_make_conf() != {}:
			xmldoc += "<make-conf>"

			make_conf = self.get_make_conf()
			for var in make_conf:
				xmldoc += "<variable name=\"%s\">%s</variable>" % (var, make_conf[var])

			xmldoc += "</make-conf>"

		if self.get_rc_conf() != {}:
			xmldoc += "<rc-conf>"

			rc_conf = self.get_rc_conf()
			for var in rc_conf:
				xmldoc += "<variable name=\"%s\">%s</variable>" % (var, rc_conf[var])

			xmldoc += "</rc-conf>"

		if self.get_filesystem_tools_pkgs() != ():
			xmldoc += "<filesystem-tools>"
			xmldoc += string.join(self.get_filesystem_tools_pkgs(), ' ')
			xmldoc += "</filesystem-tools>"

		if self.get_dns_servers() != ():
			xmldoc += "<dns-servers>"
			xmldoc += string.join(self.get_dns_servers(), ' ')
			xmldoc += "</dns-servers>"

		if self.get_network_interfaces() != {}:
			xmldoc += "<network-interfaces>"
			interfaces = self.get_network_interfaces()
			for iface in interfaces:
				if interfaces[iface][0] == 'dhcp':
					xmldoc += "<device>%s</device>" % iface
				else:
					xmldoc += "<device ip=\"%s\" broadcast=\"%s\" netmask=\"%s\">%s</device>" % (interfaces[iface][0], interfaces[iface][1], interfaces[iface][2], iface)
			xmldoc += "</network-interfaces>"

		if self.get_kernel_modules() != []:
			kernel_modules = self.get_kernel_modules()
			xmldoc += "<kernel-modules>";
			for module in kernel_modules:
				xmldoc += "<module>%s</module>" % module
			xmldoc += "</kernel-modules>";

		xmldoc += "</gli-profile>"

		dom = xml.dom.minidom.parseString(xmldoc)
		return dom.toprettyxml()

	def make_conf_add_var(self, data, attr):
		"""
		data is a string that is the value of the variable name.
		attr is an xml attribute that contains the name of the variable
		"""
		if 'name' not in attr.getNames():
			raise "MakeConfError", "Every value needs to have a variable name!"

		varName = attr.getValue('name')
		self._make_conf[str(varName)] = str(data)

	def set_make_conf(self, make_conf):
		"""
		make_conf is a dictionary that will be set to _make_conf

		There is no checking that needs to be done, so please sure sure that the make_conf dictionary
		that is passed in is valid.
		"""

		self._make_conf = make_conf

	def get_make_conf(self):
		""" Return a dictionary of the make.conf """
		return self._make_conf

	def rc_conf_add_var(self, data, attr):
		"""
		data is a string that is the value of the variable name.
		attr is an xml attribute that contains the name of the variable
		"""
		if 'name' not in attr.getNames():
			raise "RCConfError", "Every value needs to have a variable name!"

		varName = attr.getValue('name')
		self._rc_conf[str(varName)] = str(data)

	def set_rc_conf(self, rc_conf):
		"""
		rc_conf is a dictionary that will be set to _rc_conf

		There is no checking that needs to be done, so please sure sure that the rc_conf dictionary
		that is passed in is valid.
		"""

		self._rc_conf = rc_conf

	def get_rc_conf(self):
		""" Return a dictionary of the make.conf """
		return self._rc_conf

	def set_ignore_install_step_depends(self, ignore_depends):
		""" 
		Set _ignore_install_step_depends to ignore_depends, if it is a bool, if not, convert
		it first, then set _ignore_install_step_depends to val.
		"""
		# Check the data type
		if type(ignore_depends) != bool:
			if type(ignore_depends) == str:
				ignore_depends = GLIUtility.strtobool(ignore_depends)
			else:
				raise "IgnoreInstallStepDepends", "Input must be type 'bool'!"
		
		self._ignore_install_step_depends = ignore_depends

	def get_ignore_install_step_depends(self):
		""" Return _ignore_install_step_depends """
		return self._ignore_install_step_depends

	def set_install_rp_pppoe(self, install_rp_pppoe):
		"""
		Tell the installer whether or not to install the rp-pppoe package
		"""

		if type(install_rp_pppoe) != bool:
			if type(install_rp_pppoe) == str:
				install_rp_pppoe = GLIUtility.strtobool(install_rp_pppoe)
			else:
				raise "InstallRP_PPPOE", "Invalid input!"

		self._install_rp_pppoe = install_rp_pppoe

	def get_install_rp_pppoe(self):
		""" Return the boolean value of _install_rp_pppoe """
		return self._install_rp_pppoe

	def set_filesystem_tools_pkgs(self, tools):
		"""
		This method will take either a string or a list/tuple of strings that are
		packages of the filesystem tools that need to be installed. For example,
		"sys-fs/reiserfsprogs" might be the input, or a list of tuples similar
		to that will be the input
		"""
		if (type(tools) == list) or (type(tools) == tuple):
			self._filesystem_tools = tools
		elif GLIUtility.is_realstring(tools):
			self._filesystem_tools = tuple(string.split(tools))
		else:
			raise "FileSystemTools","Invalid input!"

	def get_filesystem_tools_pkgs(self):
		"""
		This method will return the string or tuple of the filesystem programs
		that need to be installed.
		"""
		return self._filesystem_tools

	def set_install_pcmcia_cs(self, install_pcmcia):
		""" This tells the installer whether or not to install the pcmcia_cs package """
		if type(install_pcmcia) != bool:
			if type(install_pcmcia) == str:
				install_pcmcia = GLIUtility.strtobool(install_pcmcia)
			else:
				raise "InstallPcmciaCS", "Input must be type 'bool'!"

		self._install_pcmcia_cs = install_pcmcia

	def get_install_pcmcia_cs(self):
		""" Returns the boolean _install_pcmcia_cs """

		return self._install_pcmcia_cs

	def set_dns_servers(self, dns_servers):
		"""
		Set the DNS servers for the post-installed system.
		"""

		if type(dns_servers) == tuple:
			dns_servers = dns_servers[0:3]
		elif type(dns_servers) == str:
			dns_servers = string.split(dns_servers)
		else:
			raise "DnsServersError", "Invalid input!"

		for server in dns_servers:
			if not GLIUtility.is_ip(server):
				raise "DnsServersError", server + " must be a valid IP address!"

		self._dns_servers = dns_servers

	def get_dns_servers(self):
		""" This returns a tuple of the form:
			(<nameserver 1>, <nameserver 2>, <nameserver 3>)
		"""
		return self._dns_servers

	def set_default_gateway(self, gateway):
		""" 
		Set the default gateway for the post-installed system.
		The format of the input is: <device>/<gateway IP addr>
		"""
		if not GLIUtility.is_realstring(gateway):
			raise "DefaultGateway", "The gateway must be a non-empty string!"

		seperator = string.find(gateway, '/')
		if seperator == -1:
			raise "DefaultGateway", "Invalid input!"

		dev = gateway[0:seperator]
		gateway_ip = gateway[seperator+1:]

		if dev[0:3] not in ('eth', 'ppp', 'wla'):
			raise "DefaultGateway", "Invalid device!"

		if not GLIUtility.is_ip(gateway_ip):
			raise "DefaultGateway", "The IP Provided is not valid!"

		self._default_gateway = gateway

	def get_default_gateway(self):
		"""
		Returns the default gateway
		"""
		return self._default_gateway

