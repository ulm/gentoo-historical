#!/usr/bin/python
import dialog, platform, string, os, glob, copy, re
import GLIInstallProfile
import GLIClientConfiguration
import GLIStorageDevice
import GLIUtility
#This is a parent class to centralize the code between UserGenCC and UserGenIP

###Clean up the __init__ function so that it doesn't auto call the sub functions

class GLIGen(object):
	def __init__(self):
		self._d = dialog.Dialog()
		self._client_profile = GLIClientConfiguration.ClientConfiguration()
		self._install_profile = GLIInstallProfile.InstallProfile()
		
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
	def __init__(self, local_install=True, advanced_mode=True):
		GLIGen.__init__(self)
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
			code, menuitem = self._d.menu(string, choices=self._dmenu_list_to_choices(template_choices), default_item=str(template_choices.index(arch)+1))
			if code == self._DLG_OK:
				menuitem = template_choices[int(menuitem)-1]
				try:
					self._client_profile.set_architecture_template(None, menuitem, None)
				except: 
					self._d.msgbox(_(u"Error!  Undefined architecture template specified or found on the current machine"))
		
	def set_logfile(self):
		#If not advanced, the default will suffice.
		if advanced_mode:
			string = _(u"""
			The installer logs all important events during the install process to a logfile for debugging purposes.
			The file gets copied to the new system once the install is complete.
			Enter the desired filename and path for the install log (the default is recommended.):
			""")
			initval = self._client_profile.get_log_file()
			code, logfile = self._d.inputbox(string, init=initval)
			if code == self._DLG_OK:
			
				self._client_profile.set_log_file(None, logfile, None)

	def set_root_mount_point(self):
		#If not advanced, the default will suffice.
		if advanced_mode:
			string = _(u"Enter the mount point to be used to mount the partition(s) where the new system will be installed.  The default is /mnt/gentoo and is greatly recommended, but any mount point will do.")	
			initval = self._client_profile.get_root_mount_point()
			code, rootmountpoint = self._d.inputbox(string, init=initval)
			if code == self._DLG_OK: 
				self._client_profile.set_root_mount_point(None, rootmountpoint, None)

	def set_client_networking(self):
		network_type = ""
		interface = ""
		ip_address = ""
		broadcast = ""
		netmask = ""
		gateway = ""
		code, interface = self._d.inputbox("Enter the interface (NIC) you would like to use for installation (e.g. eth0):")
		if code != self._DLG_OK: 
			return
	
		network_choices = ('DHCP', 'Static IP');
		code, menuitem = self._d.menu("Please select networking configuration:", choices=self._dmenu_list_to_choices(network_choices))
		
		if code != self._DLG_OK:
			return

		menuitem = network_choices[int(menuitem)-1]
		if menuitem == 'Static IP':
			code, ip_address = self._d.inputbox("Enter your IP address:")
			if code != self._DLG_OK: 
				return
			code, broadcast = self._d.inputbox("Enter your Broadcast address:")
			if code != self._DLG_OK: 
				return
			code, netmask = self._d.inputbox("Enter your Netmask:")
			if code != self._DLG_OK: 
				return
			code, gateway = self._d.inputbox("Enter your default gateway:")
			if code != self._DLG_OK: 
				return
			network_type = 'static'
		else:
			network_type = 'dhcp'

		try:
			self._client_profile.set_network_type(None, network_type, None)
			self._client_profile.set_network_interface(None, interface, None)
			if not network_type == 'dhcp':
				self._client_profile.set_network_ip(None, ip_address, None)
				self._client_profile.set_network_broadcast(None, broadcast, None)
				self._client_profile.set_network_netmask(None, netmask, None)
				self._client_profile.set_network_gateway(None, gateway, None)
		except GLIException, e:
			self._d.msgbox(e)

	def set_enable_ssh(self):
		if advanced_mode:
			if self._d.yesno(_(u"Do you want SSH enabled during the install?  This will allow you to login remotely during the installation process.  If choosing Yes, be sure you select a new LIVECD root password!")) == self._DLG_YES:
				self._client_profile.set_enable_ssh(None, True, None)
			else:
				self._client_profile.set_enable_ssh(None, False, None)

	def set_livecd_password(self):
		# The root password will be set here only if in advanced mode.  Otherwise it is auto-scrambled.
		if advanced_mode:
			match = False;
			while not match:
				string = _(u"""
				If you want to be able to login to your machine from another console during the installation,
				you will want to enter a new root password for the LIVECD.
				Note that this can be different from your new system's root password.
				Presss Enter twice to skip this step.
				Enter the new LIVECD root password:"			
				""")
				code, passwd1 = self._d.passwordbox(string)
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

	def set_client_kernel_modules(self):
		if advanced_mode:
			status, output = GLIUtility.spawn("lsmod", return_output=True)
			string1 = _(u"Here is a list of modules currently loaded on your machine.\n")
			string2 = _(u"\nIf you have additional modules you would like loaded before the installation begins (ex. a network driver), enter them in a space-separated list.")
			code, kernel_modules_list = self._d.inputbox(string1+output+string2, init="")
			if code == self._DLG_OK:
				try:
					self._client_profile.set_kernel_modules(None, kernel_modules_list, None)
				except:
					d.msgbox("ERROR! Could not set the list of kernel modules!")

	def save_client_profile(self, xmlfilename="", askforfilename=True):
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
		configuration.write(self._client_profile.serialize())
		configuration.close()
		return filename

