"""
Gentoo Linux Installer

$Id: GLIArchitectureTemplate.py,v 1.21 2005/01/05 05:02:00 codeman Exp $
Copyright 2004 Gentoo Technologies Inc.


The ArchitectureTemplate is largely meant to be an abstract class and an 
interface (yes, it is both at the same time!). The purpose of this is to create 
subclasses that populate all the methods with working methods for that architecture. 
The only definitions that are filled in here are architecture independent. 

"""

import GLIUtility, os, string, sys, shutil
from GLIException import *
# Until I switch my partition code to GLIUtility.spawn()
import commands

class ArchitectureTemplate:

	def __init__(self,configuration=None, install_profile=None, client_controller=None):
		self._client_configuration = configuration
		self._install_profile = install_profile
		self._cc = client_controller

		# This will get used a lot, so it's probably
		# better to store it in a variable than to call
		# this method 100000 times.
		self._chroot_dir = self._client_configuration.get_root_mount_point()

		# These must be filled in by the subclass. _steps is a list of
		# functions, that will carry out the installation. They must be
		# in order.
		#
		# For example, self._steps might be: [preinstall, stage1, stage2, stage3, postinstall],
		# where each entry is a function (with no arguments) that carries out the desired actions.
		# Of course, steps will be different depending on the install_profile

		self._architecture_name = "generic"
		self._install_steps = [
                                 (self.do_partitioning, "Partition"),
                                 (self.mount_local_partitions, "Mount local partitions"),
                                 (self.mount_network_shares, "Mount network (NFS) shares"),
                                 (self.unpack_stage_tarball, "Unpack stage tarball"),
                                 (self.configure_make_conf, "Configure /etc/make.conf"),
                                 (self.install_portage_tree, "Portage tree voodoo"),
                                 (self.prepare_chroot, "Preparing chroot"),
                                 (self.stage1, "Performing bootstrap"),
                                 (self.stage2, "Performing 'emerge system'"),
                                 (self.set_timezone, "Setting timezone"),
                                 (self.emerge_kernel_sources, "Emerge kernel sources"),
                                 (self.build_kernel, "Building kernel"),
                                 (self.install_logging_daemon, "Logger"),
                                 (self.install_cron_daemon, "Cron daemon"),
                                 (self.install_filesystem_tools, "Installing filesystem tools"),
                                 (self.setup_network_post, "Configuring post-install networking"),
                                 (self.install_bootloader, "Configuring and installing bootloader"),
                                 (self.update_config_files, "Updating config files"),
                                 (self.configure_rc_conf, "Updating /etc/rc.conf")
                                ]


	def get_install_steps(self):
		return self._install_steps

	def notify_frontend(self, type, data):
		self._cc.addNotification(type, data)

	# It is possible to override these methods in each Arch Template.
	# It might be necessary to do so, if the arch needs something 'weird'.

	def _add_to_runlevel(self, script_name, runlevel="default"):
		"Adds the script named 'script_name' to the runlevel 'runlevel' in the chroot environement"
		
		# Do it
		status = GLIUtility.spawn("rc-update add " + script_name + " " + runlevel, chroot=self._chroot_dir)
		if not GLIUtility.exit_success(status):
			raise GLIException("RunlevelAddError", 'warning', '_add_to_runlevel', "Failure adding " + script_name + " to runlevel " + runlevel + "!")

	def _emerge(self, package, binary=False, binary_only=False):
		if binary_only:
			return GLIUtility.spawn("emerge -K " + package, display_on_tty8=True, chroot=self._chroot_dir)
		elif binary:
			return GLIUtility.spawn("emerge -k " + package, display_on_tty8=True, chroot=self._chroot_dir)
		else:
			return GLIUtility.spawn("emerge " + package, display_on_tty8=True, chroot=self._chroot_dir)

	def _edit_config(self, filename, newvalues, delimeter='=', quotes_around_value=True):
		"""
		filename = file to be editted
		newvlaues = a dictionary of VARIABLE:VALUE pairs
		"""
		if not GLIUtility.is_file(filename):
			raise GLIException("NoSuchFileError", 'notice','_edit_config',filename + ' does not exist!')
	
		f = open(filename)
		file = f.readlines()
		f.close()
	
		for key in newvalues.keys():
			regexpr = '^\s*#?\s*' + key + '\s*' + delimeter + '.*$'
			regexpr = re.compile(regexpr)
	
			for i in range(0, len(file)):
				if regexpr.match(file[i]):
					if not file[i][0] == '#':
						file[i] = '#' + file[i]
	
			file.append('\n# Added by GLI\n')
			if quotes_around_value:
				file.append(key + delimeter + '"' + newvalues[key] + '"\n')
			else:
				file.append(key + delimeter + newvalues[key]+'\n')
	
		f = open(filename,'w')
		f.writelines(file)
		f.flush()
		f.close()


	def stage1(self):
		"Stage 1 install -- bootstraping"

		# If we are doing a stage 1 install, then bootstrap 
		if self._install_profile.get_install_stage() == 1:
			exitstatus = GLIUtility.spawn("/usr/portage/scripts/bootstrap.sh", chroot=self._chroot_dir)
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("Stage1Error", 'fatal','stage1', "Bootstrapping failed!")
		
	def stage2(self):
		# If we are doing a stage 1 or 2 install, then emerge system
		if self._install_profile.get_install_stage() in [ 1, 2 ]:
			exitstatus = self._emerge("system")
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("Stage2Error", 'fatal','stage2', "Building the system failed!")

	def unpack_stage_tarball(self):
		if not os.path.isdir(self._chroot_dir):
			os.makedirs(self._chroot_dir)
		GLIUtility.fetch_and_unpack_tarball(self._install_profile.get_stage_tarball_uri(), self._chroot_dir, keep_permissions=True)

	def prepare_chroot(self):
		ret = GLIUtility.spawn("cp -L /etc/resolv.conf /mnt/gentoo/etc/resolv.conf")
		if not GLIUtility.exitsuccess(ret):
			raise GLIException("CopyError", 'warning','preinstall','Could not copy resolv.conf!')

		ret = GLIUtility.spawn("mount -t proc none /mnt/gentoo /proc")
		if not GLIUtility.exitsuccess(ret):
			raise GLIException("MountError", 'fatal','preinstall','Could not mount /proc')

		# Set USE flags here
		# might want to rewrite/use _edit_config from the GLIInstallTemplate
		# Then you should be done... at least with the preinstall.

	def install_packages(self):
		"Will install any extra software!"

		installpackages = self._install_profile.get_install_packages()
		for package in installpackages:
			status = self._emerge(package)
			if not GLIUtility.exitsuccess(status):
				raise GLIException("InstallPackagesError", 'warning', 'install_packages', "Could not emerge " + package + "!")

