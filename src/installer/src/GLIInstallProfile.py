"""
Gentoo Linux Installer

$Id: GLIInstallProfile.py,v 1.20 2004/12/04 08:33:47 codeman Exp $
Copyright 2004 Gentoo Technologies Inc.

The GLI module contains all classes used in the Gentoo Linux Installer (or GLI).
"""

import string
import xml.sax
import os
import GLIUtility
import SimpleXMLParser
from GLIException import *

class InstallProfile:
	"""
	An object representation of a profile.

	InstallProfile is an object representation of a parsed installation
	profile file.
	"""

	def __init__(self):
		parser = SimpleXMLParser.SimpleXMLParser()

		parser.addHandler('gli-profile/stage-tarball', self.set_stage_tarball_uri)
		parser.addHandler('gli-profile/kernel-initrd', self.set_kernel_initrd)
		parser.addHandler('gli-profile/dns-servers', self.set_dns_servers)
		parser.addHandler('gli-profile/portage-tree-sync', self.set_portage_tree_sync_type)
		parser.addHandler('gli-profile/install-pcmcia-cs', self.set_install_pcmcia_cs)
		parser.addHandler('gli-profile/default-gateway', self.set_default_gateway)
		parser.addHandler('gli-profile/kernel-bootsplash', self.set_kernel_bootsplash)
		parser.addHandler('gli-profile/cron-daemon', self.set_cron_daemon_pkg)
		parser.addHandler('gli-profile/root-pass-hash', self.set_root_pass_hash)
		parser.addHandler('gli-profile/kernel-config', self.set_kernel_config_uri)
		parser.addHandler('gli-profile/domainname', self.set_domainname)
		parser.addHandler('gli-profile/portage-snapshot', self.set_portage_tree_snapshot_uri)
		parser.addHandler('gli-profile/time-zone', self.set_time_zone)
		parser.addHandler('gli-profile/boot-loader_mbr', self.set_boot_loader_mbr)
		parser.addHandler('gli-profile/nisdomainname', self.set_nisdomainname)
		parser.addHandler('gli-profile/install-stage', self.set_install_stage)
		parser.addHandler('gli-profile/boot-loader', self.set_boot_loader_pkg)
		parser.addHandler('gli-profile/install-rp-pppoe', self.set_install_rp_pppoe)
		parser.addHandler('gli-profile/kernel-source', self.set_kernel_source_pkg)
		parser.addHandler('gli-profile/filesystem-tools', self.set_filesystem_tools_pkgs)
		parser.addHandler('gli-profile/hostname', self.set_hostname)
		parser.addHandler('gli-profile/logging-daemon', self.set_logging_daemon_pkg)
		parser.addHandler('gli-profile/ignore-depends', self.set_ignore_install_step_depends)
		parser.addHandler('gli-profile/kernel-modules/module', self.add_kernel_module)
		parser.addHandler('gli-profile/users/user', self.add_user)
		parser.addHandler('gli-profile/make-conf/variable', self.make_conf_add_var)
		parser.addHandler('gli-profile/rc-conf/variable', self.rc_conf_add_var)
		parser.addHandler('gli-profile/network-interfaces/device', self.add_network_interface)
		parser.addHandler('gli-profile/install-packages', self.set_install_packages)
		parser.addHandler('gli-profile/fstab/partition', self.add_fstab_partition)
		parser.addHandler('gli-profile/partitions/device', self.add_partitions_device, call_on_null=True)
		parser.addHandler('gli-profile/partitions/device/partition', self.add_partitions_device_partition, call_on_null=True)
		parser.addHandler('gli-profile/mta', self.set_mta)
		
		self._parser = parser

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
		self._portage_tree_snapshot_uri = "file:///mnt/cdrom/snapshots/portage-20040710.tar.bz2"
		self._domainname = "localdomain"
		self._hostname = "localhost"
		self._nisdomainname = ""
		self._partition_tables = {}
		self._temp_partition_table = {}
		self._network_interfaces = {}
		self._make_conf = {}
		self._rc_conf = {}
		self._ignore_install_step_depends = False
		self._install_rp_pppoe = False
		self._filesystem_tools = ()
		self._install_pcmcia_cs = False
		self._dns_servers = ()
		self._default_gateway = ()
		self._fstab = {}
		self._install_packages = ()
		self._mta = ""

	def parse(self, filename):
		self._parser.parse(filename)

	def get_cron_daemon_pkg(self):
		"returns cron_daemon_pkg"
		return self._cron_daemon_pkg

	def set_cron_daemon_pkg(self, xml_path, cron_daemon_pkg, xml_attr):
		"cron_daemon_pkg is a string to determine which cron daemon to install and configure (ie. 'vixie-cron')"
		
		# Check data type
		if type(cron_daemon_pkg) != str:
			raise "CronDaemonPKGError", "Input must be type 'string'!"
		
		self._cron_daemon_pkg = cron_daemon_pkg

	def get_logging_daemon_pkg(self):
		"returns logging_daemon_pkg"
		return self._logging_daemon_pkg

	def set_logging_daemon_pkg(self, xml_path, logging_daemon_pkg, xml_attr):
		"logging_daemon_pkg is a string to determine which logging daemon to install and configure (ie. 'sysklogd')"
		
		# Check data type
		if type(logging_daemon_pkg) != str:
			raise "LoggingDaemonPKGError", "Input must be type 'string'!"

		self._logging_daemon_pkg = logging_daemon_pkg

	def get_boot_loader_mbr(self):
		"returns boot_loader_mbr"
		return self._boot_loader_mbr

	def set_boot_loader_mbr(self, xml_path, boot_loader_mbr, xml_attr):
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

	def set_boot_loader_pkg(self, xml_path, boot_loader_pkg, xml_attr):
		"boot_loader_pkg is a string to decide which boot loader to install. (ie. 'grub')"
		
		# Check data type
		if type(boot_loader_pkg) != str:
			raise "BootLoaderPKG", "Input must be type 'string'!"

		self._boot_loader_pkg = boot_loader_pkg

	def get_kernel_modules(self):
		"returns kernel_modules"
		return self._kernel_modules

	def add_kernel_module(self, xml_path, kernel_module, xml_attr):
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

	def set_kernel_config_uri(self, xml_path, kernel_config_uri, xml_attr):
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

	def set_kernel_initrd(self, xml_path, kernel_initrd, xml_attr):
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

	def set_kernel_bootsplash(self, xml_path, kernel_bootsplash, xml_attr):
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

	def set_kernel_source_pkg(self, xml_path, kernel_source_pkg, xml_attr):
		"kernel_source_pkg is a string to define which kernel source to use.  (ie. 'gentoo-sources')"
		
		# Check type
		if type(kernel_source_pkg) != str:
			raise "KernelSourcePKGError", "Must be a string!"
		
		self._kernel_source_pkg = kernel_source_pkg

	def get_users(self):
		"returns users"
		return self._users

	def add_user(self, xml_path, username, attr=None):
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
			for attrName in attr.keys():
				if attrName == 'groups':
					groups = tuple(str(attr[attrName]).split(','))
				elif attrName == 'shell':
					shell = str(attr[attrName])
				elif attrName == 'hash':
					hash = str(attr[attrName])
				elif attrName == 'homedir':
					homedir = str(attr[attrName])
				elif attrName == 'uid':
					uid = int(attr[attrName])
				elif attrName == 'comment':
					comment = str(attr[attrName])

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

	def set_root_pass_hash(self, xml_path, root_pass_hash, xml_attr):
		"root_pass_hash is a string containing an md5 password hash to be assinged as the password for the root user."
		
		# Check type
		if type(root_pass_hash) != str:
			raise "RootPassHashError", "Must be a string!"
		
		self._root_pass_hash = root_pass_hash

	def get_time_zone(self):
		"returns time_zone"
		return self._time_zone

	def set_time_zone(self, xml_path, time_zone, xml_attr):
		"time_zone is a string defining the time zone to use.  Time zones are found in /usr/share/zoneinfo/.  Syntax is 'UTC' or 'US/Eastern'."
		
		# Check type
		if type(time_zone) != str:
			raise "TimeZoneError", "Must be a string!"
			
		self._time_zone = time_zone

	def get_stage_tarball_uri(self):
		"returns stage_tarball_uri"
		return self._stage_tarball_uri

	def set_stage_tarball_uri(self, xml_path, stage_tarball_uri, xml_attr):
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

	def set_install_stage(self, xml_path, install_stage, xml_attr):
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

	def set_portage_tree_sync_type(self, xml_path, portage_tree_sync, xml_attr):
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

	def set_portage_tree_snapshot_uri(self, xml_path, portage_tree_snapshot_uri, xml_attr):
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

	def set_domainname(self, xml_path, domainname, xml_attr):
		"domainname is a string containing the domainname for the new system. (ie. 'mydomain.com'; NOT FQDN)"
		
		# Check type
		if type(domainname) != str:
			raise "DomainnameError", "Must be a string!"
		
		self._domainname = domainname

	def get_hostname(self):
		"returns hostname"
		return self._hostname

	def set_hostname(self, xml_path, hostname, xml_attr):
		"hostname is a string containing the hostname for the new system. (ie. 'myhost'; NOT 'myhost.mydomain.com')"

		# Check type
		if type(hostname) != str:
			raise "HostnameError", "Must be a string!"

		self._hostname = hostname

	def get_nisdomainname(self):
		"returns nisdomainname"
		return self._nisdomainname

	def set_nisdomainname(self, xml_path, nisdomainname, xml_attr):
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
			{ <minor>: { 'mb': <size in mb>, 'type': <type>, 'mountpoint': <mount point>, 'start': <start cylinder>,
			             'end': <end cylinder>, 'mountopts': <mount options>, 'format': <format> } }
		
		ie. partition_tables['/dev/hda'][1] would return { 'mb': 0, 'type': 'ext3', 'mountpoint': '/boot', 'start': 12345,
								   'end': 34567, 'mountopts': 'auto', format: 'False' }

		Types are as follows:
		string: <device>, <mount point>, <mount options>, <type>
		integer: <minor>, <size in mb>, <start cylinder>, <end cylinder>
		boolean: <format>
		
		Current <type> options include:
		ext2, ext3, reiserfs, xfs, jfs, linux-swap, extended, others?
		
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
					#if len(partition_tables[device][minor]) != 3:
					#	raise "ParitionTableError", "The number of attributes for minor " + minor + " is incorrect!"
					#
					# Make sure that the <size> is an integer or can be converted to one
					#try:
					#	int(partition_tables[device][minor][0])
					#except:
					#	raise "ParitionTableError", "The size you specified (" + partition_tables[device][minor][0] + ") is not an integer!"

			# Else, if the device is a valid remote device (hostname or ip)
			elif GLIUtility.is_ip(device) or GLIUtility.is_hostname(device):
			
				pass
				# Make sure that only the mount point is set
			#	if type(partition_tables[device]) != str:
			#		raise "ParitionTableError", "Invalid mount point for nfs mount (device: " + device + ")!"

			# If the device is not a local or remote device, then it is invalid
			else:
				raise "PartitionTableError", "The device you specified (" + device + ") is not valid!"

		# If all the tests clear, then set the variable
		self._partition_tables = partition_tables


	def get_network_interfaces(self):
		"Returns network_interfaces"
		return self._network_interfaces
		
	def add_network_interface(self, xml_path, device, attr):
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
				for attrName in attr.keys():
					if attrName == 'ip':
						ip = str(attr[attrName])
					elif attrName == 'broadcast':
						broadcast = str(attr[attrName])
					elif attrName == 'netmask':
						netmask = str(attr[attrName])
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
			self.add_network_interface(None, device, network_interfaces[device])

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
				'stage-tarball':	self.get_stage_tarball_uri,
				'install-stage':	self.get_install_stage,
				'portage-tree-sync':	self.get_portage_tree_sync_type,
				'portage-snapshot':	self.get_portage_tree_snapshot_uri,
				'domainname':		self.get_domainname,
				'hostname':		self.get_hostname,
				'nisdomainname':	self.get_nisdomainname,
				'ignore-depends':	self.get_ignore_install_step_depends,
				'install-rp-pppoe':	self.get_install_rp_pppoe,
				'install-pcmcia-cs':	self.get_install_pcmcia_cs,
				'mta':			self.get_mta,
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

		if self.get_fstab() != {}:
			xmldoc += "<fstab>"
			partitions = self.get_fstab()
			for part in partitions:
				xmldoc += "<partition dev=\"%s\" fstype=\"%s\" options=\"%s\">%s</partition>" % (partitions[part][0],partitions[part][1],partitions[part][2],part)
			xmldoc += "</fstab>"

		if self.get_install_packages() != ():
			xmldoc += "<install-packages>"
			xmldoc += string.join(self.get_install_packages(), ' ')
			xmldoc += "</install-packages>"
 
		if self.get_default_gateway() != ():
			gw = self.get_default_gateway()
			xmldoc += "<default-gateway interface=\"%s\">%s</default-gateway>" % (gw[0], gw[1])

		if self.get_partition_tables() != {}:
			partitions = self.get_partition_tables()
			xmldoc += "<partitions>";
			for device in partitions.keys():
				xmldoc += "<device devnode=\"%s\">" % device
				for minor in partitions[device]:
					part = partitions[device][minor]
					xmldoc += "<partition minor=\"%s\" mb=\"%s\" type=\"%s\" mountpoint=\"%s\" start=\"%s\" end=\"%s\" mountopts=\"%s\" format=\"%s\" />" % (str(minor), str(part['mb']), str(part['type']), str(part['mountpoint']), str(part['start']), str(part['end']), str(part['mountopts']), str(part['format']))
				xmldoc += "</device>"
			xmldoc += "</partitions>";

		xmldoc += "</gli-profile>"

		dom = xml.dom.minidom.parseString(xmldoc)
		return dom.toprettyxml()

	def make_conf_add_var(self, xml_path, data, attr):
		"""
		data is a string that is the value of the variable name.
		attr is an xml attribute that contains the name of the variable
		OR attr is a variable name, like 'USE'. This makes it easier for front-end designers.
		"""
		if type(attr) == 'str':
			self._make_conf[attr] = str(data)
		else:
			if 'name' not in attr.keys():
				raise "MakeConfError", "Every value needs to have a variable name!"

			varName = attr['name']
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

	def rc_conf_add_var(self, xml_path, data, attr):
		"""
		data is a string that is the value of the variable name.
		attr is an xml attribute that contains the name of the variable
		"""
		if 'name' not in attr.keys():
			raise "RCConfError", "Every value needs to have a variable name!"

		varName = attr['name']
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

	def set_ignore_install_step_depends(self, xml_path, ignore_depends, xml_attr):
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

	def set_install_rp_pppoe(self, xml_path, install_rp_pppoe, xml_attr):
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

	def set_filesystem_tools_pkgs(self, xml_path, tools, xml_attr):
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

	def set_install_pcmcia_cs(self, xml_path, install_pcmcia, xml_attr):
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

	def set_dns_servers(self, xml_path, dns_servers, xml_attr):
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

	def set_default_gateway(self, xml_path, gateway, xml_attr):
		""" 
		Set the default gateway for the post-installed system.
		The format of the input is: <default-gateway interface="interface name">ip of gateway</default-gateway>
		It saves this information in the following format: (<interface>, <ip of gateway>)
		"""

		if not GLIUtility.is_realstring(gateway):
			raise DefaultGatewayError('fatal', 'set_default_gateway', "The gateway must be a non-empty string!")

		if not 'interface' in xml_attr.keys():
			raise DefaultGatewayError('fatal', 'set_default_gateway', 'No interface information specified!')

		interface = str(xml_attr['interface'])

		if not GLIUtility.is_eth_device(interface):
			raise DefaultGatewayError('fatal', 'set_default_gateway', "Invalid device!")

		if not GLIUtility.is_ip(gateway):
			raise "DefaultGateway", "The IP Provided is not valid!"

		self._default_gateway = (interface, gateway)

	def get_default_gateway(self):
		"""
		Returns the default gateway
		"""
		return self._default_gateway

 
	def add_fstab_partition(self, xml_path, mountpoint, attr):
		"""
		This adds a partition to the list of partitions to be mounted in fstab.
		the format should be:
		<fstab>
			<partition dev="/dev/hda1" fstype="ext3" options="nostuff, defaults">/</partition>
		"""
		info = None
		options = fstype = dev = None
		if not GLIUtility.is_realstring(mountpoint):
			raise "AddPartitionError", "Invalid mountpoint or mountpoint does not exist!"

		
		if type(attr) == tuple:
			dev = attr[0]
			fstype = attr[1]
			options = attr[2]
			
		else:
			if "dev" in attr.getNames():
				for attrName in attr.getNames():
					if attrName == 'dev':
						dev = str(attr.getValue(attrName))
					elif attrName == 'fstype':
						fstype = str(attr.getValue(attrName))
					elif attrName == 'options':
						options = str(attr.getValue(attrName))	
		info = (dev,fstype,options)
		self._fstab[mountpoint] = info

	def get_fstab(self):
		"""
		Returns the fstab info.
		"""
		return self._fstab			
		
	def set_install_packages(self, xml_path, install_packages, xml_attr):
		"""
		Set the packages to be installed for the post-installed system.
		"""

		if type(install_packages) == str:
			install_packages = string.split(install_packages)
		else:
			raise "InstallPackagesError", "Invalid input!"

		for install_package in install_packages:
			if not GLIUtility.is_realstring(install_package):
				raise "InstallPackagesError", install_package + " must be a valid string!"

		self._install_packages = install_packages
 
	def get_install_packages(self):
		""" 
		This returns a list of the packages:
		"""
		return self._install_packages

	def add_partitions_device(self, xml_path, unused, attr):
		devnode = None
		if type(attr) == tuple:
			devnode = attr[0]
		else:
			if "devnode" in attr.getNames():
				devnode = str(attr.getValue("devnode"))
		self._partition_current_device = devnode
		self._partition_tables[devnode] = self._temp_partition_table
		self._temp_partition_table = {}

	def add_partitions_device_partition(self, xml_path, unused, attr):
		part_entry = {'end': 0, 'format': None, 'mb': 0, 'minor': 0, 'mountopts': '', 'mountpoint': '', 'start': 0, 'type': ''}
		if type(attr) == tuple:
			part_entry['end'] = attr[0]
			part_entry['format'] = attr[1]
			part_entry['mb'] = attr[2]
			part_entry['minor'] = attr[3]
			part_entry['mountopts'] = attr[4]
			part_entry['mountpoint'] = attr[5]
			part_entry['start'] = attr[6]
			part_entry['type'] = attr[7]
		else:
			if "minor" in attr.getNames():
				for attrName in attr.getNames():
					part_entry[attrName] = str(attr.getValue(attrName))
		if type(part_entry['format']) == str: part_entry['format'] = GLIUtility.strtobool(part_entry['format'])
		if GLIUtility.is_numeric(part_entry['end']): part_entry['end'] = int(part_entry['end'])
		if GLIUtility.is_numeric(part_entry['start']): part_entry['start'] = int(part_entry['start'])
		if GLIUtility.is_numeric(part_entry['mb']): part_entry['mb'] = int(part_entry['mb'])
		if GLIUtility.is_numeric(part_entry['minor']): part_entry['minor'] = int(part_entry['minor'])
		self._temp_partition_table[part_entry['minor']] = part_entry

	def set_mta(self, xml_path, mta, xml_attr):
		if type(mta) != str:
			raise "MTAError", "The MTA must be a string!"

		self._mta = mta

	def get_mta(self):
		return self._mta
