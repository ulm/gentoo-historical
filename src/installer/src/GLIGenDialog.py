import dialog, platform, string, os, glob, copy, re
import GLIInstallProfile
import GLIClientConfiguration
import GLIStorageDevice
import GLIUtility
import gettext
_ = gettext.gettext
#This is a parent class to centralize the code between UserGenCC and UserGenIP

class GLIGen(object):
	def __init__(self):
		self._d = dialog.Dialog()
		self._DLG_OK = 0
		self._DLG_YES = 0
		self._DLG_CANCEL = 1
		self._DLG_NO = 1
		self._DLG_ESC = 2
		self._DLG_ERROR = 3
		self._DLG_EXTRA = 4
		self._DLG_HELP = 5
	
	def _dmenu_list_to_choices(self, list):
		choices = []
		for i in range(0, len(list)):
			choices.append((str(i + 1), list[i]))

		return choices
		
	def client_profile(self):
		return self._client_profile
	
	def install_profile(self):
		return self._install_profile

#This class will generate a client config and return it as a xml string
class GLIGenCF(GLIGen):
	def __init__(self, client_profile, local_install=True, advanced_mode=True):
		GLIGen.__init__(self)
		self._client_profile = client_profile
		self.local_install = local_install
		self.advanced_mode = advanced_mode
		
	def serialize(self):
		return self._client_profile.serialize()
	#-----------------------------------------------
	#Functions for generating a client configuration
	#-----------------------------------------------	
	def set_arch_template(self):
		subarches = { 'i386': 'x86', 'i486': 'x86', 'i586': 'x86', 'i686': 'x86', 'x86_64': 'amd64', 'parisc': 'hppa' }
		arch = platform.machine()
		if arch in subarches: 
			arch = subarches[arch]
		if self.local_install:
			try:
				self._client_profile.set_architecture_template(None, arch, None)
			except:
				self._d.msgbox(_(u"Error!  Undefined architecture template specified or found on the current machine"))
		else:
			template_choices = ["x86", "amd64", "sparc", "alpha", "hppa", "ppc"]
			string = _(u"Please select the architecture of the computer that gentoo will be installed on.  For pentium and AMD 32-bit processors, choose x86.  If you don't know your architecture, you should consider another Linux distribution.")
			code, menuitem = self._d.menu(string, choices=self._dmenu_list_to_choices(template_choices), default_item=str(template_choices.index(arch)+1), height=20)
			if code == self._DLG_OK:
				menuitem = template_choices[int(menuitem)-1]
				try:
					self._client_profile.set_architecture_template(None, menuitem, None)
				except: 
					self._d.msgbox(_(u"Error!  Undefined architecture template specified or found on the current machine"))
		
	def set_logfile(self):
		#If not advanced, the default will suffice.
		if self.advanced_mode:
			string = _(u"""
The installer logs all important events during the install process to a logfile for debugging purposes.
The file gets copied to the new system once the install is complete.
Enter the desired filename and path for the install log (the default is recommended):""")
			initval = self._client_profile.get_log_file()
			code, logfile = self._d.inputbox(string, init=initval, width=60, height=15)
			if code == self._DLG_OK:
			
				self._client_profile.set_log_file(None, logfile, None)

	def set_root_mount_point(self):
		#If not advanced, the default will suffice.
		if self.advanced_mode:
			string = _(u"Enter the mount point to be used to mount the partition(s) where the new system will be installed.  The default is /mnt/gentoo and is greatly recommended, but any mount point will do.")	
			initval = self._client_profile.get_root_mount_point()
			code, rootmountpoint = self._d.inputbox(string, init=initval, width=60, height=11)
			if code == self._DLG_OK: 
				self._client_profile.set_root_mount_point(None, rootmountpoint, None)

	def set_client_networking(self):
		if GLIUtility.ping("www.gentoo.org") and not self.advanced_mode:	#If an active connection exists, ignore this step if standard mode
			return
		if self.local_install:
			device_list = GLIUtility.get_eth_devices()
		else:
			device_list = []
		choice_list = []
		for device in device_list:
			choice_list.append((device, GLIUtility.get_interface_realname(device)))
		choice_list.append(("Other","Type your own."))
		string1 = _(u"In order to complete most installs, an active Internet connection is required.  Listed are the network devices already detected.  In this step you will need to setup one network connection for GLI to use to connect to the Internet.  If your desired device does not show up in the list, you can select Other and input the device name manually.")
		code, interface = self._d.menu(string1, width=75, height=20, choices=choice_list)
		if code != self._DLG_OK: 
			return
		if interface == "Other":
			code, interface = self._d.inputbox("Enter the interface (NIC) you would like to use for installation (e.g. eth0):")
			if code != self._DLG_OK: 
				return
		
		#Not sure if I can get rid of these yet.
		#network_type = ""
		#ip_address = ""
		#broadcast = ""
		#netmask = ""
		#gateway = ""
		dhcp_options = ""
		
		#Change the Yes/No buttons to new labels for this question.
		d.add_persistent_args(["--yes-label", _(u"DHCP")])
		d.add_persistent_args(["--no-label", _(u"Static IP/Manual")])
		string2 = _(u"To setup your network interface, you can either use DHCP if enabled, or manually enter your network information.\n  DHCP (Dynamic Host Configuration Protocol) makes it possible to automatically receive networking information (IP address, netmask, broadcast address, gateway, nameservers etc.). This only works if you have a DHCP server in your network (or if your provider provides a DHCP service).  If you do not, you must enter the information manually.  Please select your networking configuration method:")
		if d.yesno(string2) == self._DLG_YES: #DHCP
			network_type = 'dhcp'
			code, dhcp_options = self._d.inputbox(_(u"If you have any additional DHCP options to pass, type them here in a space-separated list.  If you have none, just press Enter."))
		else:
			network_type = 'static'
			code, data = self._d.form('Enter your networking information: (See Chapter 3 of the Handbook for more information)  Your broadcast address is probably your IP address with 255 as the last tuple.  Do not press Enter until all fields are complete!', (('Enter your IP address:', 15),('Enter your Broadcast address:', 15),('Enter your Netmask:',15,'255.255.255.0'),('Enter your default gateway:',15), ('Enter a DNS server:',15,'128.118.25.3')))
			(ip_address, broadcast, netmask, gateway, dnsservers) = data.split()
			if code != self._DLG_OK: 
				return
		#Set the info now that it's all gathered.
		try:
			self._client_profile.set_network_type(None, network_type, None)
			self._client_profile.set_network_interface(None, interface, None)
			if not network_type == 'dhcp':
				self._client_profile.set_network_ip(None, ip_address, None)
				self._client_profile.set_network_broadcast(None, broadcast, None)
				self._client_profile.set_network_netmask(None, netmask, None)
				self._client_profile.set_network_gateway(None, gateway, None)
				self._client_profile.set_dns_servers(None, dnsservers, None)
			else:
				if dhcp_options:
					self._client_profile.set_network_dhcp_options(None, dhcp_options, None)
		except: 
			self._d.msgbox("ERROR! Could not set networking information!")

	def set_enable_ssh(self):
		if self.advanced_mode:
			if self._d.yesno(_(u"Do you want SSH enabled during the install?  This will allow you to login remotely during the installation process.  If choosing Yes, be sure you select a new LIVECD root password!"), width=60) == self._DLG_YES:
				self._client_profile.set_enable_ssh(None, True, None)
			else:
				self._client_profile.set_enable_ssh(None, False, None)

	def set_livecd_password(self):
		# The root password will be set here only if in advanced mode.  Otherwise it is auto-scrambled.
		if self.advanced_mode:
			match = False;
			while not match:
				string = _(u"""
If you want to be able to login to your machine from another console during the installation,
you will want to enter a new root password for the LIVECD.
Note that this can be different from your new system's root password.
Presss Enter twice to skip this step.
Enter the new LIVECD root password:	""")
				code, passwd1 = self._d.passwordbox(string, width=60, height=16)
				if code != self._DLG_OK: 
					return
				code, passwd2 = self._d.passwordbox(_(u"Enter the new LIVECD root password again to verify:"))
				if code != self._DLG_OK: 
					return
				if passwd1 != passwd2:
					self._d.msgbox(_(u"The passwords do not match.  Please try again."))
					return
				else:
					match = True;
					if passwd1 != "":  #don't want to hash an empty password.
						try:
							self._client_profile.set_root_passwd(None, GLIUtility.hash_password(passwd1), None)
						except:
							d.msgbox("ERROR! Could not set the root password on the LiveCD!")
						self._d.msgbox(_(u"Password saved.  Press Enter to continue."))
						
	def set_client_kernel_modules(self):
		if self.advanced_mode:
			status, output = GLIUtility.spawn("lsmod", return_output=True)
			string1 = _(u"Here is a list of modules currently loaded on your machine.\n  Please look through and see if any modules are missing\n that you would like loaded.\n\n")
			self._d.add_persistent_args(["--exit-label", "Continue"])
			self._d.scrollbox(string1+output, height=20, width=70, title="Loaded Modules")
			string2 = _(u"\nIf you have additional modules you would like loaded before the installation begins (ex. a network driver), enter them in a space-separated list.")
			code, kernel_modules_list = self._d.inputbox(string2, init="", width=60, height=12)
			if code == self._DLG_OK:
				try:
					self._client_profile.set_kernel_modules(None, kernel_modules_list, None)
				except:
					d.msgbox("ERROR! Could not set the list of kernel modules!")

	def save_client_profile(self, xmlfilename="", askforfilename=True):
		code = 0
		filename = xmlfilename
		if askforfilename:
			code, filename = self._d.inputbox(_(u"Enter a filename for the XML file"), init=xmlfilename)
			if code != self._DLG_OK: 
				return
		if GLIUtility.is_file(filename):
			if not self._d.yesno("The file " + filename + " already exists. Do you want to overwrite it?") == self._DLG_YES:
				return
		configuration = open(filename ,"w")
		configuration.write(self._client_profile.serialize())
		configuration.close()