class GLIGenIP(GLIGen):
	def __init__(self, local_install=True):
		GLIGen.__init__(self)
		self.local_install = local_install
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
			code, menuitem = self._d.menu("Choose an option", choices=self._dmenu_list_to_choices(self._menu_list), default_item=str(current_item), cancel="Done")
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
			code, tznum = self._d.menu("Select a timezone", choices=self._dmenu_list_to_choices(tzlist), cancel="Back")
			if code == self._DLG_OK:
				zonepath = os.path.join(zonepath,tzlist[int(tznum)-1])
				if tzlist[int(tznum)-1][-1:] != "/": 
					break
			else:
				if zonepath == "/usr/share/zoneinfo": 
					return
				slashloc = zonepath[:-1].rfind("/")
				zonepath = zonepath[:slashloc]
		self._install_profile.set_time_zone(None, zonepath[20:], None)
	
	def _set_portage_tree(self):
	# This section will ask whether to sync the tree, whether to use a snapshot, etc.
		menulist = ["Normal 'emerge sync'", "Webrsync (rsync is firewalled)", "Snapshot (using a portage snapshot)", "None (NFS mount)"]
		code, portage_tree_sync = self._d.menu("How do you want to sync the portage tree?", choices=self._dmenu_list_to_choices(menulist))
		if code != self._DLG_OK: 
			return
		portage_tree_sync = menulist[int(portage_tree_sync)-1]
		#FIX ME when python 2.4 comes out.
		if portage_tree_sync == "Normal 'emerge sync'": 
			self._install_profile.set_portage_tree_sync_type(None, "sync", None)
		if portage_tree_sync == "Webrsync (rsync is firewalled)": 
			self._install_profile.set_portage_tree_sync_type(None, "webrsync", None)
		if portage_tree_sync == "None (NFS mount)": 
			self._install_profile.set_portage_tree_sync_type(None, "none", None)
		if portage_tree_sync == "Snapshot (using a portage snapshot)":
			self._install_profile.set_portage_tree_sync_type(None, "snapshot", None)		
			snapshot_options = ("Use Local", "Specify URI")
			code, snapshot_option = self._d.menu("Select a local portage snapshot or manually specify a location:", choices=self._dmenu_list_to_choices(snapshot_options))
			snapshot_option = snapshot_options[int(snapshot_option)-1]
			if snapshot_option == "Use Local":
				snapshot_dir = "/mnt/cdrom/snapshots"
				stages_dir = "/mnt/cdrom/stages"
				if os.path.isdir(snapshot_dir) and os.listdir(stages_dir):
					local_snapshots = glob.glob(snapshot_dir + "/portage*.bz2")
					if len(local_snapshots) == 1:
						snapshot = local_snapshots[0]
					else:
						local_snapshots.sort()
						code, snapshot = self._d.menu("Select a local portage snapshot:", choices=self._dmenu_list_to_choices(local_snapshots))
						if code != self._DLG_OK: return
						snapshot = local_snapshots[int(snapshot)-1]
				else:
					self._d.msgbox("There don't seem to be any local portage snapshots available.  Hit OK to manually specify a URI.")
					snapshot_option = "Specify URI"
			if snapshot_option != "Use Local":
				code, snapshot = self._d.inputbox("Enter portage tree snapshot URI", init=self._install_profile.get_portage_tree_snapshot_uri())
			if code == self._DLG_OK:
				if snapshot: 
					if not GLIUtility.is_uri(snapshot, checklocal=self.local_install):
						self._d.msgbox("The specified URI is invalid.  It was not saved.  Please go back and try again.");
					else: 
						self._install_profile.set_portage_tree_snapshot_uri(None, snapshot, None)
			
				else: 
					self._d.msgbox("No URI was specified!")
			#if d.yesno("The specified URI is invalid. Use it anyway?") == DLG_YES: install_profile.set_stage_tarball_uri(None, stage_tarball, None)

	def _set_partitions(self):
		if not self._d.yesno("This will reset any changes you have made. Continue?") == self._DLG_YES: 
			return
