"""
Gentoo Linux Installer

$Id: GLI.py,v 1.6 2004/02/19 18:23:01 npmccallum Exp $
Copyright 2004 Gentoo Technologies Inc.

The GLI module contains all classes used in the Gentoo Linux Installer (or GLI).
"""

import string
import xml.sax
import os

class InstallProfile(xml.sax.ContentHandler):
	"""
	An object representation of a profile.

	InstallProfile is an object representation of a parsed installation
	profile file.
	"""

	# Configuration information - profile data
	_cron_daemon = ""
	_logging_daemon = ""
	_boot_loader_mbr = ""
	_boot_loader = ""
	_kernel_modules = []
	_kernel_config = ""
	_kernel_initrd = ""
	_kernel_bootsplash = ""
	_kernel_source = ""
	_users = []
	_root_pass_hash = ""
	_time_zone = ""
	_custom_stage3_tarball = ""
	_install_stage = ""
	_portage_tree_sync = ""
	_portage_tree_snapshot = ""
	_domainname = ""
	_hostname = ""
	_nisdomainname = ""
	_partition_tables = {}


	# Internal SAX state info
	_xml_elements = [];
	_xml_current_data = ""
	_xml_current_attr = None

	def __init__(self):
		pass
		
	def _is_ip(self, ip):
		"Check to see if a string is a valid ip. Returns bool."
		
		# Make sure it is a string
		if type(ip) != str:
			return False
		
		# Make sure there are only 4 elements when split by '.'s.
		if len(ip.split(".")) != 4:
			return False
		
		# Make sure each element is a number within the propper range
		for number in ip.split("."):
			try:
				int(number)
			except:
				return False
				
			if int(number) > 255:
				return False
				
			if int(number) < 0:
				return False
		
		return True
		
	def _is_device(self, path):
		"Check to see if the string passed is a valid device. Returns bool."
		
		# Make sure the string starts with /dev/
		if path[0:5] != '/dev/':
			return False
			
		# Check to make sure the device exists
		return os.access(path, os.F_OK)
		
	def _is_hostname(self, hostname):
		"Check to see if the string is a valid hostname. Returns bool."
		
		# These are the characters that are not letters or numbers
		# but are still allowed to be in a hostname.  Any others?
		# I am allowing '.' for FQHNs.
		non_alphanum_chars = '-_.'
		
		# Make sure that each 
		for letter in hostname:
			if letter in string.letters or letter in string.digits:
				continue
			elif letter in non_alphanum_chars:
				continue
			else:
				return False
				
		return True

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
			self.set_cron_daemon(self._xml_current_data)
		elif path == 'gli-profile/logging-daemon':
			self.set_logging_daemon(self._xml_current_data)
		elif path == 'gli-profile/boot-loader_mbr':
			self.set_boot_loader_mbr(self._xml_current_data)
		elif path == 'gli-profile/boot-loader':
			self.set_boot_loader(self._xml_current_data)
		elif path == 'gli-profile/kernel-modules/module':
			self.get_kernel_modules().append(self._xml_current_data)
		elif path == 'gli-profile/kernel-config':
			self.set_kernel_config(self._xml_current_data)
		elif path == 'gli-profile/kernel-initrd':
			self.set_kernel_initrd(self._xml_current_data)
		elif path == 'gli-profile/kernel-bootsplash':
			self.set_kernel_bootsplash(self._xml_current_data)
		elif path == 'gli-profile/kernel-source':
			self.set_kernel_source(self._xml_current_data)
		elif path == 'gli-profile/users':
			self.get_users().append(self._xml_current_data)
		elif path == 'gli-profile/root-pass-hash':
			self.set_root_pass_hash(self._xml_current_data)
		elif path == 'gli-profile/time-zone':
			self.set_time_zone(self._xml_current_data)
		elif path == 'gli-profile/custom-stage3-tarball':
			self.set_custom_stage3_tarball(self._xml_current_data)
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

		self._xml_current_data += data

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

	def get_cron_daemon(self):
		"returns cron_daemon"
		return self._cron_daemon

	def set_cron_daemon(self, cron_daemon):
		"cron_daemon is a string to determine which cron daemon to install and configure (ie. 'vixie-cron')"
		self._cron_daemon = cron_daemon

	def get_logging_daemon(self):
		"returns logging_daemon"
		return self._logging_daemon

	def set_logging_daemon(self, loggin_daemon):
		"logging_daemon is a string to determine which logging daemon to install and configure (ie. 'sysklogd')"
		self._logging_daemon = logging_daemon

	def get_boot_loader_mbr(self):
		"returns boot_loader_mbr"
		return self._boot_loader_mbr

	def set_boot_loader_mbr(self, boot_loader_mbr):
		"boot_loader_mbr is a bool to decide whether or not to install the boot loader to the MBR. True installs boot loader to MBR.  False installs boot loader to the boot or root partition."
		self._boot_loader_mbr = boot_loader_mbr

	def get_boot_loader(self):
		"returns boot_loader"
		return self._boot_loader

	def set_boot_loader(self, boot_loader):
		"boot_loader is a string to decide which boot loader to install. (ie. 'grub')"
		self._boot_loader = boot_loader

	def get_kernel_modules(self):
		"returns kernel_modules"
		return self._kernel_modules

	def set_kernel_modules(self, kernel_modules):
		"kernel_modules is a list of strings containing names of modules to automatically load at boot time. (ie. '( 'ide-scsi', )')"
		self._kernel_modules = kernel_modules

	def get_kernel_config(self):
		"returns kernel_config"
		return self._kernel_config

	def set_kernel_config(self, kernel_config):
		"kernel_config is a string that is the path to the kernel config file you wish to use.  Can also be a http:// or ftp:// path."
		self._kernel_config = kernel_config

	def get_kernel_initrd(self):
		"returns kernel_initrd"
		return self._kernel_initrd

	def set_kernel_initrd(self, kernel_initrd):
		"kernel_initrd is a bool to determine whether or not to build an initrd kernel.  False builds a non-initrd kernel. (overwritten by kernel_bootsplash; needs genkernel non-initrd support not yet present)"
		self._kernel_initrd = kernel_initrd

	def get_kernel_bootsplash(self):
		"returns kernel_bootsplash"
		return self._kernel_bootsplash

	def set_kernel_bootsplash(self, kernel_bootsplash):
		"kernel_bootsplash is a bool to determine whether or not to install bootsplash into the kernel.  True builds in bootsplash support to the initrd.  WARNING: kernel_source must contain a kernel with bootsplash support or the bootsplash will not appear.  If you set this to true, it will build an initrd kernel even if you chose false for kernel_initrd!"
		self._kernel_bootsplash = kernel_bootsplash

	def get_kernel_source(self):
		"returns kernel_source"
		return self._kernel_source

	def set_kernel_source(self, kernel_source):
		"kernel_source is a string to define which kernel source to use.  (ie. 'gentoo-sources')"
		self._kernel_source = kernel_source

	def get_users(self):
		"returns users"
		return self._users

	def set_users(self, users):
		"users is a list of users.  A 'user' is defined as a tuple with the following format: ( 'user_name', 'user_pass_hash', 'user_groups', 'users_shell', 'users_homedir', uid, 'users_comment' ). Therefore, a user is a tuple embeded in a list containing all users."
		self._users = users

	def get_root_pass_hash(self):
		"returns root_pass_hash"
		return self._root_pass_hash

	def set_root_pass_hash(self, root_pass_hash):
		"root_pass_hash is a string containing an md5 password hash to be assinged as the password for the root user."
		self._root_pass_hash = root_pass_hash

	def get_time_zone(self):
		"returns time_zone"
		return self._time_zone

	def set_time_zone(self, time_zone):
		"time_zone is a string defining the time zone to use.  Time zones are found in /usr/share/zoneinfo/.  Syntax is 'UTC' or 'US/Eastern'."
		self._time_zone = time_zone

	def get_custom_stage3_tarball(self):
		"returns custom_stage3_tarball"
		return self._custom_stage3_tarball

	def set_custom_stage3_tarball(self, custom_stage3_tarball):
		"custom_stage3_tarball is a string that is the full path to your own custom stage3 tarball. (ie. '/path/to/mytarball.tar.bz2')"
		self._custom_stage3_tarball = custom_stage3_tarball

	def get_install_stage(self):
		"returns install_stage"
		return self._install_stage

	def set_install_stage(self, install_stage):
		"install_stage is a integer to define which stage install to use.  Appropriate stages are 1-3."
		if 0 < install_stage < 4:
			self._install_stage = install_stage
		else:
			# We should probably raise some kind of exception here...
			pass

	def get_portage_tree_sync(self):
		"returns portage_tree_sync"
		return self._portage_tree_sync

	def set_portage_tree_sync(self, portage_tree_sync):
		"portage_tree_sync is a bool to determine whether or not to run 'emerge sync' to get the latest portage tree."
		self._portage_tree_sync = portage_tree_sync

	def get_portage_tree_snapshot(self):
		"returns portage_tree_snapshot"
		return self._portage_tree_snapshot

	def set_portage_tree_snapshot(self, portage_tree_snapshot):
		"portage_tree_snapshot is a string defining the path to a portage tree snapshot. (ie. '/mnt/cdrom/snapshots/portage-*.tar.bz2')"
		self._portage_tree_snapshot = portage_tree_snapshot

	def get_domainname(self):
		"returns domainname"
		return self._domainname

	def set_domainname(self, domainname):
		"domainname is a string containing the domainname for the new system. (ie. 'mydomain.com'; NOT FQDN)"
		self._domainname = domainname

	def get_hostname(self):
		"returns hostname"
		return self._hostname

	def set_hostname(self, hostname):
		"hostname is a string containing the hostname for the new system. (ie. 'myhost'; NOT 'myhost.mydomain.com')"
		self._hostname = hostname

	def get_nisdomainname(self):
		"returns nisdomainname"
		return self._nisdomainname

	def set_nisdomainname(self, nisdomainname):
		"nisdomainname is a string containing the NIS domainname for the new system."
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
			if self._is_device(device):
			
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
					if minor < 1
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
			elif self._is_ip(device) or self._is_hostname(device):
			
					# Make sure that only the mount point is set
					if type(partition_tables[device]) != str:
						raise "ParitionTableError", "Invalid mount point for nfs mount (device: " + device + ")!"
						
			# If the device is not a local or remote device, then it is invalid
			else:
				raise "PartitionTableError", "The device you specified (" + device + ") is not valid!"

		# If all the tests clear, then set the variable
		self._partition_tables = partition_tables