class GLIGenIP(GLIGen):
	def __init__(self, client_profile, install_profile, local_install=True, advanced_mode=True):
		GLIGen.__init__(self)
		self._client_profile = client_profile
		self._install_profile = install_profile
		self.local_install = local_install
		self.advanced_mode = advanced_mode
		self._fn = (
			{ 'text': "Partitioning", 'fn': self._set_partitions },
			{ 'text': "Network mounts", 'fn': self._set_network_mounts },
			{ 'text': "Install Stage", 'fn': self._set_install_stage },
			{ 'text': "Portage Tree", 'fn': self._set_portage_tree },
			{ 'text': "make.conf", 'fn': self._set_make_conf },
			{ 'text': "Kernel", 'fn': self._set_kernel },
			{ 'text': "Bootloader", 'fn': self._set_boot_loader },
			{ 'text': "Timezone", 'fn': self._set_timezone },
			{ 'text': "Networking", 'fn': self._set_networking },
			{ 'text': "Cron daemon", 'fn': self._set_cron_daemon },
			{ 'text': "Logging daemon", 'fn': self._set_logger },
			{ 'text': "Extra packages", 'fn': self._set_extra_packages },
			{ 'text': "Services", 'fn': self._set_services },
			{ 'text': "rc.conf", 'fn': self._set_rc_conf },
			{ 'text': "Root password", 'fn': self._set_root_password },
			{ 'text': "Additional Users", 'fn': self._set_additional_users })
		self._menu_list = []
		for item in self._fn:
			self._menu_list.append(item['text'])
		current_item = 0
		while 1:
			code, menuitem = self._d.menu("Choose an option", choices=self._dmenu_list_to_choices(self._menu_list), default_item=str(current_item), height=23, menu_height=17, cancel="Done")
			if code != self._DLG_OK:
				break
			current_item = int(menuitem)
			menuitem = self._menu_list[int(menuitem)-1]
			for item in self._fn:
				if menuitem == item['text']:
					item['fn']()
					current_item += 1
	
	def serialize(self):
		return self._install_profile.serialize()
	#---------------------------------------
	#Functions to generate a install profile
	#---------------------------------------
	def _set_timezone(self):
	# This section will be for setting the timezone.
		zonepath = "/usr/share/zoneinfo"
		skiplist = ["zone.tab","iso3166.tab","posixrules"]
		while 1:
			tzlist = []
			for entry in os.listdir(zonepath):
				if entry not in skiplist:
					if os.path.isdir(zonepath + "/" + entry): entry += "/"
					tzlist.append(entry)
			tzlist.sort()
			string = _(u"Please select the timezone for the new installation.  Entries ending with a / can be selected to reveal a sub-list of more specific locations. For example, you can select America/ and then Chicago.")
			code, tznum = self._d.menu(string, choices=self._dmenu_list_to_choices(tzlist), height=20, cancel="Back")
			if code == self._DLG_OK:
				zonepath = os.path.join(zonepath,tzlist[int(tznum)-1])
				if tzlist[int(tznum)-1][-1:] != "/": 
					break
			else:
				if zonepath == "/usr/share/zoneinfo": 
					return
				slashloc = zonepath[:-1].rfind("/")
				zonepath = zonepath[:slashloc]
		try:
			self._install_profile.set_time_zone(None, zonepath[20:], None)
		except:
			self._d.msgbox(_(u"ERROR: Could not set that timezone!"))
	
	def _set_portage_tree(self):
	# This section will ask whether to sync the tree, whether to use a snapshot, etc.
		menulist = [("Sync", "Normal. Use emerge sync RECOMMENDED!"), ("Webrsync", "HTTP daily snapshot. Use when rsync is firewalled."), ("Snapshot", "Use a portage snapshot, either a local file or a URL"), ("None", "Extra cases such as if /usr/portage is an NFS mount")]
		code, portage_tree_sync = self._d.menu(_(u"Which method do you want to use to sync the portage tree for the installation?  If choosing a snapshot you will need to provide the URI for the snapshot if it is not on the livecd."),width=60, height=15, choices=menulist)
		if code != self._DLG_OK: 
			return
		#portage_tree_sync = menulist[int(portage_tree_sync)-1]
		#FIX ME when python 2.4 comes out.
		#if portage_tree_sync == "Normal  'emerge sync'": 
		#	self._install_profile.set_portage_tree_sync_type(None, "sync", None)
		#if portage_tree_sync == "Webrsync  (rsync is firewalled)": 
		#	self._install_profile.set_portage_tree_sync_type(None, "webrsync", None)
		#if portage_tree_sync == "None  (NFS mount)": 
		#	self._install_profile.set_portage_tree_sync_type(None, "none", None)
		#if portage_tree_sync == "Snapshot  (using a portage snapshot)":
		#	self._install_profile.set_portage_tree_sync_type(None, "snapshot", None)		
			self._install_profile.set_portage_tree_sync_type(None, portage_tree_sync.lower(), None)
			snapshot_options = ("Use Local", "Specify URI")
			code, snapshot_option = self._d.menu("Select a local portage snapshot or manually specify a location:", choices=self._dmenu_list_to_choices(snapshot_options))
			snapshot_option = snapshot_options[int(snapshot_option)-1]
			if snapshot_option == "Use Local":
				snapshot_dir = "/mnt/cdrom/snapshots"
				if os.path.isdir(snapshot_dir) and os.listdir(snapshot_dir):
					local_snapshots = glob.glob(snapshot_dir + "/portage*.bz2")
					if len(local_snapshots) == 1:
						snapshot = local_snapshots[0]
					else:
						local_snapshots.sort()
						code, snapshot = self._d.menu("Select a local portage snapshot:", choices=self._dmenu_list_to_choices(local_snapshots))
						if code != self._DLG_OK: return
						snapshot = local_snapshots[int(snapshot)-1]
				else:
					self._d.msgbox(_(u"There don't seem to be any local portage snapshots available.  Hit OK to manually specify a URI."))
					snapshot_option = "Specify URI"
			if snapshot_option != "Use Local":
				code, snapshot = self._d.inputbox(_(u"Enter portage tree snapshot URI"), init=self._install_profile.get_portage_tree_snapshot_uri())
			if code == self._DLG_OK:
				if snapshot: 
					if not GLIUtility.is_uri(snapshot, checklocal=self.local_install):
						self._d.msgbox(_(u"The specified URI is invalid.  It was not saved.  Please go back and try again."))
					else: 
						self._install_profile.set_portage_tree_snapshot_uri(None, snapshot, None)
			
				else: 
					self._d.msgbox(_(u"No URI was specified! Returning to default emerge sync."))
			#if d.yesno("The specified URI is invalid. Use it anyway?") == DLG_YES: install_profile.set_stage_tarball_uri(None, stage_tarball, None)

	def _set_partitions(self):
		string1 = _("""The first thing on the new system to setup is the partitoning on the new system.
You will first select a drive and then edit its partitions.
No changes will be saved until the end of the step.
No changes to your disk will be made until the installation.
NOTE: YOU MUST AT LEAST SELECT ONE PARTITION AS YOUR ROOT PARTITION "/"
If your drive is pre-partitioned, just select the mountpoints and make 
sure that the format option is set to FALSE or it will erase your data.
The installer does not yet support resizing of partitions (its not safe).
Please refer to the Gentoo Installation Handbook for more information
on partitioning and the various filesystem types available in Linux.""")
		self._d.msgbox(string1, height=17, width=78)
		devices = self._install_profile.get_partition_tables()
		drives = devices.keys()
		drives.sort()
		choice_list = []
		if not devices:
			tmp_drives = GLIStorageDevice.detect_devices()
			tmp_drives.sort()
			for drive in tmp_drives:
				devices[drive] = GLIStorageDevice.Device(drive)
				if self.local_install:
					devices[drive].set_partitions_from_disk()
				drives.append(drive)
				choice_list.append((drive, devices[drive].get_model()))
		#choice_list.append(("Other", "Type your own drive name))  # I DONT THINK GLISD CAN DO NONEXISTANT DRIVES
		while 1:
			code, drive_to_partition = self._d.menu(_(u"Which drive would you like to partition?\n Info provided: Type, mkfs Options, Mountpoint, Mountopts, Size in MB"), choices=choice_list, cancel="Save and Continue")
			if code != self._DLG_OK: break
			while 1:
				partitions = devices[drive_to_partition].get_partitions()
				partlist = devices[drive_to_partition].get_ordered_partition_list()
				tmpparts = devices[drive_to_partition].get_partitions()
				partsmenu = []
				for part in partlist:
					tmppart = tmpparts[part]
					entry = ""
					if tmppart.get_type() == "free":
						#partschoice = "New"
						entry = _(u" - Unallocated space (")
						if tmppart.is_logical():
							entry += _(u"logical, ")
						entry += str(tmppart.get_mb()) + "MB)"
					elif tmppart.get_type() == "extended":
						entry = str(int(tmppart.get_minor()))
						entry += _(u" - Extended Partition (") + str(tmppart.get_mb()) + "MB)"
					else:
						entry = str(int(tmppart.get_minor())) + " - "
						# Type: " + tmppart.get_type() + ", Mountpoint: " + tmppart.get_mountpoint() + ", Mountopts: " + tmppart.get_mountopts() + "("
						if tmppart.is_logical():
							entry += _(u"Logical (")
						else:
							entry += _(u"Primary (")
						entry += tmppart.get_type() + ", "
						entry += (tmppart.get_mkfsopts() or "none") + ", "
						entry += (tmppart.get_mountpoint() or "none") + ", "
						entry += (tmppart.get_mountopts() or "none") + ", "
						entry += str(tmppart.get_mb()) + "MB)"
					partsmenu.append(entry)
				code, part_to_edit = self._d.menu(_(u"Select a partition or unallocated space to edit"), width=70, choices=self._dmenu_list_to_choices(partsmenu), cancel="Back")
				if code != self._DLG_OK: break
				part_to_edit = partlist[int(part_to_edit)-1]
				tmppart = tmpparts[part_to_edit]
				if tmppart.get_type() == "free":
					# partition size first
					free_mb = tmppart.get_mb()
					code, new_mb = self._d.inputbox("Enter the size of the new partition in MB (max " + str(free_mb) + "MB).  If creating an extended partition input its entire size (not just the first logical size):", init=str(free_mb))
					if code != self._DLG_OK: continue
					if int(new_mb) > free_mb:
						self._d.msgbox("The size you entered (" + new_mb + "MB) is larger than the maximum of " + str(free_mb) + "MB")
						continue
					# partition type
					part_types = [("ext2", "Old, stable, but no journaling"), ("ext3", "ext2 with journaling and b-tree indexing (RECOMMENDED)"), ("linux-swap", "Swap partition for memory overhead"), ("fat32", "Windows filesystem format used in Win9X and XP"), ("ntfs", "Windows filesystem format used in Win2K and NT"),("jfs", "IBM's journaling filesystem.  stability unknown."), ("xfs", "Don't use this unless you know you need it."), ("reiserfs", "B*-tree based filesystem. great performance. Only V3 supported."), ("extended", "Create an extended partition containing other logical partitions"), ("other", "Something else we probably don't support.")]
					code, type = self._d.menu(_(u"Choose the filesystem type for this new partition."), height=20, width=77, choices=part_types)
					if code != self._DLG_OK: continue
										
					# 'other' partition type
					if type == "other":
						code, type = self._d.inputbox(_(u"Please enter the new partition's type:"))
					if code != self._DLG_OK: continue
					
					# now add it to the data structure
					devices[drive_to_partition].add_partition(part_to_edit, int(new_mb), 0, 0, type)
				else:
					while 1:
						tmppart = tmpparts[part_to_edit]
						tmptitle = drive_to_partition + str(part_to_edit) + " - "
						if tmppart.is_logical():
							tmptitle += "Logical ("
						else:
							tmptitle += "Primary ("
						tmptitle += tmppart.get_type() + ", "
						tmptitle += (tmppart.get_mkfsopts() or "none") + ", "
						tmptitle += (tmppart.get_mountpoint() or "none") + ", "
						tmptitle += (tmppart.get_mountopts() or "none") + ", "
						tmptitle += str(tmppart.get_mb()) + "MB)"
						menulist = ["Delete", "Mount Point", "Mount Options", "Format", "Extra mkfs.* Parameters"]
						code, part_action = self._d.menu(tmptitle, choices=self._dmenu_list_to_choices(menulist), cancel="Back")
						if code != self._DLG_OK: break
						part_action = menulist[int(part_action)-1]
						if part_action == "Delete":
							answer = (self._d.yesno("Are you sure you want to delete the partition " + drive_to_partition + str(part_to_edit) + "?") == self._DLG_YES)
							if answer == True:
								tmpdev = tmppart.get_device()
								tmpdev.remove_partition(part_to_edit)
								break
						elif part_action == "Mount Point":
							code, answer = self._d.inputbox("Enter a mountpoint for partition " + str(part_to_edit), init=tmppart.get_mountpoint())
							if code == self._DLG_OK: tmppart.set_mountpoint(answer)
						elif part_action == "Mount Options":
							code, answer = self._d.inputbox("Enter your mount options for partition " + str(part_to_edit), init=(tmppart.get_mountopts() or "defaults"))
							if code == self._DLG_OK: tmppart.set_mountopts(answer)
						elif part_action == "Format":
							code = d.yesno("Do you want to format this partition?")
							if code == self._DLG_YES: 
								tmppart.set_format(True)
							else:
								tmppart.set_format(False)
						elif part_action == "Extra mkfs.* Parameters":
							new_mkfsopts = tmppart.get_mkfsopts()
							# extra mkfs options
							if tmppart.get_type() != "extended":
								code, new_mkfsopts = self._d.inputbox("Extra mkfs parameters", init=new_mkfsopts)
								if code == self._DLG_OK: tmppart.set_mkfsopts(new_mkfsopts)							
		try:										
			self._install_profile.set_partition_tables(devices)
		except:
			self._d.msgbox(_(u"ERROR:  The partition tables could not be set correctly!"))

	def _set_network_mounts(self):
	# This is where any NFS mounts will be specified
		network_mounts = copy.deepcopy(self._install_profile.get_network_mounts())
		while 1:
			menulist = []
			for mount in network_mounts:
				menulist.append(mount['host'] + ":" + mount['export'])
			menulist.append("Add a new network mount")
			choices = self._dmenu_list_to_choices(menulist)
			code, menuitemidx = self._d.menu(_(u"If you have any network shares you would like to mount during the install and for your new system, define them here. Select a network mount to edit or add a new mount.  Currently GLI only supports NFS mounts."), choices=choices, cancel="Save and Continue")
			if code == self._DLG_CANCEL:
				try:
					self._install_profile.set_network_mounts(network_mounts)
				except:
					self._d.msgbox(_(u"ERROR: Could net set network mounts!"))
				break
			menuitem = menulist[int(menuitemidx)-1]
			if menuitem == "Add a new network mount":
				code, nfsmount = self._d.inputbox(_(u"Enter NFS mount or just enter the IP/hostname to search for available mounts"))
				if code != self._DLG_OK: 
					continue
				if not GLIUtility.is_nfs(nfsmount):
					if GLIUtility.is_ip(nfsmount) or GLIUtility.is_hostname(nfsmount):
						status, remotemounts = GLIUtility.spawn("/usr/sbin/showmount -e " + nfsmount + " 2>&1 | egrep '^/' | cut -d ' ' -f 1 && echo", return_output=True)
						if not len(remotemounts):
							self._d.msgbox(_(u"No NFS exports were detected on ") + nfsmount)
							continue
						for i in range(0, len(remotemounts)):
							remotemounts[i] = string.strip(remotemounts[i])
						code, nfsmount2 = self._d.menu("Select a NFS export", choices=self._dmenu_list_to_choices(remotemounts), cancel="Back")
						if code != self._DLG_OK: 
							continue
						nfsmount2 = remotemounts[int(nfsmount2)-1]
					else:
						self._d.msgbox("The address you entered, '" + nfsmount + "', is not a valid IP or hostname.  Please try again.")
						continue
				else:
					colon_location = nfsmount.find(':')
					menuitem = nfsmount
					nfsmount = menuitem[:colon_location]
					nfsmount2 = menuitem[colon_location+1:]
				for mount in network_mounts:
					if nfsmount == mount['host'] and nfsmount2 == mount['export']:
						self._d.msgbox("There is already an entry for " + nfsmount + ":" + nfsmount2 + ".")
						nfsmount = None
						break
				if nfsmount == None: 
					continue
				network_mounts.append({'export': nfsmount2, 'host': nfsmount, 'mountopts': '', 'mountpoint': '', 'type': 'nfs'})
				menuitem = nfsmount + ":" + nfsmount2
				menuitemidx = len(network_mounts)

			if menuitem.find(':') != -1:
				colon_location = menuitem.find(':')
				tmpmount = network_mounts[int(menuitemidx)-1]
				code, mountpoint = self._d.inputbox("Enter a mountpoint", init=tmpmount['mountpoint'])
				if code == self._DLG_OK: 
					tmpmount['mountpoint'] = mountpoint
				code, mountopts = self._d.inputbox("Enter mount options", init=tmpmount['mountopts'])
				if code == self._DLG_OK: 
					tmpmount['mountopts'] = mountopts
				network_mounts[int(menuitemidx)-1] = tmpmount

	def _set_make_conf(self):
	# This section will be for setting things like CFLAGS, ACCEPT_KEYWORDS, and USE
		make_conf = self._install_profile.get_make_conf()
		
		self._d.msgbox(_(u"""The installer will now gather information regarding the contents of /etc/make.conf
One of the unique (and best) features of Gentoo is the ability to
define flags (called USE flags) that define what components are 
compiled into applications.  For example, you can enable the alsa
flag and programs that have alsa capability will use it.  
The result is a finely tuned OS with no unnecessary components to
slow you down.
The installer divides USE flag selection into two screens, one for
global USE flags and one for local flags specific to each program.
		"""), width=73, height=16)
					
		#Second set the USE flags, this is a biggie.
		system_use_flags = GLIUtility.spawn("portageq envvar USE", return_output=True)[1].strip().split()
		use_flags = []
		use_local_flags = []
		use_desc = {}
		use_local_desc = {}
		f = open("/usr/portage/profiles/use.desc", "r")
		for line in f:
			line = line.strip()
			if not line or line.startswith("#"): continue
			dash_pos = line.find(" - ")
			if dash_pos == -1: continue
			flagname = line[:dash_pos] or line[dash_pos-1]
			desc = line[dash_pos+3:]
			use_desc[flagname] = desc
		f.close()

		f = open("/usr/portage/profiles/use.local.desc", "r")
		for line in f:
			line = line.strip()
			if not line or line.startswith("#"): continue
			dash_pos = line.find(" - ")
			if dash_pos == -1: continue
			colon_pos = line.find(":", 0, dash_pos)
			pkg = line[:colon_pos]
			flagname = line[colon_pos+1:dash_pos] or line[colon_pos+1]
			desc = "(" + pkg + ") " + line[dash_pos+3:]
			use_local_desc[flagname] = desc
		f.close()
		
		#populate the choices list
		sorted_use = use_desc.keys()
		sorted_use.sort()
		for flagname in sorted_use:
			use_flags.append((flagname, use_desc[flagname], int(flagname in system_use_flags)))
		#present the menu
		code, use_flags = self._d.checklist(_(u"Choose which *global* USE flags you want on the new system"), height=25, width=80,list_height=19, choices=use_flags)	
		
		#populate the chocies list
		sorted_use = use_local_desc.keys()
		sorted_use.sort()
		for flagname in sorted_use:
			use_local_flags.append((flagname, use_local_desc[flagname], int(flagname in system_use_flags)))
		#present the menu
		code, use_local_flags = self._d.checklist(_(u"Choose which *local* USE flags you want on the new system"), height=25, width=80,list_height=19, choices=use_local_flags)	
		temp_use = "-* "
		for flag in use_flags:
			temp_use += flag + " "
		for flag in use_local_flags:
			temp_use += flag + " "
		make_conf["USE"] = temp_use
		
		#Second, set the ACCEPT_KEYWORDS
		#Change the Yes/No buttons to new labels for this question.
		self._d.add_persistent_args(["--yes-label", _(u"Stable")])
		self._d.add_persistent_args(["--no-label", _(u"Unstable")])
		if self._d.yesno(_(u"Do you want to run the normal stable portage tree, or the bleeding edge unstable (i.e. ACCEPT_KEYWORDS=arch)?  If unsure select stable.  Stable is required for GRP installs.")) == self._DLG_YES:
			#Stable
			make_conf["ACCEPT_KEYWORDS"] = ""
		else:  #Unstable
			make_conf["ACCEPT_KEYWORDS"] = "~" + self._client_profile.get_architecture_template()
		#Third, misc. stuff.
		while 1:
			menulist = [("CFLAGS","Edit your C Flags and Optimization level"), ("CHOST", "Change the Host Setting"), ("MAKEOPTS", "Specify number of parallel makes (-j) to perform. (ex. CPUs+1)"), ("FEATURES", "Change portage functionality settings."), ("GENTOO_MIRRORS", "Specify mirrors to use for source retrieval."), ("SYNC", "Specify server used by rsync to sync the portage tree.")]
			code, menuitem = self._d.menu(_(u"For experienced users, the following /etc/make.conf variables can also be defined.  Choose a variable to edit or Done to continue."), choices=menulist, cancel="Done")
			if code != self._DLG_OK: 
				self._install_profile.set_make_conf(make_conf)
				break
			oldval = ""
			if make_conf.has_key(menuitem): 
				oldval = make_conf[menuitem]
			code, newval = self._d.inputbox("Enter new value for " + menuitem, init=oldval)
			if code == self._DLG_OK:
				make_conf[menuitem] = newval
				

	def _set_kernel(self):
	# This section will be for choosing kernel sources, choosing (and specifying) a custom config or genkernel, modules to load at startup, etc.
		kernel_sources = [("vanilla-sources", "The Unaltered Linux Kernel ver 2.6+ (safest)"), ("gentoo-sources", "Gentoo's optimized 2.6+ kernel. (less safe)"), ("hardened-sources", "Hardened sources for the 2.6 kernel tree"), ("grsec-sources","Vanilla sources with grsecurity patches"), ("livecd-kernel", "Use the current running kernel for the new system (fastest)"), ("Other", "Choose one of the other sources available.")]
		code, menuitem = self._d.menu(_(u"Choose which kernel sources to use for your system.  If using a previously-made kernel configuration, make sure the sources match the kernel used to create the configuration."), choices=kernel_sources)
		if code != self._DLG_OK: 
			return
		if menuitem == "Other":
			code, menuitem = self._d.inputbox(_(u"Please enter the desired kernel sources package name:"))
			if code != self._DLG_OK: return
		try:
			self._install_profile.set_kernel_source_pkg(None, menuitem, None)
		except:
			self._d.msgbox("ERROR! Could not set the kernel source package!")
		if not menuitem == "livecd-kernel":
			#Change the Yes/No buttons to new labels for this question.
			self._d.add_persistent_args(["--yes-label", _(u"Genkernel")])
			self._d.add_persistent_args(["--no-label", _(u"Traditional (requires config file!)")])
			string1 = _(u"There are currently two ways the installer can compile a kernel for your new system.  You can either provide a previously-made kernel configuration file and use the traditional kernel-compiling procedure (no initrd) or have genkernel automatically create your kernel for you (with initrd).  \n\n If you do not have a previously-made kernel configuration, YOU MUST CHOOSE Genkernel.  Choose which method you want to use.")
			if self._d.yesno(string1, width=70, height=13) == self._DLG_YES:   #Genkernel
				self._install_profile.set_kernel_build_method(None,"genkernel", None)
				#Change the Yes/No buttons back.
				self._d.add_persistent_args(["--yes-label", _(u"Yes")])
				self._d.add_persistent_args(["--no-label", _(u"No")])
				if self._d.yesno("Do you want the bootsplash screen to show up on bootup?") == self._DLG_YES:
					self._install_profile.set_kernel_bootsplash(None, True, None)
				else:
					self._install_profile.set_kernel_bootsplash(None, False, None)
			else: 	#Custom
				self._install_profile.set_kernel_build_method(None,"custom", None)
				
			code, custom_kernel_uri = self._d.inputbox(_(u"If you have a custom kernel configuration, enter its location (otherwise just press Enter to continue):"))
			if code == self._DLG_OK: 
				if custom_kernel_uri: 
					if not GLIUtility.is_uri(custom_kernel_uri, checklocal=self.local_install):
						self._d.msgbox(_(u"The specified URI is invalid.  It was not saved.  Please go back and try again."))
					else: 
						try:
							self._install_profile.set_kernel_config_uri(None, custom_kernel_uri, None)
						except:
							self._d.msgbox(_(u"ERROR! Could not set the kernel config URI!"))
				else: self._d.msgbox(_(u"No URI was specified!  Reverting to using genkernel"))
				
				

	def _set_install_stage(self):
	# The install stage and stage tarball will be selected here
		install_stages = (("1","Stage1 is used when you want to bootstrap and build the entire system from scratch."), ("2","Stage2 is used for building the entire system from a bootstrapped semi-compiled state."), ("3","Stage3 installation is a basic Gentoo Linux system that has been built for you (no compiling)."), ("3 + GRP", "A Stage3 install but using binary packages from the LiveCD whenever possible"))
		code, install_stage = self._d.menu("Which stage do you want to start at?", choices=install_stages, cancel="Back")
		if code == self._DLG_OK:
			if install_stage == "3 + GRP":
				install_stage = "3"
			try:			
				self._install_profile.set_grp_install(None, True, None)
				self._install_profile.set_install_stage(None, install_stage, None)
			except:
				self._d.msgbox("ERROR! Could not set install stage!")
		#Change the Yes/No buttons to new labels for this question.
		self._d.add_persistent_args(["--yes-label", _(u"Use Local")])
		self._d.add_persistent_args(["--no-label", _(u"Specify URI")])
		if self._d.yesno(_(u"Do you want to use a local tarball on the LiveCD (or other local location) or do you want to grab your stage tarball from the Internet?")) == self._DLG_YES:
			#Use Local				
			stages_dir = "/mnt/cdrom/stages"
			if os.path.isdir(stages_dir) and os.listdir(stages_dir):
				local_tarballs = glob.glob(stages_dir + "/stage" + install_stage + "*.bz2")
				local_tarballs.sort()
				code, stage_tarball = self._d.menu("Select a local tarball:", choices=self._dmenu_list_to_choices(local_tarballs))
				if code != self._DLG_OK: 
					return
				stage_tarball = local_tarballs[int(stage_tarball)-1]
				try:
					self._install_profile.set_stage_tarball_uri(None, stage_tarball, None)
				except:
					self._d.msgbox("ERROR: Could not set the stage tarball URI!")
				return
			else:
				self._d.msgbox("There don't seem to be any local tarballs available.  Hit OK to manually specify a URI.")
		
		#Specify URI
		subarches = { 'x86': ("x86", "i686", "pentium3", "pentium4", "athlon-xp"), 'hppa': ("hppa1.1", "hppa2.0"), 'ppc': ("g3", "g4", "g5", "ppc"), 'sparc': ("sparc32", "sparc64")}
		type_it_in = False
		stage_tarball = ""
		if GLIUtility.ping("www.gentoo.org"):  #Test for network connectivity
			mirrors = GLIUtility.list_mirrors()
			mirrornames = []
			mirrorurls = []
			for item in mirrors:
				mirrornames.append(item[1])
				mirrorurls.append(item[0])
			code, mirror = self._d.menu("Select a mirror to grab the tarball from or select Cancel to enter an URI manually.", choices=self._dmenu_list_to_choices(mirrornames), width=77, height=20)
			if code != self._DLG_OK:
				type_it_in = True
			else:
				mirror = mirrorurls[int(mirror)-1]
				arch = self._client_profile.get_architecture_template()
				subarches = GLIUtility.list_subarch_from_mirror(mirror,arch)
				code, subarch = self._d.menu("Select the sub-architecture that most closely matches your system (this changes the amount of optimization):", choices=self._dmenu_list_to_choices(subarches))
				if code != self._DLG_OK:
					type_it_in = True
				else:
					subarch = subarches[int(subarch)-1]	
					tarballs = GLIUtility.list_stage_tarballs_from_mirror(mirror, arch, subarch)
					code, stage_tarball = self._d.menu("Select your desired stage tarball:", choices=self._dmenu_list_to_choices(tarballs))
					if (code != self._DLG_OK):
						type_it_in = True
					else:
						stage_tarball = mirror + "/releases/" + arch + "/current/stages/" + subarch + tarballs[int(stage_tarball)-1]
		#get portageq envvar value of cflags and look for x86, i686,etc.
			#URL SYNTAX
			#http://gentoo.osuosl.org/releases/ARCHITECTURE/current/stages/SUB-ARCH/
		else:
			type_it_in = True
		if type_it_in:
			code, stage_tarball = self._d.inputbox("Specify the stage tarball URI or local file:", init=self._install_profile.get_stage_tarball_uri())
			if code != self._DLG_OK:
				return
		#If Doing a local install, check for valid file:/// uri
		if stage_tarball:
			if not GLIUtility.is_uri(stage_tarball, checklocal=self.local_install):
				self._d.msgbox("The specified URI is invalid.  It was not saved.  Please go back and try again.");
			else: self._install_profile.set_stage_tarball_uri(None, stage_tarball, None)
		else: self._d.msgbox("No URI was specified!")
			#if d.yesno("The specified URI is invalid. Use it anyway?") == DLG_YES: install_profile.set_stage_tarball_uri(None, stage_tarball, None)

	def _set_boot_loader(self):
		arch = self._client_profile.get_architecture_template()
		arch_loaders = { 'x86': ("grub","GRand Unified Bootloader, newer, RECOMMENDED"),("lilo","LInux LOader, older, traditional.(detects windows partitions)")} #FIXME ADD OTHER ARCHS
		boot_loaders = arch_loaders[arch]
		boot_loaders.append(("none", "Do not install a bootloader.  (System may be unbootable!)"))
		string1 = _(u"To boot successfully into your new Linux system, a bootloader will be needed.  If you already have a bootloader you want to use you can select None here.  The bootloader choices available are dependent on what GLI supports and what architecture your system is.  Choose a bootloader")
		code, menuitem = self._d.menu(string1, choices=boot_loaders)
		if code != self._DLG_OK: 
			return
		try:
			self._install_profile.set_boot_loader_pkg(None, menuitem, None)
		except:
			self._d.msgbox(_(u"ERROR! Could not set boot loader pkg! ")+menuitem)
		if menuitem != "none":
			#Reset the Yes/No labels.
			d.add_persistent_args(["--yes-label", "Yes"])
			d.add_persistent_args(["--no-label","No"])
			if self._d.yesno(_(u"Most bootloaders have the ability to install to either the Master Boot Record (MBR) or some other partition.  Most people will want their bootloader installed on the MBR for successful boots, but if you have special circumstances, you can have the bootloader installed to the /boot partition instead.  Do you want the boot loader installed in the MBR? (YES is RECOMMENDED)")) == self._DLG_YES:
				self._install_profile.set_boot_loader_mbr(None, True, None)
			else:
				self._install_profile.set_boot_loader_mbr(None, False, None)
		code, bootloader_kernel_args = self._d.inputbox(_(u"If you have any additional optional arguments you want to pass to the kernel at boot, type them here or just press Enter to continue:"))
		if code == self._DLG_OK:
			try:
				self._install_profile.set_bootloader_kernel_args(None, bootloader_kernel_args, None)
			except:
				self._d.msgbox(_(u"ERROR! Could not set bootloader kernel arguments! ")+bootloader_kernel_args)
	
	def _set_networking(self):
	# This section will be for setting up network interfaces, defining DNS servers, default routes/gateways, etc.
		interfaces = self._install_profile.get_network_interfaces()
		CC_iface = self._client_profile.get_network_interface()
		if CC_iface and (CC_iface not in interfaces):
			#The CC has a network config that's not already there.  Preload it.
			CC_net_type = self._client_profile.get_network_type()
			if CC_net_type == 'dhcp':
				try:
					interfaces[CC_iface] = ('dhcp', self._client_profile.get_network_dhcp_options(), None)
				except:
					pass
			else:
				try:
					interfaces[CC_iface] = (self._client_profile.get_network_ip(), self._client_profile.get_network_broadcast(), self._client_profile.get_network_netmask())
				except:
					pass
			
		while 1:
			menulist = ["Edit Interfaces", "DNS Servers", "Default Gateway", "Hostname", "Domain Name", "HTTP Proxy", "FTP Proxy", "RSYNC Proxy", "NIS Domain Name"]
			string = _(u"Here you will enter all of your networking information for the new system.  You can either choose a network interface to edit, add a network interface, delete an interface, or edit the miscellaneous options such as hostname and proxy servers.")
			if self.local_install:
				device_list = GLIUtility.get_eth_devices()
			else:
				device_list = []
			code, menuitem = self._d.menu(
			
			code, menuitem = self._d.menu("Choose an option", choices=self._dmenu_list_to_choices(menulist), cancel="Done")
			if code != self._DLG_OK: 
				break
			menuitem = menulist[int(menuitem)-1]
			if menuitem == "Edit Interfaces":
				while 1:
					interfaces = self._install_profile.get_network_interfaces()
					menu_list = interfaces.keys()
					menu_list.sort()
					menu_list.append("Add new interface")
					code, menuitem = self._d.menu("Select an interface", choices=self._dmenu_list_to_choices(menu_list), cancel="Back")
					if code != self._DLG_OK: 
						break
					menuitem = menu_list[int(menuitem)-1]
					newnic = None
					if menuitem == "Add new interface":
						code, newnic = self._d.inputbox("Enter name for new interface (eth0, ppp0, etc.)")
						if code != self._DLG_OK: 
							continue
						if newnic in interfaces:
							self._d.msgbox("An interface with the name is already defined.")
							continue
						interfaces[newnic] = ("", "", "")
						menuitem = newnic
					menuitem2 = ""
					menulist = ["Edit", "Rename", "Delete"]
					if newnic == None:
						menuitem2 = self._d.menu("What do you want to do with interface " + menuitem + "?", choices=self._dmenu_list_to_choices(menulist), cancel="Back")
						if code != self._DLG_OK: 
							continue
					else:
						menuitem2 = "1"
					menuitem2 = menulist[int(menuitem2)-1]
					if menuitem2 == "Edit":
						tmpnic = [interfaces[menuitem][0], interfaces[menuitem][1], interfaces[menuitem][2]]
						code, ip = self._d.inputbox("Enter an IP address for " + menuitem + " or 'dhcp' for DHCP", init=tmpnic[0])
						if code != self._DLG_OK: 
							continue
						tmpnic[0] = ip
						if ip == "dhcp" or ip == "DHCP":
							tmpnic[1] = ""
							tmpnic[2] = ""
						else:
							code, netmask = self._d.inputbox("Enter the netmask", init=tmpnic[2])
							if code == self._DLG_OK: tmpnic[2] = netmask
							code, broadcast = self._d.inputbox("Enter a broadcast", init=tmpnic[1])
							if code == self._DLG_OK: tmpnic[1] = broadcast
						interfaces[menuitem] = (tmpnic[0], tmpnic[1], tmpnic[2])
					elif menuitem2 == "Rename":
						self._d.msgbox("Not implimented yet")
					elif menuitem2 == "Delete":
						if self._d.yesno("Are you sure you want to remove the interface " + menuitem + "?") == self._DLG_YES:
							del interfaces[menuitem]
					self._install_profile.set_network_interfaces(interfaces)
			elif menuitem == "DNS Servers":
				code, dnsservers = self._d.inputbox("Enter a space-separated list of DNS servers")
				if code == self._DLG_OK: 
					install_profile.set_dns_servers(None, dnsservers, None)
				
			elif menuitem == "Default Gateway":
				while 1:
					interfaces = self._install_profile.get_network_interfaces()
					if not interfaces: 
						break
					menu_list = interfaces.keys()
					menu_list.sort()
					code, menuitem = self._d.menu("Which interface is the default gateway?", choices=self._dmenu_list_to_choices(menu_list), cancel="Back")
					if code != self._DLG_OK: 
						break
					menuitem = menu_list[int(menuitem)-1]
					code, ip = self._d.inputbox("Enter an IP address for " + menuitem , init=interfaces[menuitem][0])
					if code != self._DLG_OK: 
						continue
					self._install_profile.set_default_gateway(None, ip,{'interface': menuitem})
					break		
			elif menuitem == "Hostname":
				code, hostname = self._d.inputbox("Enter the desired hostname")
				if type(hostname) != str:
					self._d.msgbox("Incorrect hostname!  It must be a string.  Not saved.")
				if code == self._DLG_OK: 
					self._install_profile.set_hostname(None, hostname, None)
			elif menuitem == "Domain Name":
				code, domain = self._d.inputbox("Enter the desired domain name")
				if type(domain) != str:
					self._d.msgbox("Incorrect domain name!  It must be a string.  Not saved.")
				if code == self._DLG_OK: 
					self._install_profile.set_domainname(None, domain, None)
			elif menuitem == "HTTP Proxy":
				code, http_proxy = self._d.inputbox("Enter a HTTP Proxy if you have one.")
				if not GLIUtility.is_uri(http_proxy):
					self._d.msgbox("Incorrect HTTP Proxy! It must be a uri. Not saved.")
				if code == self._DLG_OK: 
					self._install_profile.set_http_proxy(None, http_proxy, None)
			elif menuitem == "FTP Proxy":
				code, ftp_proxy = self._d.inputbox("Enter a FTP Proxy if you have one.")
				if not GLIUtility.is_uri(ftp_proxy):
					self._d.msgbox("Incorrect FTP Proxy! It must be a uri. Not saved.")
				if code == self._DLG_OK: 
					self._install_profile.set_ftp_proxy(None, ftp_proxy, None)
			elif menuitem == "RSYNC Proxy":
				code, rsync_proxy = self._d.inputbox("Enter a RSYNC Proxy if you have one.")
				if not GLIUtility.is_uri(rsync_proxy):
					self._d.msgbox("Incorrect RSYNC Proxy! It must be a uri. Not saved.")
				if code == self._DLG_OK: 
					self._install_profile.set_rsync_proxy(None, rsync_proxy, None)
			elif menuitem == "NIS Domain Name":
				code, nisdomain = self._d.inputbox("Enter the desired NIS domain name (if you don't know what this is, don't enter one.)")
				if type(nisdomain) != str:
					self._d.msgbox("Incorrect NIS domain name!  It must be a string.  Not saved.")
				if code == self._DLG_OK: 
					self._install_profile.set_nisdomainname(None, nisdomain, None)

	def _set_cron_daemon(self):
		cron_daemons = (("vixie-cron", "Paul Vixie's cron daemon, fully featured, RECOMMENDED."), ("dcron","A cute little cron from Matt Dillon."), ("fcron", "A command scheduler with extended capabilities over cron and anacron"), ("None", "Don't use a cron daemon. (NOT Recommended!)"))
		string = _(u"A cron daemon executes scheduled commands. It is very handy if you need to execute some command regularly (for instance daily, weekly or monthly).  Gentoo offers three possible cron daemons: dcron, fcron and vixie-cron. Installing one of them is similar to installing a system logger. However, dcron and fcron require an extra configuration command, namely crontab /etc/crontab. If you don't know what to choose, use vixie-cron.  If doing a networkless install, choose vixie-cron.  Choose your cron daemon:")
		code, menuitem = d.menu(string, choices=cron_daemons)
		if code == self._DLG_OK:
			if menuitem == "None": 
				menuitem = ""
			self._install_profile.set_cron_daemon_pkg(None, menuitem, None)

	def _set_logger(self):
		loggers = (("syslog-ng", "An advanced system logger."), ("metalog", "A Highly-configurable system logger."), ("syslogkd", "The traditional set of system logging daemons."))
		string = _(u"Linux has an excellent history of logging capabilities -- if you want you can log everything that happens on your system in logfiles. This happens through the system logger. Gentoo offers several system loggers to choose from.  If you plan on using sysklogd or syslog-ng you might want to install logrotate afterwards as those system loggers don't provide any rotation mechanism for the log files.  Choose a system logger:")
		code, menuitem = self._d.menu("Choose a system logger", choices=loggers)
		if code == self._DLG_OK:
			self._install_profile.set_logging_daemon_pkg(None, menuitem, None)

	def _set_extra_packages(self):
		#d.msgbox("This section is for selecting extra packages (pcmcia-cs, rp-pppoe, xorg-x11, etc.) and setting them up")
		#file indexing (slocate)
		#logrotate
		code, install_packages = self._d.inputbox("Enter a space-separated list of extra packages to install on the system")
		if code == self._DLG_OK: 
			self._install_profile.set_install_packages(None, install_packages, None)
	
	def _set_rc_conf(self):
	# This section is for editing /etc/rc.conf
		rc_conf = self._install_profile.get_rc_conf()
		menulist = ["KEYMAP", "SET_WINDOWSKEYS", "EXTENDED_KEYMAPS", "CONSOLEFONT", "CONSOLETRANSLATION", "CLOCK", "EDITOR", "PROTOCOLS", "DISPLAYMANAGER", "XSESSION"]
		while 1:
			code, menuitem = self._d.menu("Choose a variable to edit", choices=self._dmenu_list_to_choices(menulist), cancel="Done")
			if code != self._DLG_OK: 
				break
			menuitem = menulist[int(menuitem)-1]
			oldval = ""
			if rc_conf.has_key(menuitem): 
				oldval = rc_conf[menuitem]
			code, newval = self._d.inputbox("Enter new value for " + menuitem, init=oldval)
			if code == self._DLG_OK:
				rc_conf[menuitem] = newval
				self._install_profile.set_rc_conf(rc_conf)

	def _set_root_password(self):
	# The root password will be set here
		while 1:
			code, passwd1 = self._d.passwordbox(_(u"Please enter your desired password for the root account.  (note it will not show the password.  Also do not try to use backspace.):"))
			if code != self._DLG_OK: 
				return
			code, passwd2 = self._d.passwordbox("Enter the new root password again for confirmation")
			if code != self._DLG_OK: 
				return
			if passwd1 != passwd2:
				self._d.msgbox("The passwords do not match.  Please try again or cancel.")
			else:
				try:
					self._install_profile.set_root_pass_hash(None, GLIUtility.hash_password(passwd1), None)
				except:
					self._d.msgbox(_(u"ERROR! Could not set the new system root password!"))
				self._d.msgbox(_(u"Password saved.  Press Enter to continue."))
				return

	def _set_additional_users(self):
	# This section will be for adding non-root users
		users = {}
		for user in self._install_profile.get_users():
			users[user[0]] = (user[0], user[1], user[2], user[3], user[4], user[5], user[6])
		while 1:
			menu_list = []
			for user in users:
				menu_list.append(user)
			menu_list.sort()
			menu_list.append("Add user")
			string1 = _(u"Working as root on a Unix/Linux system is dangerous and should be avoided as much as possible. Therefore it is strongly recommended to add a user for day-to-day use.  Choose a user to edit:")
			code, menuitem = self._d.menu(string1, choices=self._dmenu_list_to_choices(menu_list), cancel="Save and Continue")
			if code != self._DLG_OK:
				#if self._d.yesno("Do you want to save changes?") == self._DLG_YES:
				tmpusers = []
				for user in users:
					tmpusers.append(users[user])
				self._install_profile.set_users(tmpusers)
				break
			menuitem = menu_list[int(menuitem)-1]
			if menuitem == "Add user":
				code, newuser = self._d.inputbox("Enter the username for the new user")
				if code != self._DLG_OK: 
					continue
				if newuser in users:
					self._d.msgbox("A user with that name already exists")
					continue
				code, passwd1 = self._d.passwordbox("Enter the new password for user "+ newuser)
				code, passwd2 = self._d.passwordbox("Enter the new password again for confirmation")
				if code == self._DLG_OK: 
					if passwd1 != passwd2:
						self._d.msgbox("The passwords do not match! Go to the menu and try again.")
				#Create the entry for the new user
				new_user = [newuser, GLIUtility.hash_password(passwd1), ('users',), '/bin/bash', '/home/' + newuser, '', '']
				users[newuser] = new_user
				menuitem = newuser
			while 1:
				menulist = ["Password", "Group Membership", "Shell", "Home Directory", "UID", "Comment", "Delete"]
				code, menuitem2 = self._d.menu("Choose an option for user " + menuitem, choices=self._dmenu_list_to_choices(menulist), cancel="Back")
				if code != self._DLG_OK: 
					break
				menuitem2 = menulist[int(menuitem2)-1]
				if menuitem2 == "Password":
					code, passwd1 = self._d.passwordbox("Enter the new password")
					if code != self._DLG_OK: 
						continue
					code, passwd2 = self._d.passwordbox("Enter the new password again")
					if code != self._DLG_OK: 
						continue
					if passwd1 != passwd2:
						self._d.msgbox("The passwords do not match! Try again.")
						continue
					self._d.msgbox(_(u"Password saved.  Press Enter to continue."))
					users[menuitem][1] = GLIUtility.hash_password(passwd1)
				elif menuitem2 == "Group Membership":
					choice_list = [("users", "The usual group for normal users.", 1), ("wheel", "Allows users to attempt to su to root.", 0), ("audio", "Allows access to audio devices.", 0), ("games", "Allows access to games.", 0), ("apache", "For users who know what they're doing only.", 0), ("cdrom", "For users who know what they're doing only.", 0), ("ftp", "For users who know what they're doing only.", 0), ("video", "For users who know what they're doing only.", 0), ("Other", "Manually specify your groups in a comma-separated list.", 0)]
					string2 = _(u"Select which groups you would like the user %s to be in." % menuitem)
					code, group_list = self._d.checklist(string2, choices=choice_list, height=15, list_height=7, width=60)
					groups = ""
					for group in group_list:
						groups += group + ","
					if "Other" in group_list:
						code, groups = self._d.inputbox("Enter a comma-separated list of groups the user is to be in", init=",".join(users[menuitem][2]))
						if code != self._DLG_OK: continue
					users[menuitem][2] = string.split(groups, ",")
				elif menuitem2 == "Shell":
					code, shell = self._d.inputbox("Enter the shell you want the user to use.  default is /bin/bash.  ", init=users[menuitem][3])
					if code != self._DLG_OK: 
						continue
					users[menuitem][3] = shell
				elif menuitem2 == "Home Directory":
					code, homedir = self._d.inputbox("Enter the user's home directory. default is /home/username.  ", init=users[menuitem][4])
					if code != self._DLG_OK: 
						continue
					users[menuitem][4] = homedir
				elif menuitem2 == "UID":
					code, uid = self._d.inputbox("Enter the user's UID. If left blank the system will choose a default value (this is recommended).", init=users[menuitem][5])
					if code != self._DLG_OK: 
						continue
					if type(uid) != int: 
						continue
					users[menuitem][5] = uid
				elif menuitem2 == "Comment":
					code, comment = self._d.inputbox("Enter the user's comment.  This is completely optional.", init=users[menuitem][6])
					if code != self._DLG_OK: 
						continue
					users[menuitem][6] = comment
				elif menuitem2 == "Delete":
					if self._d.yesno("Are you sure you want to delete the user " + menuitem + "?") == self._DLG_YES:
						del users[menuitem]
						break

	def _set_services(self):
		choice_list = [("alsasound", "ALSA Sound Daemon"), ("sshd", "SSH Daemon (allows remote logins)"), ("","")]
		string = _(u"Choose the services you want started on bootup.  Note that depending on what packages are selected, some services listed will not exist.")
		code, services = self._d.inputbox("Enter a space-separated list of services to start on boot")
		if code == self._DLG_OK: 
			self._install_profile.set_services(None, services, None)
			
	def _save_install_profile(self, xmlfilename="", askforfilename=True):
		code = 0
		filename = xmlfilename
		if askforfilename:
			code, filename = self._d.inputbox("Enter a filename for the XML file", init=xmlfilename)
			if code != self._DLG_OK: 
				return None
		if GLIUtility.is_file(filename):
			if not self._d.yesno("The file " + filename + " already exists. Do you want to overwrite it?") == self._DLG_YES:
				return None
		configuration = open(filename ,"w")
		configuration.write(self._install_profile.serialize())
		configuration.close()
		return filename