#		devices = copy.deepcopy(install_profile.get_partition_tables())
		devices = {}
		drives = GLIStorageDevice.detect_devices()
		drives.sort()
#		use_existing = False
#		if not devices:
		use_existing = self.local_install #(d.yesno("Do you want to use the existing disk partitions?") == DLG_YES)
		for drive in drives:
			devices[drive] = GLIStorageDevice.Device(drive)
			if use_existing: 
				devices[drive].set_partitions_from_disk()
		while 1:
			code, drive_to_partition = self._d.menu("Which drive would you like to partition?", choices=self._dmenu_list_to_choices(drives), cancel="Done")
			if code != self._DLG_OK: 
				break
			drive_to_partition = drives[int(drive_to_partition)-1]
			while 1:
				partitions = devices[drive_to_partition].get_partitions()
				partsmenu = devices[drive_to_partition].get_ordered_partition_list()
				code, part_to_edit = self._d.menu("Which partition would you like to edit?", width=70, choices=self._dmenu_list_to_choices(partsmenu), cancel="Back")
				if code != self._DLG_OK: 
					break
				part_to_edit = partsmenu[int(part_to_edit)-1]
				if re.compile("^Free Space").match(part_to_edit) != None:
					new_start, new_end = re.compile("^Free Space \((\d+)\s*-\s*(\d+)\)").match(part_to_edit).groups()
					code, new_start2 = self._d.inputbox("New partition start (minimum " + new_start + ")?", init=new_start)
					if code != self._DLG_OK: 
						continue
					code, new_end2 = self._d.inputbox("New partition end (maximum " + new_end + ")?", init=new_end)
					if code != self._DLG_OK: 
						continue
					part_types = ["ext2", "ext3", "linux-swap", "fat32", "ntfs", "extended", "other"]
					code, r_type = self._d.menu("Type for new partition (reiserfs not yet supported!)", choices=self._dmenu_list_to_choices(part_types))
					if code != self._DLG_OK: 
						continue
					r_type = part_types[int(r_type)-1]
					if r_type == "other":
						code, r_type = self._d.inputbox("New partition's type?")
					if code != self._DLG_OK: 
						continue
					if (int(new_start2) < int(new_start)) or (int(new_end2) > int(new_end)):
						self._d.msgbox("Cannot create new partition because it is not within the bounds of the selected free space.")
						continue
					devices[drive_to_partition].add_partition(devices[drive_to_partition].get_free_minor_at(int(new_start2), int(new_end2)), int(new_start2), int(new_end2), r_type)
				else:
					while 1:
						tmpdevice, tmpminor = re.compile("^(/dev/[a-zA-Z]+)(\d+):").search(part_to_edit).groups()
						tmppart = partitions[int(tmpminor)]
						tmptitle = tmpdevice + tmpminor + ": " + str(tmppart.get_start()) + "-" + str(tmppart.get_end())
						menulist = ["Delete", "Mount Point", "Mount Options", "Type", "Format"]
						code, part_action = self._d.menu(tmptitle, choices=self._dmenu_list_to_choices(menulist), cancel="Back")
						if code != self._DLG_OK: break
						part_action = menulist[int(part_action)-1]
						if part_action == "Delete":
							answer = (self._d.yesno("Are you sure you want to delete the partition " + tmpdevice + tmpminor + "?") == self._DLG_YES)
							if answer:
								tmpdev = tmppart.get_device()
								tmpdev.remove_partition(int(tmpminor))
								break
						elif part_action == "Mount Point":
							code, answer = self._d.inputbox("Enter a mountpoint for partition" + str(tmpminor), init=tmppart.get_mountopts())
							if code == DLG_OK: 
								tmppart.set_mountpoint(answer)
						elif part_action == "Mount Options":
							code, answer = self._d.inputbox("Enter your options for partition" + str(tmpminor), init=tmppart.get_mountopts())
							if code == self._DLG_OK: 
								tmppart.set_mountopts(answer)
						elif part_action == "Type":
							part_types = ["ext2", "ext3", "linux-swap", "fat32", "ntfs", "extended", "other"]
							code, r_type = self._d.menu("Type for partition (reiserfs not supported!)", choices=self._dmenu_list_to_choices(part_types))
							if code != self._DLG_OK: 
								continue
							r_type = part_types[int(type)-1]
							if r_type == "other":
								code, r_type = self._d.inputbox("Partition's type?")
							tmppart.set_type(type)
						elif part_action == "Format":
							answer = self._d.yesno("Do you want to format this partition?")
							if code == self._DLG_YES: 
								tmppart.set_format(True)
							else:
								tmppart.set_format(False)						
												
		if self._d.yesno("Would you like to save changes?") == self._DLG_YES:
			parts_tmp = {}
			for part in devices.keys():
				parts_tmp[part] = devices[part].get_install_profile_structure()
			self._install_profile.set_partition_tables(parts_tmp)

	def _set_network_mounts(self):
	# This is where any NFS mounts will be specified
		network_mounts = copy.deepcopy(self._install_profile.get_network_mounts())
		while 1:
			menulist = []
			for mount in network_mounts:
				menulist.append(mount['host'] + ":" + mount['export'])
			menulist.append("Add new network mount")
			choices = self._dmenu_list_to_choices(menulist)
			code, menuitemidx = self._d.menu("Select a network mount", choices=choices, cancel="Done")
			if code:
				if self._d.yesno("Do you want to save changes?") == self._DLG_YES:
					self._install_profile.set_network_mounts(network_mounts)
				break
			menuitem = menulist[int(menuitemidx)-1]
			if menuitem == "Add new network mount":
				code, nfsmount = self._d.inputbox("Enter NFS mount or just enter the IP/hostname to search for available mounts")
				if code != self._DLG_OK: 
					continue
				if not GLIUtility.is_nfs(nfsmount):
					if GLIUtility.is_ip(nfsmount) or GLIUtility.is_hostname(nfsmount):
						status, remotemounts = GLIUtility.spawn("/usr/sbin/showmount -e " + nfsmount + " 2>&1 | egrep '^/' | cut -d ' ' -f 1 && echo", return_output=True)
						if not len(remotemounts):
							self._d.msgbox("No NFS exports detected on " + nfsmount)
							continue
						for i in range(0, len(remotemounts)):
							remotemounts[i] = string.strip(remotemounts[i])
						code, nfsmount2 = self._d.menu("Select a NFS export", choices=self._dmenu_list_to_choices(remotemounts), cancel="Back")
						if code != self._DLG_OK: 
							continue
						nfsmount2 = remotemounts[int(nfsmount2)-1]
					else:
						self._d.msgbox("Enter '" + nfsmount + "' is not a valid IP or hostname")
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
		while 1:
			menulist = ["ACCEPT_KEYWORDS", "CFLAGS", "CHOST", "MAKEOPTS", "FEATURES", "USE", "GENTOO_MIRRORS", "SYNC"]
			code, menuitem = self._d.menu("Choose a variable to edit", choices=self._dmenu_list_to_choices(menulist), cancel="Done")
			if code != self._DLG_OK: 
				break
			menuitem = menulist[int(menuitem)-1]
			oldval = ""
			if make_conf.has_key(menuitem): 
				oldval = make_conf[menuitem]
			code, newval = self._d.inputbox("Enter new value for " + menuitem, init=oldval)
			if code == self._DLG_OK:
				make_conf[menuitem] = newval
				self._install_profile.set_make_conf(make_conf)

	def _set_kernel(self):
	# This section will be for choosing kernel sources, choosing (and specifying) a custom config or genkernel, modules to load at startup, etc.
		kernel_sources = ("vanilla-sources", "gentoo-sources", "development-sources", "gentoo-dev-sources", "hardened-sources", "livecd-kernel")
		code, menuitem = self._d.menu("Choose a kernel sources package", choices=self._dmenu_list_to_choices(kernel_sources))
		if code != self._DLG_OK: 
			return
		menuitem = kernel_sources[int(menuitem)-1]
		self._install_profile.set_kernel_source_pkg(None, menuitem, None)
		if not menuitem == "livecd-kernel":
			if self._d.yesno("Do you want to use genkernel to automatically generate your kernel?") == self._DLG_NO:
				code, custom_kernel_uri = self._d.inputbox("Enter the custom kernel uri")
				if code == self._DLG_OK: 
					if custom_kernel_uri: 
						if not GLIUtility.is_uri(custom_kernel_uri, checklocal=self.local_install):
							self._d.msgbox("The specified URI is invalid.  It was not saved.  Please go back and try again.");
						else: self._install_profile.set_kernel_config_uri(None, custom_kernel_uri, None)
					else: self._d.msgbox("No URI was specified!")
			else: 
				if self._d.yesno("Do you want the bootsplash?") == self._DLG_YES:
					self._install_profile.set_kernel_bootsplash(None, True, None)
				else:
					self._install_profile.set_kernel_bootsplash(None, False, None)

	def _set_install_stage(self):
	# The install stage and stage tarball will be selected here
		install_stages = ("1","2","3","3 + GRP (use binary packages)")
		code, install_stage = self._d.menu("Which stage do you want to start at?", choices=self._dmenu_list_to_choices(install_stages), cancel="Back")
		if code == self._DLG_OK:
			install_stage = install_stages[int(install_stage)-1]
			if install_stage == "3 + GRP (use binary packages)":
				install_stage = "3"
				self._install_profile.set_grp_install(None, True, None)
			self._install_profile.set_install_stage(None, install_stage, None)
		tarball_options = ("Use Local", "Specify URI")
		code, tarball_option = self._d.menu("Select a local stage " + install_stage + " tarball or manually specify a URI:", choices=self._dmenu_list_to_choices(tarball_options))
		if code == self._DLG_OK:
			tarball_option = tarball_options[int(tarball_option)-1]
			if tarball_option == "Use Local":
				stages_dir = "/mnt/cdrom/stages"
				if os.path.isdir(stages_dir) and os.listdir(stages_dir):
					local_tarballs = glob.glob(stages_dir + "/stage" + install_stage + "*.bz2")
					local_tarballs.sort()
					code, stage_tarball = self._d.menu("Select a local tarball:", choices=self._dmenu_list_to_choices(local_tarballs))
					if code != self._DLG_OK: 
						return
					stage_tarball = local_tarballs[int(stage_tarball)-1]
				else:
					self._d.msgbox("There don't seem to be any local tarballs available.  Hit OK to manually specify a URI.")
					tarball_option = "Specify URI"
			if tarball_option != "Use Local": 
				code, stage_tarball = self._d.inputbox("Specify the stage tarball URI or local file:", init=self._install_profile.get_stage_tarball_uri())
		#If Doing a local install, check for valid file:/// uri
		if code == self._DLG_OK:
			if stage_tarball:
				if not GLIUtility.is_uri(stage_tarball, checklocal=self.local_install):
					self._d.msgbox("The specified URI is invalid.  It was not saved.  Please go back and try again.");
				else: self._install_profile.set_stage_tarball_uri(None, stage_tarball, None)
			else: self._d.msgbox("No URI was specified!")
			#if d.yesno("The specified URI is invalid. Use it anyway?") == DLG_YES: install_profile.set_stage_tarball_uri(None, stage_tarball, None)

	def _set_boot_loader(self):
		boot_loaders = ("grub", "lilo")
		code, menuitem = self._d.menu("Choose a boot loader", choices=self._dmenu_list_to_choices(boot_loaders))
		if code != self._DLG_OK: 
			return
		menuitem = boot_loaders[int(menuitem)-1]
		self._install_profile.set_boot_loader_pkg(None, menuitem, None)
		if self._d.yesno("Do you want the boot loader installed in the MBR?") == self._DLG_YES:
			self._install_profile.set_boot_loader_mbr(None, True, None)
		else:
			self._install_profile.set_boot_loader_mbr(None, False, None)
		code, bootloader_kernel_args = self._d.inputbox("Add any optional arguments to pass to the kernel at boot here:")
		if code == self._DLG_OK: 
			self._install_profile.set_bootloader_kernel_args(None, bootloader_kernel_args, None)
	
	def _set_networking(self):
	# This section will be for setting up network interfaces, defining DNS servers, default routes/gateways, etc.
		while 1:
			menulist = ["Edit Interfaces", "DNS Servers", "Default Gateway", "Hostname", "Domain Name", "HTTP Proxy", "FTP Proxy", "RSYNC Proxy", "NIS Domain Name"]
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
		cron_daemons = ("vixie-cron", "fcron", "dcron", "None")
		code, menuitem = d.menu("Choose a cron daemon", choices=self._dmenu_list_to_choices(cron_daemons))
		if code == self._DLG_OK:
			menuitem = cron_daemons[int(menuitem)-1]
			if menuitem == "None": 
				menuitem = ""
			self._install_profile.set_cron_daemon_pkg(None, menuitem, None)

	def _set_logger(self):
		loggers = ("syslog-ng", "metalog", "syslogkd")
		code, menuitem = self._d.menu("Choose a system logger", choices=self._dmenu_list_to_choices(loggers))
		if code == self._DLG_OK:
			menuitem = loggers[int(menuitem)-1]
			self._install_profile.set_logging_daemon_pkg(None, menuitem, None)

	def _set_extra_packages(self):
		#d.msgbox("This section is for selecting extra packages (pcmcia-cs, rp-pppoe, xorg-x11, etc.) and setting them up")
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
		code, passwd1 = self._d.passwordbox("Enter the new root password")
		if code != self._DLG_OK: 
			return
		code, passwd2 = self._d.passwordbox("Enter the new root password again")
		if code != self._DLG_OK: 
			return
		if passwd1 != passwd2:
			self._d.msgbox("The passwords do not match")
			return
		self._install_profile.set_root_pass_hash(None, GLIUtility.hash_password(passwd1), None)

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
			code, menuitem = self._d.menu("Choose a user to edit", choices=self._dmenu_list_to_choices(menu_list), cancel="Done")
			if code != self._DLG_OK:
				if self._d.yesno("Do you want to save changes?") == self._DLG_YES:
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
				new_user = [newuser, '', ('users',), '/bin/bash', '/home/' + newuser, '', '']
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
						self._d.msgbox("The passwords do not match")
						continue
					users[menuitem][1] = GLIUtility.hash_password(passwd1)
				elif menuitem2 == "Group Membership":
					code, groups = self._d.inputbox("Enter a space-separated list of groups the user is to be in", init=",".join(users[menuitem][2]))
					if code != self._DLG_OK: continue
