"""
Gentoo Linux Installer

$Id: GLI.py,v 1.14 2004/03/16 02:38:19 esammer Exp $
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

	# Configuration information - profile data
	_cron_daemon_pkg = ""
	_logging_daemon_pkg = ""
	_boot_loader_mbr = True
	_boot_loader_pkg = ""
	_kernel_modules = ()
	_kernel_config_uri = ""
	_kernel_initrd = False
	_kernel_bootsplash = False
	_kernel_source_pkg = ""
	_users = ()
	_root_pass_hash = ""
	_time_zone = ""
	_custom_stage3_tarball_uri = ""
	_install_stage = 1
	_portage_tree_sync = True
	_portage_tree_snapshot_uri = ""
	_domainname = "localdomain"
	_hostname = "localhost"
	_nisdomainname = ""
	_partition_tables = {}
	_network_interfaces = {}


	# Internal SAX state info
	_xml_elements = [];
	_xml_current_data = ""
	_xml_current_attr = None

	def __init__(self):
		pass
		
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

		path = self._xml_element_path()

		if path == 'gli-profile/cron-daemon':
			self.set_cron_daemon_pkg(self._xml_current_data)
		elif path == 'gli-profile/logging-daemon':
			self.set_logging_daemon_pkg(self._xml_current_data)
		elif path == 'gli-profile/boot-loader_mbr':
			self.set_boot_loader_mbr(self._xml_current_data)
		elif path == 'gli-profile/boot-loader':
			self.set_boot_loader_pkg(self._xml_current_data)
		elif path == 'gli-profile/kernel-modules/module':
			self.get_kernel_modules().append(self._xml_current_data)
		elif path == 'gli-profile/kernel-config':
			self.set_kernel_config_uri(self._xml_current_data)
		elif path == 'gli-profile/kernel-initrd':
			self.set_kernel_initrd(self._xml_current_data)
		elif path == 'gli-profile/kernel-bootsplash':
			self.set_kernel_bootsplash(self._xml_current_data)
		elif path == 'gli-profile/kernel-source':
			self.set_kernel_source_pkg(self._xml_current_data)
		elif path == 'gli-profile/users':
			self.get_users().append(self._xml_current_data)
		elif path == 'gli-profile/root-pass-hash':
			self.set_root_pass_hash(self._xml_current_data)
		elif path == 'gli-profile/time-zone':
			self.set_time_zone(self._xml_current_data)
		elif path == 'gli-profile/custom-stage3-tarball':
			self.set_custom_stage3_tarball_uri(self._xml_current_data)
		elif path == 'gli-profile/install-stage':
			self.set_install_stage(self._xml_current_data)
		elif path == 'gli-profile/portage-tree-sync':
			self.set_portage_tree_sync(self._xml_current_data)
		elif path == 'gli-profile/portage-snapshot':
			self.set_portage_snapshot(self._xml_current_data)
		elif path == 'gli-profile/domainname':
			self.set_domainname(self._xml_current_data)
		elif path == 'gli-profile/hostname':
			self.set_hostname(self._xml_current_data)
		elif path == 'gli-profile/nisdomainname':
			self.set_nisdomainname(self._xml_current_data)

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
		self._xml_current_data += str(data)

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

	def set_logging_daemon_pkg(self, loggin_daemon):
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

	def set_kernel_modules(self, kernel_modules):
		"kernel_modules is a tuple of strings containing names of modules to automatically load at boot time. (ie. '( 'ide-scsi', )')"
		
		# Check type
		if type(kernel_modules) != tuple:
			raise "KernelModulesError", "Must be a tuple!"
			
		# Check tuple data type
		for module in kernel_modules:
			if type(module) != str:
				raise "KernelModulesError", "Kernel modules tuple must contain strings!"
		
		# Set the data
		self._kernel_modules = kernel_modules

	def get_kernel_config_uri(self):
		"returns kernel_config_uri"
		return self._kernel_config_uri

	def set_kernel_config_uri(self, kernel_config_uri):
		"kernel_config_uri is a string that is the path to the kernel config file you wish to use.  Can also be a http:// or ftp:// path."
		
		# Check type
		if type(kernel_config_uri) != str:
			raise "KernelConfigURIError", "Must be a string!"

		# Check validity
		if not GLIUtility._is_uri(kernel_config_uri):
			raise "KernelConfigURIError", "Invalid URI!"

		self._kernel_config_uri = kernel_config_uri

	def get_kernel_initrd(self):
		"returns kernel_initrd"
		return self._kernel_initrd

	def set_kernel_initrd(self, kernel_initrd):
		"kernel_initrd is a bool to determine whether or not to build an initrd kernel.  False builds a non-initrd kernel. (overwritten by kernel_bootsplash; needs genkernel non-initrd support not yet present)"

		# Check type
		if type(kernel_initrd) != bool:
			raise "KernelInitRDError", "Must be a bool!"
		
		self._kernel_initrd = kernel_initrd

	def get_kernel_bootsplash(self):
		"returns kernel_bootsplash"
		return self._kernel_bootsplash

	def set_kernel_bootsplash(self, kernel_bootsplash):
		"kernel_bootsplash is a bool to determine whether or not to install bootsplash into the kernel.  True builds in bootsplash support to the initrd.  WARNING: kernel_source_pkg must contain a kernel with bootsplash support or the bootsplash will not appear.  If you set this to true, it will build an initrd kernel even if you chose false for kernel_initrd!"
		
		# Check type
		if type(kernel_bootsplash) != bool:
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

	def set_users(self, users):
		"""
		users is a tuple of users.
		A 'user' is defined as a tuple with the following format: ( <user_name>, <user_pass_hash>, ( <user_group1>, <user_group2> ), <user_shell_uri>, <user_homedir>, <uid>, <user_comment> ). 
		Therefore, a user is a tuple embeded in a list containing all users.
		All items are strings except <uid> which is an integer.
		<user_name> and <user_pass_hash> are NOT optional, the rest are (by passing None)
		
		"""
		
		if type(users) != tuple:
			raise "UsersError", "users variable must be a tuple!"
			
		for user in users:
			# Test for proper user name stuff
			allowable_nonalphnum_characters = '_-'
			if type(user[0]) != str:
				raise "UsersError", "A username must be a string!"
			if not user[0][0] in string.lowercase:
				raise "UsersError", "A username must start with a letter!"
			for char in user[0]:
				if not char in (string.lowercase + string.numbers + allowable_nonalphnum_characters):
					raise "UsersError", "A username must contain only letters, numbers, or these symbols: " + allowable_nonalphnum_characters
			
			# Check data type for user's password hash
			if type(user[1]) != str:
				raise "UsersError", "A user's password hash must be a string!"
				
			# Check data types for groups
			if type(user[2]) != tuple and (user[2] != None):
				raise "UsersError", "A user's groups must be a tuple or None for no groups!"
			for group in user[2]:
				if type(group) != str:
					raise "UsersError", "A user's group data must be a string!"
					
			# Check data type for user's shell
			if type(user[3]) != str and (user[3] != None):
				raise "UsersError", "The path to a user's shell must be a string or None for '/bin/bash'!"
				
			# Check data type for user's home dir
			if type(user[4]) != str and (user[4] != None):
				raise "UsersError", "A user's home directory must be a string or None for '/home/username'!"
			
			# Check data type for user's ID
			if (type(user[5]) != int) and (user[5] != None):
				raise "UsersError", "A user's ID must be an integer or None for next available UID!"
			
			# Check data type for user's comment
			if type(user[6]) != str and (user[6] != None):
				raise "UsersError", "A user's comment must be a string or None for no comment!"
		
		self._users = users

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

	def get_custom_stage3_tarball_uri(self):
		"returns custom_stage3_tarball_uri"
		return self._custom_stage3_tarball_uri

	def set_custom_stage3_tarball_uri(self, custom_stage3_tarball_uri):
		"custom_stage3_tarball_uri is a string that is the full path to your own custom stage3 tarball. (ie. '/path/to/mytarball.tar.bz2')"

		# Check type
		if type(custom_stage3_tarball_uri) != str:
			raise "CustomStage3TarballURIError", "Must be a string!"

		# Check validity
		if not GLIUtility._is_uri(kernel_config_uri):
			raise "CustomStage3TarballURIError", "Invalid URI!"
		
		self._custom_stage3_tarball_uri = custom_stage3_tarball_uri

	def get_install_stage(self):
		"returns install_stage"
		return self._install_stage

	def set_install_stage(self, install_stage):
		"install_stage is a integer to define which stage install to use.  Appropriate stages are 1-3."
		
		# Check type
		if type(install_stage) != int:
			raise "InstallStageError", "Must be an integer!"
		
		# Check for stage bounds
		if 0 < install_stage < 4:
			self._install_stage = install_stage
		else:
			raise "InstallStageError", "install_stage must be 1-3!"

	def get_portage_tree_sync(self):
		"returns portage_tree_sync"
		return self._portage_tree_sync

	def set_portage_tree_sync(self, portage_tree_sync):
		"portage_tree_sync is a bool to determine whether or not to run 'emerge sync' to get the latest portage tree."
		
		# Check type
		if type(portage_tree_sync) != bool:
			raise "PortageTreeSyncError", "Must be a bool!"
			
		self._portage_tree_sync = portage_tree_sync

	def get_portage_tree_snapshot_uri(self):
		"returns portage_tree_snapshot_uri"
		return self._portage_tree_snapshot_uri

	def set_portage_tree_snapshot_uri(self, portage_tree_snapshot_uri):
		"portage_tree_snapshot_uri is a string defining the path to a portage tree snapshot. (ie. 'file:///mnt/cdrom/snapshots/portage-*.tar.bz2')"
		
		# Check type
		if type(portage_tree_snapshot_uri) != str:
			raise "PortageTreeSnapshotURIError", "Must be a string!"

		# Check validity
		if not GLIUtility._is_uri(portage_tree_snapshot_uri):
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
			if GLIUtility._is_device(device):
			
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
			elif GLIUtility._is_ip(device) or GLIUtility._is_hostname(device):
			
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
		
	def set_network_interfaces(self, network_interfaces):
		"""
		Sets a dictionary of information for the available network_interfaces:
		{ <eth_device> : ( <pre-install device info (tuple/None)>, <post-install device info (tuple/None)>, <load at boot (bool)> ) }

		<eth_device> is a string with the device name, ie. 'eth0'
		If you desire DHCP, set <pre/post-install device info> to None.
		If you desire a static ip, set <pre/post-install device info> to a tuple as defined below:
		( <ip address>, <broadcast>, <netmask>, <gateway>, <alias (tuple)> )
		
		If you do not desire a gateway, set <gateway> to None.
		If you do not desire an alias, set <alias> to None.
		Otherwise, <alias> is a tuple of tuples containing alias info in the following format:
		( ( <alias ip>, <alias broadcast>, <alias netmask> ), ( <alias ip>, <alias broadcast>, <alias netmask> ), etc. )
		
		<alias ip>, <alias broadcast> and <alias netmask> MUST be defined for each alias!
		
		An <ip address> (or broadcast, netmask, etc...) is defined as a string containing the ip address (ie. "192.168.1.2")
		"""
		
		# Check type
		if type(network_interfaces) != dict:
			raise "NetworkInterfacesError", "Must be a dictionary!"
		
		for device in network_interfaces:

			# Split device into type and number
			digit_found = False
			for i in range(len(device)):
				if device[i] in string.digits:
					digit_found = True
					device_type = device[:i]
			
			
			# If the device is only letters or has the wrong proportion of letters and numbers
			# then it is not a valid device
			if (not digit_found) or (5 > i > 2):
				raise "NetworkInterfacesError", "Improper device name!"
			
			# For 'eth' type devices:
			if device_type == "eth":
			
				# Do the same for both pre and post tuples
				for i in range(2):
				
					# If the user does not desire DHCP, then validate each ip address provided
					if network_interfaces[device][i] != None:
						if not GLIUtility._is_ip(network_interfaces[device][i][0]):
							raise "NetworkInterfacesError", "The ip address you specified for " + device + " is not valid!"
						if not GLIUtility._is_ip(network_interfaces[device][i][1]):
							raise "NetworkInterfacesError", "The broadcast address you specified for " + device + " is not valid!"
						if not GLIUtility._is_ip(network_interfaces[device][i][2]):
							raise "NetworkInterfacesError", "The netmask address you specified for " + device + " is not valid!"
						
						# If gateway is set to none, check the validity of the ip
						if (network_interfaces[device][i][3] != None) and (not GLIUtility._is_ip(network_interfaces[device][i][3])):
							raise "NetworkInterfacesError", "The gateway address you specified for " + device + " is not valid!"
							
						# Check the validity of aliases if they exist
						if (network_interfaces[device][i][4] != None):
							
							# Type must be tuple
							if type(network_interfaces[device][i][4]) != tuple:
								raise "NetworkInterfacesError", "Improper type for network aliases (device: " + device + "), must be tuple!"
							
							# Tuple must contain at least 1 alias tuple
							if not len(network_interfaces[device][i][4]) > 0:
								raise "NetworkInterfacesError", "Aliases must contain at least one alias (device: " + device + ")!"
								
							# 
							for alias in network_interfaces[device][i][4]:
								
								# Alias must be a tuple
								if type(alias) != tuple:
									raise "NetworkInterfacesError", "Improper type for network alias (device: " + device + "), must be tuple!"
									
								# Alias must have a length of 3
								if len(alias) != 3:
									raise "NetworkInterfacesError", "Alias must have ip address, netmask and broadcast defined (device: " + device + ")!"
								
								# Alias must have an ip address, netmask, and broadcast defined
								if not GLIUtility._is_ip(alias[0]):
									raise "NetworkInterfacesError", "Invalid ip address for alias (device: " + device + ")!"
								if not GLIUtility._is_ip(alias[1]):
									raise "NetworkInterfacesError", "Invalid broadcast address for alias (device: " + device + ")!"
								if not GLIUtility._is_ip(alias[2]):
									raise "NetworkInterfacesError", "Invalid netmask address for alias (device: " + device + ")!"
			
			# Other device types
			else:
				raise "NetworkInterfacesError", "Invalid or unimplimented device type (" + device_type + ")!"
				
		# Set network_interfaces
		self._network_interfaces = network_interfaces