# **************************************************************************************

			
	def mount_local_partitions(self):
		"Mounts all partitions that are on the local machine"
		pass
		
	def mount_network_shares(self):
		"Mounts all network shares to the local machine"
		pass
		
	def fetch_sources_from_cd(self):
		"Gets sources from CD (required for non-network installation)"
		pass

	def fetch_grp_from_cd(self):
		"Gets grp binary packages from CD (required for non-network binary installation)"
		pass
	
	def configure_make_conf(self):
		"Configures make.conf"
				
		# Get make.conf options
		options = self._install_profile.get_make_conf()
		
		# For each configuration option...
		for key in options.keys():
		
			# Add/Edit it into make.conf
			self._edit_config(self._chroot_dir + "/etc/make.conf", key, options[key])

	def install_portage_tree(self):
		"Get/update the portage tree"
		
		# Check the type of portage tree fetching we'll do
		# If it is custom, follow the path to the custom tarball and unpack it
		if self._install_profile.get_portage_tree_sync_type() == "custom":
		
			# Get portage tree info
			portage_tree_snapshot_uri = self._install_profile.get_portage_tree_snapshot_uri()
			
			# Fetch and unpack the tarball
			GLIUtility.fetch_and_unpack_tarball(portage_tree_snapshot_uri, self._chroot_dir + "/usr/", self._chroot_dir + "/")
			if not GLIUtility.is_file(self._chroot_dir+"/usr/portage/distfiles"):
				exitstatus = GLIUtility.spawn("mkdir /usr/portage/distfiles",chroot=self._chroot_dir)
				if exitstatus != 0:
					raise GLIException("MkdirError", 'fatal','install_portage_tree',"Making the distfiles directory failed.")
			#!!!!!!!!!!FIXME THIS SHOULD NOT BE HERE
			exitstatus = GLIUtility.spawn("cp /mnt/cdrom/distfiles/* "+self._chroot_dir+"/usr/portage/distfiles/")
			if exitstatus != 0:
				raise GLIException("PortageError", 'fatal','install_portage_tree',"Failed to copy the distfiles to the new system")
		# If the type is webrsync, then run emerge-webrsync
		elif self._install_profile.get_portage_tree_sync_type() == "webrsync":
			exitstatus = GLIUtility.spawn("emerge-webrsync", chroot=self._chroot_dir)
			if exitstatus != 0:
				raise GLIException("EmergeWebRsyncError", 'fatal','install_portage_tre', "Failed to retrieve portage tree!")
				
		# Otherwise, just run emerge sync
		else:
			exitstatus = self._emerge("sync")
			if exitstatus != 0:
				raise GLIException("EmergeSyncError", 'fatal','install_portage_tree', "Failed to retrieve portage tree!")
		
	def set_timezone(self):
		"Sets the timezone for the new environment"
		# Set symlink
		if not os.access(self._chroot_dir + "/etc/localtime", os.W_OK):
			os.symlink(self._chroot_dir + "/usr/share/zoneinfo/" + self._install_profile.get_time_zone(), self._chroot_dir + "/etc/localtime")
		if not (self._install_profile.get_time_zone() == "UTC"):
			self._edit_config(self._chroot_dir + "/etc/rc.conf", "CLOCK", "local")
		
	def configure_fstab(self):
		"Configures fstab"
		newfstab = ""
		partitions = self._install_profile.get_fstab()
		for partition in partitions:
			if not GLIUtility.is_file(self._chroot_dir+partition):
				exitstatus = GLIUtility.spawn("mkdir " + partition, True)
				if exitstatus != 0:
					raise GLIException("MkdirError", 'fatal','configure_fstab', "Making the mount point failed!")
			newfstab += partitions[partition][0] + "\t " + partition + "\t " + partitions[partition][1]
			newfstab += "\t " + partitions[partition][2] + "\t "
			if partition == "/boot":
				newfstab += "1 2\n"
			elif partition == "/":
				newfstab += "0 1\n"
			else:
				newfstab += "0 0\n"
		newfstab += "none        /proc     proc    defaults          0 0\n"
		newfstab += "none        /dev/shm  tmpfs   defaults          0 0\n"
		if GLIUtility.is_device("/dev/cdroms/cdrom0"):
			newfstab += "/dev/cdroms/cdrom0    /mnt/cdrom    auto      noauto,user    0 0\n"

		for netmount in self._install_profile.get_network_mounts():
			if netmount['type'] == "nfs":
				newfstab += netmount['host'] + ":" + netmount['export'] + "\t" + netmount['mountpoint'] + "\tnfs\t" + netmount['mountopts'] + "\t0 0\n"
			
		file_name = self._chroot_dir + "/etc/fstab"	
		try:
			shutil.move(file_name, file_name + ".OLDdefault")
		except:
			pass
		f = open(file_name, 'w')
		f.writelines(newfstab)
		f.close()


	def emerge_kernel_sources(self):
		"Fetches desired kernel sources"
		exitstatus = self._emerge(self._install_profile.get_kernel_source_pkg())
		if exitstatus != 0:
			raise GLIException("EmergeKernelSourcesError", 'warning','emerge_kernel_sources',"Could not retrieve kernel sources!")
		try:
			os.stat(self._chroot_dir + "/usr/src/linux")
		except:
			kernels = os.listdir(self._chroot_dir+"/usr/src")
			found_a_kernel = False
			counter = 0
			while not found_a_kernel:
				if kernels[counter][0:6]=="linux-":
					exitstatus = GLIUtility.spawn("ln -s /usr/src/"+kernels[counter]+ " /usr/src/linux",chroot=self._chroot_dir)
					found_a_kernel = True
				else:
					counter = counter + 1

	def build_kernel(self):
		"Builds kernel"
		exitstatus = self._emerge("genkernel")
		if exitstatus != 0:
			raise GLIException("EmergeGenKernelError", 'warning','build_kernel', "Could not emerge genkernel!")
		
		# Null the genkernel_options
		genkernel_options = ""

		# Get the uri to the kernel config
		kernel_config_uri = self._install_profile.get_kernel_config_uri()
		
		# If the uri for the kernel config is not null, then
		if kernel_config_uri != "":
			GLIUtility.get_uri(kernel_config_uri, self._chroot_dir + "/root/kernel_config")
			genkernel_options = genkernel_options + " --kernel-config=/root/kernel_config"
			
		# Decide whether to use bootsplash or not
		if self._install_profile.get_kernel_bootsplash():
			genkernel_options = genkernel_options + " --bootsplash"
		else:
			genkernel_options = genkernel_options + " --no-bootsplash"
			
		# This is code to choose whether or not genekernel will build an initrd or not
		# Genkernel currently does not support this
		#if self._install_profile.get_kernel_initrd():
		#	pass
		#else:
		#	pass
			
		# Run genkernel in chroot
		print "genkernel all " + genkernel_options
		exitstatus = GLIUtility.spawn("genkernel all " + genkernel_options, chroot=self._chroot_dir)
		if exitstatus != 0:
			raise GLIException("KernelBuildError", 'fatal', 'build_kernel', "Could not build kernel!")
			
	def install_logging_daemon(self):
		"Installs and sets up logger"
		# Get loggin daemon info
		logging_daemon_pkg = self._install_profile.get_logging_daemon_pkg()
		if logging_daemon_pkg:
			# Emerge Logging Daemon
			exitstatus = self._emerge(logging_daemon_pkg)
			if exitstatus != 0:
				raise GLIException("LoggingDaemonError", 'warning','install_logging_daemon', "Could not emerge " + logging_daemon_pkg + "!")

			# Add Logging Daemon to default runlevel
			self._add_to_runlevel(logging_daemon_pkg)

	def install_cron_daemon(self):
		"Installs and sets up cron"
		# Get cron daemon info
		cron_daemon_pkg = self._install_profile.get_cron_daemon_pkg()
		if cron_daemon_pkg:
			# Emerge Cron Daemon
			exitstatus = self._emerge(cron_daemon_pkg)
			if exitstatus != 0:
				raise GLIException("CronDaemonError", 'warning', 'install_cron_daemon', "Could not emerge " + cron_daemon_pkg + "!")

			# Add Cron Daemon to default runlevel
			self._add_to_runlevel(cron_daemon_pkg)
		
			# If the Cron Daemon is not vixie-cron, run crontab			
			if cron_daemon_pkg != "vixie-cron":
				exitstatus = GLIUtility.spawn("crontab /etc/crontab", chroot=self._chroot_dir)
				if exitstatus != 0:
					raise GLIException("CronDaemonError", 'warning', 'install_cron_daemon', "Failure making crontab!")

	def install_filesystem_tools(self):
		"Installs and sets up fstools"
		# Get the list of file system tools to be installed
		filesystem_tools = self._install_profile.get_filesystem_tools_pkgs()
		
		# If the fstools var is a str, convert it to a list
		if type(filesystem_tools) == str:
			filesystem_tools = [ filesystem_tools ]
		
		# For each fstool package in the list, install it
		for package in filesystem_tools:
			exitstatus = self._emerge(package)
			if exitstatus != 0:
				raise GLIException("FilesystemToolsError", 'warning', 'install_filesystem_tools', "Could not emerge " + package + "!")

	def install_rp_pppoe(self):
		"Installs rp-pppoe"
		# If user wants us to install rp-pppoe, then do so
		if self._install_profile.get_install_rp_pppoe():
			exitstatus = self._emerge("rp-pppoe")
			if exitstatus != 0:
				raise GLIException("RP_PPPOEError", 'warning', 'install_rp_pppoe', "Could not emerge rp-pppoe!")
				
		# Should we add a section here to automatically configure rp-pppoe?
		# I think it should go into the setup_network_post section
		# What do you guys think?
				
	def install_pcmcia_cs(self):
		"Installs and sets up pcmcia-cs"
		# If user wants us to install pcmcia-cs, then do so
		if self._install_profile.get_install_pcmcia_cs():
			exitstatus = self._emerge("pcmcia-cs")
			if exitstatus != 0:
				raise GLIException("PCMCIA_CSError", 'warning', 'install_pcmcia_cs', "Could not emerge pcmcia-cs!")
				
			# Add pcmcia-cs to the default runlevel
			self._add_to_runlevel(pcmcia)

	def update_config_files(self):
		"Runs etc-update (overwriting all config files), then re-configures the modified ones"
		# Run etc-update overwriting all config files
		status = GLIUtility.spawn('echo "-5" | etc-update', chroot=self._chroot_dir)
		if not GLIUtility.exit_success(status):
			raise GLIException("EtcUpdateError", 'warning', 'update_config_files', "Could not update config files!")
			
		self.configure_make_conf()
		self.configure_fstab()

	def configure_rc_conf(self):
		"Configures rc.conf"
		# Get make.conf options
		options = self._install_profile.get_rc_conf()
		
		# For each configuration option...
		for key in options.keys():
		
			# Add/Edit it into rc.conf
			self._edit_config(self._chroot_dir + "/etc/rc.conf", key, options[key])
			
	def setup_network_post(self):
		"Sets up the network for the first boot"
		# Get hostname, domainname and nisdomainname
		hostname = self._install_profile.get_hostname()
		domainname = self._install_profile.get_domainname()
		nisdomainname = self._install_profile.get_nisdomainname()
		
		# Write the hostname to the hostname file		
		open(self._chroot_dir + "/etc/hostname", "w").write(hostname + "\n")
		
		# Write the domainname to the nisdomainname file
		if domainname:
			open(self._chroot_dir + "/etc/dnsdomainname", "w").write(domainname + "\n")
		
		# Write the nisdomainname to the nisdomainname file
		if nisdomainname:
			open(self._chroot_dir + "/etc/nisdomainname", "w").write(nisdomainname + "\n")
			
		#
		# EDIT THE /ETC/HOSTS FILE
		#
			
		# The address we are editing is 127.0.0.1
		hosts_ip = "127.0.0.1"

		# If the hostname is localhost
		if hostname == "localhost":
			# If a domainname is set
			if domainname:
				hosts_line = hostname + "." + domainname + "\t" + hostname
			else:
				hosts_line = hostname
		# If the hostname is not localhost
		else:
			# If a domainname is set
			if domainname:
				hosts_line = hostname + "." + domainname + "\t" + hostname + "\tlocalhost"
			else:
				hosts_line = "localhost\t" + hostname

		# Write to file
		self._edit_config(self._chroot_dir + "/etc/hosts", hosts_ip, hosts_line, True, '\t', False)

		#
		# SET DEFAULT GATEWAY
		#

		# Get default gateway
		default_gateway = self._install_profile.get_default_gateway()
		
		# If the default gateway exists, add it
		if default_gateway:
			self._edit_config(self._chroot_dir + "/etc/conf.d/net", "gateway", default_gateway)
			
		#
		# SET RESOLV INFO
		#

		# Get dns servers
		dns_servers = self._install_profile.get_dns_servers()
		
		# Clear the list
		resolv_output = []
		
		# If dns servers are set
		if dns_servers:
			
			
			# Parse each dns server
			for dns_server in dns_servers:
				# Add the server to the output
				resolv_output.append("nameserver " + dns_server +"\n")
			
			# If the domainname is set, then also output it
			if domainname:
				resolv_output.append("search " + domainname + "\n")
				
		# Output to file
		resolve_conf = open(self._chroot_dir + "/etc/resolv.conf", "w")
		resolve_conf.writelines(resolv_output)
		resolve_conf.close()
		
		#
		# PARSE INTERFACES
		#

		# Fetch interfaces
		interfaces = self._install_profile.get_network_interfaces()
		
		# Parse each interface
		for interface in interfaces.keys():
		
			# If we are going to load the network at boot...
			if interfaces[interface][2]:
				
				# Add it to the default runlevel
				self._add_to_runlevel("net."+interface)	

			# Set what kind of interface it is
			interface_type = interface[:3]
		
			# Check to see if there is a startup script for this interface, if there isn't link to the proper script
			try:
				os.stat(self._chroot_dir + "/etc/init.d/net." + interface)
			except:
				os.symlink(self._chroot_dir + "/etc/init.d/net." + interface_type +  "0", self._chroot_dir + "/etc/init.d/net." + interface)				
		
			#
			# ETHERNET
			#
			if interface_type == "eth":

				#
				# STATIC IP
				#
				# If the post-install device info is not None, then it is a static ip addy
				if interfaces[interface][1]:
					ip = interfaces[interface][0]
					broadcast = interfaces[interface][1]
					netmask = interfaces[interface][2]
			#		aliases = interfaces[interface][1][3]
			#		alias_ips = []
			#		alias_broadcasts = []
			#		alias_netmasks = []
					
					# Write the static ip config to /etc/conf.d/net
					self._edit_config(self._chroot_dir + "/etc/conf.d/net", "iface_" + interface, ip + " broadcast " + broadcast + " netmask " + netmask)
					
					# If aliases are set
			#		if aliases:
					
						# Parse aliases to format alias info
			#			for alias in aliases:
			#				alias_ips.append(alias[0])
			#				alias_broadcasts.append(alias[1])
			#				alias_netmasks.append(allias[2])
						
						# Once the alias info has been gathered, then write it out
						# Alias ips first
			#			self._edit_config(self._chroot_dir + "/etc/conf.d/net", "alias_" + interface, string.join(alias_ips))
						# Alias broadcasts next
			#			self._edit_config(self._chroot_dir + "/etc/conf.d/net", "broadcast_" + interface, string.join(alias_broadcasts))
						# Alias netmasks last
			#			self._edit_config(self._chroot_dir + "/etc/conf.d/net", "netmask_" + interface, string.join(alias_netmasks))

				#
				# DHCP IP
				#
				else:
					self._edit_config(self._chroot_dir + "/etc/conf.d/net", "iface_" + interface, "dhcp")
							
	def set_root_password(self):
		"Sets the root password"
		status = GLIUtility.spawn('echo "root:' + self._install_profile.get_root_pass_hash() + '" | chpasswd -e', chroot=self._chroot_dir)
		if not GLIUtility.exit_success(status):
			raise GLIException("SetRootPasswordError", 'warning', 'set_root_password', "Failure to set root password!")

	def set_users(self):
		"Sets up the new users for the system"
		# Loop for each user
		for user in self._install_profile.get_users():
		
			# Get values from the tuple
			username = user[0]
			password_hash = user[1]
			groups = user[2]
			shell = user[3]
			home_dir = user[4]
			uid = user[5]
			comment = user[6]
			
			options = [ "-m", "-p " + password_hash  ]
			
			# If the groups are specified
			if groups:
			
				# If just one group is listed as a string, make it a list
				if groups == str:
					groups = [ groups ]
					
				# If only 1 group is listed
				if len(groups) == 1:
					options.append("-G " + groups[0])
					
				# If there is more than one group
				elif len(groups) > 1:
					options.append('-G "' + string.join(groups, ",") + '"')
			
			# If a shell is specified
			if shell:
				options.append("-s " + shell)
				
			# If a home dir is specified
			if home_dir:
				options.append("-d " + home_dir)
				
			# If a UID is specified
			if uid:
				options.append("-u " + str(uid))
				
			# If a comment is specified
			if comment:
				options.append('-c "' + comment + '"')
				
			# Add the user
			exitstatus = GLIUtility.spawn('useradd ' + string.join(options) + ' ' + username, chroot=self._chroot_dir)
			if not GLIUtility.exit_success(exitstatus):
				raise GLIException("AddUserError", 'warning', 'set_users', "Failure to add user " + username)

	def _cylinders_to_sectors(self, minor, start, end, sectors_in_cylinder):
		cylinders = int(end) - int(start) + 1
		total_sectors = cylinders * int(sectors_in_cylinder)
		start_sector = int(start) * sectors_in_cylinder
		end_sector = start_sector + total_sectors - 1
		if int(minor) == 1 and start_sector == 0: start_sector = 63
		return (start_sector, end_sector)

	def _sectors_to_megabytes(self, sectors, sector_bytes=512):
		return float((float(sectors) * sector_bytes)/ float(1024*1024))

	def _sectors_to_bytes(self, sectors, sector_bytes=512):
		return (int(sectors) * sector_bytes)

	def _run_parted_command(self, device, cmd):
		parted_output = commands.getoutput("parted -s " + device + " " + cmd)
		print "parted -s " + device + " " + cmd

	def _add_partition(self, device, start, end, type, fs):
		start = self._sectors_to_megabytes(start)
		end = self._sectors_to_megabytes(end)
		self._run_parted_command(device, "mkpart " + type + " " + fs + " " + str(start) + " " + str(end))
		if type == "ntfs":
			pass
		elif type == "ext2" or type == "ext3":
			pass
		else:
			pass

	def do_partitioning(self):
		import GLIStorageDevice, parted, pprint

		devices_old = {}
		parts_old = {}
		parts_new = self._install_profile.get_partition_tables()
		drives = GLIStorageDevice.detect_devices()
		drives.sort()
		for drive in drives:
			devices_old[drive] = GLIStorageDevice.Device(drive)
			devices_old[drive].set_partitions_from_disk()
		for part in devices_old.keys(): parts_old[part] = devices_old[part].get_install_profile_structure()

		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(parts_old)
		pp.pprint(parts_new)

		for dev in parts_old.keys():
			parts_active = []
			parts_lba = []
			print "\nProcessing " + dev + "..."
			parted_dev = parted.PedDevice.get(dev)
			parted_disk = parted.PedDisk.new(parted_dev)
			last_partition_touched = 0
			sectors_in_cylinder = devices_old[dev]._sectors_in_cylinder
			# First pass to delete old partitions that aren't resized
			for part in parts_old[dev]:
				oldpart = parts_old[dev][part]
				old_start, old_end = self._cylinders_to_sectors(part, oldpart['start'], oldpart['end'], sectors_in_cylinder)
				matchingminor = 0
				for new_part in parts_new[dev]:
					tmppart = parts_new[dev][new_part]
					new_start, new_end = self._cylinders_to_sectors(new_part, tmppart['start'], tmppart['end'], sectors_in_cylinder)
					if int(tmppart['start']) == int(oldpart['start']) and tmppart['format'] == False and tmppart['type'] == oldpart['type'] and int(tmppart['end']) == int(oldpart['end']):
						matchingminor = new_part
						print "  Deleting old minor " + str(part) + " to be recreated later"
						self._run_parted_command(dev, "rm " + str(part))
						break
					if int(tmppart['start']) == int(oldpart['start']) and tmppart['format'] == False and tmppart['type'] == oldpart['type'] and int(tmppart['end']) != int(oldpart['end']):
						matchingminor = new_part
						print "  Ignoring old minor " + str(part) + " to resize later"
						break
				if not matchingminor:
					print "  No match found...deleting partition " + str(part)
					self._run_parted_command(dev, "rm " + str(part))
				else:
					if parted_disk.get_partition(part).get_flag(1): # Active/boot
						print "  Partition " + str(part) + " was active...noted"
						parts_active.append(int(matchingminor))
					if parted_disk.get_partition(part).get_flag(7): # LBA
						print "  Partition " + str(part) + " was LBA...noted"
						parts_lba.append(int(matchingminor))
			# Second pass to resize old partitions that need to be resized
			print " Second pass..."
			for part in parts_old[dev]:
				oldpart = parts_old[dev][part]
				old_start, old_end = self._cylinders_to_sectors(part, oldpart['start'], oldpart['end'], sectors_in_cylinder)
				for new_part in parts_new[dev]:
					tmppart = parts_new[dev][new_part]
					new_start, new_end = self._cylinders_to_sectors(new_part, tmppart['start'], tmppart['end'], sectors_in_cylinder)
					if int(tmppart['start']) == int(oldpart['start']) and tmppart['format'] == False and tmppart['type'] == oldpart['type'] and int(tmppart['end']) != int(oldpart['end']):
						print "  Resizing old minor " + str(part) + " from " + str(oldpart['start']) + "-" + str(oldpart['end'])+  " to " + str(tmppart['start']) + "-" + str(tmppart['end'])
						type = tmppart['type']
						device = dev
						minor = part
						start = int(new_start)
						end = int(new_end)
						if type == "ext2" or type == "ext3":
							total_sectors = end - start + 1
							commands.getstatus("resize2fs " + device + str(minor) + " " + str(total_sectors) + "s")
							print "resize2fs " + device + str(minor) + " " + str(total_sectors) + "s"
						elif type == "ntfs":
							total_sectors = end - start + 1
							total_bytes = int(self._sectors_to_bytes(total_sectors))
							commands.getstatus("ntfsresize --size " + str(total_bytes) + " " + device + str(minor))
							print "ntfsresize --size " + str(total_bytes) + " " + device + str(minor)
						else:
							start = float(self._sectors_to_megabytes(start))
							end = float(self._sectors_to_megabytes(end))
							self._run_parted_command(device, "resize " + str(minor) + " " + str(start) + " " + str(end))
						print "  Deleting old minor " + str(part) + " to be recreated in 3rd pass"
						self._run_parted_command(dev, "rm " + str(part))
						break
			# Third pass to create new partition table
			print " Third pass..."
			for part in parts_new[dev]:
				newpart = parts_new[dev][part]
				new_start, new_end = self._cylinders_to_sectors(part, newpart['start'], newpart['end'], sectors_in_cylinder)
				if newpart['type'] == "extended":
					print "  Adding extended partition from " + str(newpart['start']) + " to " + str(newpart['end'])
					self._add_partition(dev, new_start, new_end, "extended", "")
				elif int(part) < 5:
					print "  Adding primary partition from " + str(newpart['start']) + " to " + str(newpart['end'])
					self._add_partition(dev, new_start, new_end, "primary", newpart['type'])
				elif int(part) > 4:
					print "  Adding logical partition from " + str(newpart['start']) + " to " + str(newpart['end'])
					self._add_partition(dev, new_start, new_end, "logical", newpart['type'])
				if int(part) in parts_active and not newpart['format']:
					print "   Partition was previously active...setting"
					self._run_parted_command(dev, "set " + str(part) + " boot on")
				if int(part) in parts_lba and not newpart['format']:
					print "   Partition was previously LBA...setting"
					self._run_parted_command(dev, "set " + str(part) + " lba on")