#					new_groups = []
#					groups = string.split(groups)
#					for group in groups:
#						new_groups.append(group)
					users[menuitem][2] = string.split(groups, ",")
				elif menuitem2 == "Shell":
					code, shell = self._d.inputbox("Enter the shell you want the user to use.  default is /bin/bash.  Get it right b/c there's no error checking!", init=users[menuitem][3])
					if code != self._DLG_OK: 
						continue
					users[menuitem][3] = shell
				elif menuitem2 == "Home Directory":
					code, homedir = self._d.inputbox("Enter the user's home directory. default is /home/username.  Get it right b/c there's no error checking!", init=users[menuitem][4])
					if code != self._DLG_OK: 
						continue
					users[menuitem][4] = homedir
				elif menuitem2 == "UID":
					code, uid = self._d.inputbox("Enter the user's UID. ", init=users[menuitem][5])
					if code != self._DLG_OK: 
						continue
					if type(uid) != int: 
						continue
					users[menuitem][5] = uid
				elif menuitem2 == "Comment":
					code, comment = self._d.inputbox("Enter the user's comment.", init=users[menuitem][6])
					if code != self._DLG_OK: 
						continue
					users[menuitem][6] = comment
				elif menuitem2 == "Delete":
					if self._d.yesno("Are you sure you want to delete the user " + menuitem + "?") == self._DLG_YES:
						del users[menuitem]
						break

	def _set_services(self):
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
