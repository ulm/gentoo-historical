import os, sys, shutil, GLIUtility

class GLIInstallTemplate:

	def __init__(self, install_profile, client_configuration):
		"Sets the install_profile and client_configuration referances"
		
		self._install_profile = install_profile
		self._client_configuration = client_configuration
		
	def _emerge(self, package, binary=False, binary_only=False):
		"A private method to emerge a program in the chroot environment"
		
		#
		# I made this little private method in case we want to tie
		# this more into the emerge api.  However, right now all
		# the loggin is being handled by the _run method.
		# If we integrate with portage api, we need to make sure
		# we handle logging.
		#
		
		# Decide which to run
		if binary_only:
			return self._run("emerge -K " + package, True)
		elif binary:
			return self._run("emerge -k " + package, True)
		else:
			return self._run("emerge " + package, True)	

	def _depends(self, depends):
		"A private method for dependency checking (returns bool)"

		# Type checking
		if type(depends) in [ list, str, tuple ]:
			raise "Dependencies must be a string or a list of strings"

		# If it is a string, change it to a list for parsing
		if type(depends) == str:
			depends = [ depends ]

		# Parse dependencies
		for dependency in depends:

			# If the dependency has not been satisfied, check to see if 'ignore' has been turned on
			if not dependency in self._client_configuration.install_steps_completed:

				#If ignore is on, just print a warning
				if self._install_profile.get_ignore_install_step_depends():
					print "Warning: You chose to ignore install step dependencies.  The " + dependency + " was not met.  Ignoring."
				#If ignore is off, then raise exception
				else:
					raise "InstallTemplateError",  "Install step dependency not met!"
					
	def _run(self, command, chroot=False):
		"Runs a command in the livecd or chroot environment."
		
		# If chroot is true, set the prefix to execute in chroot
		if chroot:
			prefix = "chroot " + self._client_configuration.root_mount_point + " "
		else:
			prefix = ""
			
		# This sets the logging info
		suffix = " | tee " + self._client_configuration.proc_temp_log  + " >> " + self._client_configuration.log_file
		
		exitstatus = os.WEXITSTATUS(os.system(prefix + command + suffix))
		
		return(exitstatus)

	def _edit_config(self, file_name, key, value, enabled=True, delimeter='=', quotes_around_value=True):
		"""This allows one to edit a config file non-destructively.
		For instance: USE="gtk gtk2 X gnome"
		key = "USE"
		value = "gtk gtk2 X gnome"
		enabled determines whether the line will be active or commented.
		"""
		
		# read the file into memory
		f = open(file_name)
		file = f.readlines()
		f.close()
	
		# We haven't searched for the key yet, so we haven't found it
		found_key = False
		
		# Search for the key
		for i in range(len(file)):
		
			# If the line doesn't have the delimeter, just continue the loop
			if not delimeter in file[i]:
				continue
				
			# If we find the key, whether its commented or not...
			if (file[i].split(delimeter)[0] == key) or (file[i].split(delimeter)[0] == '#' + key):
			
				# If we haven't already found (and reset) the key, lets do it...
				if not found_key:
					# Replace the line with the appropriate...
					if enabled:
						if quotes_around_value:
							file[i] = key + delimeter + '"' + value + '"' + '\n'
						else:
							file[i] = key + delimeter + value + '\n'
					else:
						if quotes_around_value:
							file[i] = '#' + key + delimeter + '"' + value + '"' + '\n'
						else:
							file[i] = '#' + key + delimeter + value + '\n'
							
					# We found the key, yeah!!!
					found_key = True
					
				# If we already found the key (and reset it),
				# but we find another instance, comment it out
				else:
				
					# If the line is not commented, comment it
					if file[i].split(delimeter)[0] == key:
						file[i] = '#' + file[i]
	
		# If after searching the whole file, we still haven't found the key...
		if not found_key:
		
			# Then just add the lines to the end of the file
			file.append('\n')
			file.append('# This line added by GLI\n')
			if enabled:
				if quotes_around_value:
					file.append(key + delimeter + '"' + value + '"' + '\n')
				else:
					file.append(key + delimeter + value + '\n')
			else:
				if quotes_around_value:
					file.append('#' + key + delimeter + '"' + value + '"' + '\n')
				else:
					file.append('#' + key + delimeter + value + '\n')
		
		# Write lines back out to file	
		f = open(file_name, 'w')
		f.writelines(file)
		f.close()
		
	def _get_uri(self, uri, dest):
		"Fetches a file from uri and places it at dest"
		
		# Check to make sure URI is valid
		if not GLIUtility.is_uri(uri):
			raise "URIError", str(uri) + " is not a valid URI!"
		
		# If this is a local URI...
		if uri.split(':')[0] == "file":
		
			# Just copy the file to the destination
			shutil.copy(uri[7:], dest)
			
		else:
			
			# Wget the file
			exitstatus = self._run("wget " + uri + " -O " + dest)
			if exitstatus != 0:
				raise "URIError", "Could not retrieve " + uri + "!"
				
	def _fetch_and_unpack_tarball(self, tarball_uri, target_directory, temp_directory="/tmp", keep_permisions=False):
		"Fetches a tarball from tarball_uri and extracts it into target_directory"
		
		# Get tarball info
		tarball_filename = tarball_uri.split("/")[-1]
		
		# Get the tarball
		self._get_uri(tarball_uri, temp_directory + "/" + tarball_filename)
		
		# Reset tar options
		tar_options = "xv"
		
		# If the tarball is bzip'd
		if tarball_filename.split(".")[-1] == "tbz" or  tarball_filename.split(".")[-1] == "bz2":
			tar_options = tar_options + "j"
				
		# If the tarball is gzip'd
		elif tarball_filename.split(".")[-1] == "tgz" or  tarball_filename.split(".")[-1] == "gz":
			tar_options = tar_options + "z"
		
		# If we want to keep permissions
		if keep_permissions:
			tar_options = tar_options + "p"
			
		# Unpack the tarball
		exitstatus = self._run("tar -" + tar_options + " -f " + temp_directory + "/" + tarball_filename + " -C " + target_directory)
		if exitstatus != 0:
			raise "UnpackTarballError", "Could not unpack tarball!"
			
	def _add_to_runlevel(self, script_name, runlevel="default"):
		"Adds the script named 'script_name' to the runlevel 'runlevel' in the chroot environement"
		
		# Do it
		exitstatus = self._run("rc-update add " + script_name + " " + runlevel, True)
		if exitstatus != 0:
			raise "RunlevelAddError", "Failure adding " + script_name + " to runlevel " + runlevel + "!"
			
	def setup_network_pre(self):
		"Sets up the network on the live CD environment"
			
		#
		# SET DEFAULT GATEWAY
		#

		# Get default gateway
		default_gateway = self._install_profile.get_default_gateway_pre()
		
		# If the default gateway exists, add it
		if default_gateway:
			self._edit_config("/etc/conf.d/net", "gateway", default_gateway)

		#
		# SET RESOLV INFO
		#

		# Get dns servers
		dns_servers = self._install_profile.get_dns_servers_pre()
		
		# If dns servers are set
		if dns_servers:
			
			# Clear the list
			resolv_output = []
			
			# Parse each dns server
			for dns_server in dns_servers:
				# Add the server to the output
				resolv_output.append("nameserver " + dns_server +"\n")
			
		# Output to file
		open("/etc/resolv.conf", "w").writelines(resolv_output)

		#
		# PARSE INTERFACES
		#

		# Fetch interfaces
		interfaces = self._install_profile.get_network_interfaces_pre()
		
		# Parse each interface
		for interface in interfaces.keys():
		
			# Set what kind of interface it is
			interface_type = interface[:3]
		
			# Check to see if there is a startup script for this interface, if there isn't link to the proper script
			if not os.access(self._client_configuration.root_mount_point + "/etc/net." + interface, W_OK):
				os.symlink("net." + interface_type +  "0", self._client_configuration.root_mount_point + "/etc/net." + interface)				
		
			#
			# ETHERNET
			#
			if interface_type == "eth":

				#
				# STATIC IP
				#
				# If the pre device info is not None, then it is a static ip addy
				if interfaces[interface][1]:
					ip = interfaces[interface][0][0]
					broadcast = interfaces[interface][0][1]
					netmask = interfaces[interface][0][2]
					aliases = interfaces[interface][0][3]
					alias_ips = []
					alias_broadcasts = []
					alias_netmasks = []
					
					# Write the static ip config to /etc/conf.d/net
					self._edit_config("/etc/conf.d/net", "iface_" + interface, ip + " broadcast " + broadcast + " netmask " + netmask)
					
					# If aliases are set
					if aliases:
					
						# Parse aliases to format alias info
						for alias in aliases:
							alias_ips.append(alias[0])
							alias_broadcasts.append(alias[1])
							alias_netmasks.append(allias[2])
						
						# Once the alias info has been gathered, then write it out
						# Alias ips first
						self._edit_config("/etc/conf.d/net", "alias_" + interface, string.join(alias_ips))
						# Alias broadcasts next
						self._edit_config("/etc/conf.d/net", "broadcast_" + interface, string.join(alias_broadcasts))
						# Alias netmasks last
						self._edit_config("/etc/conf.d/net", "netmask_" + interface, string.join(alias_netmasks))
					
				#
				# DHCP IP
				#
				else:
					self._edit_config("/etc/conf.d/net", "iface_" + interface, "dhcp")
					
			#
			# START INTERFACE
			#
			
			# Test to see if interface is already up
			iface_status = os.popen("/etc/init.d/net." + interface + " status", "r").readline().split()[-1]
			
			# If the interface is already started, restart it
			if iface_status.lower() == "started":
				exitstatus = self._run("/etc/init.d/net." + interface + " restart")
				if exitstatus != 0:
					raise "NetworkPreError", "Could not start interface " + interface + "!"
					
			# Otherwise, just start the interface
			else:
				exitstatus = self._run("/etc/init.d/net." + interface + " start")
				if exitstatus != 0:
					raise "NetworkPreError", "Could not start interface " + interface + "!"						


	def partition_local_devices(self):
		"Partitions local devices (hard drives, memory sticks, etc)"
		pass 
		
	def mount_local_partitions(self):
		"Mounts all partitions that are on the local machine"
		# Dependency checking		
		self._depends("partition_local_drives")

	def mount_network_shares(self):
		"Mounts all network shares to the local machine"
		# Dependency checking		
		self._depends([ "setup_network_pre", "mount_local_partitions" ])

	def unpack_tarball(self):
		"Unpacks the appropriate stage tarball"
		# Dependency checking		
		self._depends([ "mount_local_partitions", "mount_network_shares" ])
		
		# Get tarball info
		stage_tarball_uri = self._install_profile.get_stage_tarball_uri()
		tarball_filename = stage_tarball_uri.split("/")[-1]
		
		# Get the tarball and unpack it
		self._fetch_and_unpack_tarball(stage_tarball_uri, self._client_configuration.root_mount_point + "/", self._client_configuration.root_mount_point + "/", True)

	def fetch_sources_from_cd(self):
		"Gets sources from CD (required for non-network installation)"
		# Dependency checking		
		self._depends("unpack_tarball")

	def fetch_grp_from_cd(self):
		"Gets grp binary packages from CD (required for non-network binary installation)"
		# Dependency checking		
		self._depends("unpack_tarball")

	def prepare_chroot(self):
		"Copies resolve.conf to the chroot environment and mounts /dev and /proc"
		# Dependency checking		
		self._depends("unpack_tarball")
		
		# Copy resolv.conf to new env
		try:
			shutil.copy("/etc/resolv.conf", self._client_configuration.root_mount_point + "/etc/resolv.conf")
		except:
			pass
			
		# Mount /dev and /proc in the chroot env
		exitstatus = self._run("mount -t proc proc " + self._client_configuration.root_mount_point + "/proc", False)
		if exitstatus != 0:
			raise "MountProcError", "Could not mount /proc into the chroot environment!"
		exitstatus = self._run("mount -o bind /dev " + self._client_configuration.root_mount_point + "/dev", False)
		if exitstatus != 0:
			raise "MountDevError", "Could not mount /dev into the chroot environment!"

	def configure_make_conf(self):
		"Configures make.conf"
		# Dependency checking		
		self._depends("prepare_chroot")
		
		# Get make.conf options
		options = self._install_profile.get_make_conf()
		
		# For each configuration option...
		for key in options.keys():
		
			# Add/Edit it into make.conf
			self._edit_config(self._client_configuration.root_mount_point + "/etc/make.conf", key, option[key])

	def install_portage_tree(self):
		"Get/update the portage tree"
		# Dependency checking		
		self._depends("prepare_chroot")
		
		# Check the type of portage tree fetching we'll do
		# If it is custom, follow the path to the custom tarball and unpack it
		if self._install_profile.get_portage_tree_sync_type() == "custom":
		
			# Get portage tree info
			portage_tree_snapshot_uri = self._install_profile.get_portage_tree_snapshot_uri()
			
			# Fetch and unpack the tarball
			self._fetch_and_unpack_tarball(portage_tree_snapshot_uri, self._client_configuration.root_mount_point + "/usr/", self._client_configuration.root_mount_point + "/")
			
		# If the type is webrsync, then run emerge-webrsync
		elif self._install_profile.get_portage_tree_sync_type() == "webrsync":
			exitstatus = self._run("emerge-webrsync", True)
			if exitstatus != 0:
				raise "EmergeWebRsyncError", "Failed to retrieve portage tree!"
				
		# Otherwise, just run emerge sync
		else:
			exitstatus = self._emerge("sync")
			if exitstatus != 0:
				raise "EmergeSyncError", "Failed to retrieve portage tree!"
		
	def bootstrap(self):
		"Stage 1 install -- bootstraping"
		# Dependency checking		
		self._depends([ "install_portage_tree", "configure_make_conf" ])
		
		# If we are doing a stage 1 install, then bootstrap
		if self._install_profile.get_install_stage() == 1:
			exitstatus = self._run("/usr/portage/scripts/bootstrap.sh", True)
			if exitstatus != 0:
				raise "BootstrapError", "Bootstrapping failed!"

	def emerge_system(self):
		"Stage 1 and 2 install -- build system"
		# Dependency checking		
		self._depends("bootstrap")
		
		# If we are doing a stage 1 or 2 install, then emerge system
		if self._install_profile.get_install_stage() in [ 1, 2 ]:
			exitstatus = self._emerge("system")
			if exitstatus != 0:
				raise "EmergeSystemError", "Building the system failed!"

	def set_timezone(self):
		"Sets the timezone for the new environment"

		# Dependency checking		
		self._depends("unpack_tarball")
		self._process_desc("Setting the timezone")

		# Set symlink
		os.symlink("../usr/share/zoneinfo/" + self._install_profile.get_time_zone(), self._client_configuration.root_mount_point + "/etc/localtime")
		
	def configure_fstab(self):
		"Configures fstab"
		# Dependency checking		
		self._depends("unpack_tarball")

	def emerge_kernel_sources(self):
		"Fetches desired kernel sources"
		# Dependency checking		
		self._depends("emerge_system")
		
		exitstatus = self._emerge(self._install_profile.get_kernel_source_pkg())
		if exitstatus != 0:
			raise "EmergeKernelSourcesError", "Could not retrieve kernel sources!"

	def build_kernel(self):
		"Builds kernel"
		# Dependency checking		
		self._depends("emerge_kernel_sources")
		
		# Null the genkernel_options
		genkernel_options = ""

		# Get the uri to the kernel config
		kernel_config_uri = self._install_profile.get_kernel_config_uri()
		
		# If the uri for the kernel config is not null, then
		if kernel_config_uri != "":
			self._get_uri(kernel_config_uri, self._client_configuration.root_mount_point + "/root/kernel_config")
			genkernel_options = genkernel_options + " --kernel-config=/root/kernel_config"
			
		# Decide whether to use bootsplash or not
		if self._install_profile.get_kernel_bootsplash():
			genkernel_options = genkernel_options + " --bootsplash"
		else:
			genkernel_options = genkernel_options + " --no-bootsplash"
			
		# This is code to choose whether or not genekernel will build an initrd or not
		# Genkernel currently does not support this
		if self._install_profile.get_kernel_initrd():
			pass
		else:
			pass
			
		# Run genkernel in chroot
		exitstatus = self._run("genkernel all " + genkernel_options, True)
		if exitstatus != 0:
			raise "KernelBuildError", "Could not build kernel!"
			
	def install_logging_daemon(self):
		"Installs and sets up logger"
		# Dependency checking		
		self._depends("emerge_system")
		
		# Get loggin daemon info
		logging_daemon_pkg = self._install_profile.get_logging_daemon_pkg()

		# Emerge Logging Daemon
		exitstatus = self._emerge(logging_daemon_pkg)
		if exitstatus != 0:
			raise "LoggingDaemonError", "Could not emerge " + logging_daemon_pkg + "!"

		# Add Logging Daemon to default runlevel
		self. _add_to_runlevel(self,  logging_daemon_pkg.split('/')[-1].lower())

	def install_cron_daemon(self):
		"Installs and sets up cron"
		# Dependency checking		
		self._depends("emerge_system")
		
		# Get cron daemon info
		cron_daemon_pkg = self._install_profile.get_cron_daemon_pkg()

		# Emerge Cron Daemon
		exitstatus = self._emerge(cron_daemon_pkg)
		if exitstatus != 0:
			raise "CronDaemonError", "Could not emerge " + cron_daemon_pkg + "!"

		# Add Cron Daemon to default runlevel
		self. _add_to_runlevel(self,  cron_daemon_pkg.split('/')[-1].lower())
		
		# If the Cron Daemon is not vixie-cron, run crontab			
		if cron_daemon_pkg.split('/')[-1].lower() != "vixie-cron":
			exitstatus = self._run("crontab /etc/crontab", True)
			if exitstatus != 0:
				raise "CronDaemonError", "Failure making crontab!"

	def install_filesystem_tools(self):
		"Installs and sets up fstools"
		# Dependency checking		
		self._depends("emerge_system")
		
		# Get the list of file system tools to be installed
		filesystem_tools = self._install_profile.get_filesystem_tools_pkgs()
		
		# If the fstools var is a str, convert it to a list
		if type(filesystem_tools) == str:
			filesystem_tools = [ filesystem_tools ]
		
		# For each fstool package in the list, install it
		for package in filesystem_tools:
			exitstatus = self._emerge(package)
			if exitstatus != 0:
				raise "FilesystemToolsError", "Could not emerge " + package + "!"

	def install_rp_pppoe(self):
		"Installs rp-pppoe"
		# Dependency checking		
		self._depends("emerge_system")
		
		# If user wants us to install rp-pppoe, then do so
		if self._install_profile.get_install_rp_pppoe():
			exitstatus = self._emerge("rp-pppoe")
			if exitstatus != 0:
				raise "RP-PPPOEError", "Could not emerge rp-pppoe!"
				
		# Should we add a section here to automatically configure rp-pppoe?
		# I think it should go into the setup_network_post section
		# What do you guys think?
				
	def install_pcmcia_cs(self):
		"Installs and sets up pcmcia-cs"
		# Dependency checking		
		self._depends("build_kernel")
		
		# If user wants us to install pcmcia-cs, then do so
		if self._install_profile.get_install_pcmcia_cs():
			exitstatus = self._emerge("pcmcia-cs")
			if exitstatus != 0:
				raise "PCMCIA-CSError", "Could not emerge pcmcia-cs!"
				
			# Add pcmcia-cs to the default runlevel
			exitstatus = self._run("rc-update add pcmcia default", True)
			if exitstatus != 0:
				raise "PCMCIA-CSError", "Could not add pcmcia-cs to the default runlevel!"
	
	def install_bootloader(self):
		"Installs and configures bootloader"
		#
		# THIS IS ARCHITECTURE DEPENDANT!!!
		#
		# Dependency checking		
		self._depends("emerge_system")
		pass

	def update_config_files(self):
		"Runs etc-update (overwriting all config files), then re-configures the modified ones"
		# Dependency checking		
		self._depends("emerge_system")
		
		# Run etc-update overwriting all config files
		exitstatus = self._run('echo "-5" | etc-update', True)
		if exitstatus != 0:
			raise "EtcUpdateError", "Could not update config files!"
			
		self.configure_make_conf()
		self.configure_fstab()

	def configure_rc_conf(self):
		"Configures rc.conf"
		# Dependency checking		
		self._depends("update_config_files")
		
		# Get make.conf options
		options = self._install_profile.get_rc_conf()
		
		# For each configuration option...
		for key in options.keys():
		
			# Add/Edit it into rc.conf
			self._edit_config(self._client_configuration.root_mount_point + "/etc/rc.conf", key, option[key])
			
	def setup_network_post(self):
		"Sets up the network for the first boot"
		# Dependency checking		
		self._depends("unpack_tarball")
		
		# Get hostname, domainname and nisdomainname
		hostname = self._install_profile.get_hostname()
		domainname = self._install_profile.get_domainname()
		nisdomainname = self._install_profile.get_nisdomainname()
		
		# Write the hostname to the hostname file		
		open(self._client_configuration.root_mount_point + "/etc/hostname", "w").write(hostname + "\n")
		
		# Write the domainname to the nisdomainname file
		if domainname:
			open(self._client_configuration.root_mount_point + "/etc/dnsdomainname", "w").write(domainname + "\n")
		
		# Write the nisdomainname to the nisdomainname file
		if nisdomainname:
			open(self._client_configuration.root_mount_point + "/etc/nisdomainname", "w").write(nisdomainname + "\n")
			
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
		self._edit_config(self._client_configuration.root_mount_point + "/etc/hosts", hosts_ip, hosts_line, True, '\t', False)

		#
		# SET DEFAULT GATEWAY
		#

		# Get default gateway
		default_gateway = self._install_profile.get_default_gateway_post()
		
		# If the default gateway exists, add it
		if default_gateway:
			self._edit_config(self._client_configuration.root_mount_point + "/etc/conf.d/net", "gateway", default_gateway)
			
		#
		# SET RESOLV INFO
		#

		# Get dns servers
		dns_servers = self._install_profile.get_dns_servers_post()
		
		
		# If dns servers are set
		if dns_servers:
			
			# Clear the list
			resolv_output = []
			
			# Parse each dns server
			for dns_server in dns_servers:
				# Add the server to the output
				resolv_output.append("nameserver " + dns_server +"\n")
			
			# If the domainname is set, then also output it
			if domainname:
				resolv_output.append("search " + domainname + "\n")
				
		# Output to file
		resolve_conf = open(self._client_configuration.root_mount_point + "/etc/resolv.conf", "w")
		resolve_conf.write_lines(resolv_output)
		resolve_conf.close()
		
		#
		# PARSE INTERFACES
		#

		# Fetch interfaces
		interfaces = self._install_profile.get_network_interfaces_post()
		
		# Parse each interface
		for interface in interfaces.keys():
		
			# If we are going to load the network at boot...
			if interfaces[interface][2]:
				
				# Add it to the default runlevel
					exitstatus = self._run("rc-update add net." + interface + " default", True)
					if exitstatus != 0:
						raise "NetStartupError", "Cannot add interface " + interface + " to the default runlevel!"

			# Set what kind of interface it is
			interface_type = interface[:3]
		
			# Check to see if there is a startup script for this interface, if there isn't link to the proper script
			try:
				os.stat(self._client_configuration.root_mount_point + "/etc/net." + interface)
			except:
				os.symlink("net." + interface_type +  "0", self._client_configuration.root_mount_point + "/etc/net." + interface)				
		
			#
			# ETHERNET
			#
			if interface_type == "eth":

				#
				# STATIC IP
				#
				# If the post-install device info is not None, then it is a static ip addy
				if interfaces[interface][1]:
					ip = interfaces[interface][1][0]
					broadcast = interfaces[interface][1][1]
					netmask = interfaces[interface][1][2]
					aliases = interfaces[interface][1][3]
					alias_ips = []
					alias_broadcasts = []
					alias_netmasks = []
					
					# Write the static ip config to /etc/conf.d/net
					self._edit_config(self._client_configuration.root_mount_point + "/etc/conf.d/net", "iface_" + interface, ip + " broadcast " + broadcast + " netmask " + netmask)
					
					# If aliases are set
					if aliases:
					
						# Parse aliases to format alias info
						for alias in aliases:
							alias_ips.append(alias[0])
							alias_broadcasts.append(alias[1])
							alias_netmasks.append(allias[2])
						
						# Once the alias info has been gathered, then write it out
						# Alias ips first
						self._edit_config(self._client_configuration.root_mount_point + "/etc/conf.d/net", "alias_" + interface, string.join(alias_ips))
						# Alias broadcasts next
						self._edit_config(self._client_configuration.root_mount_point + "/etc/conf.d/net", "broadcast_" + interface, string.join(alias_broadcasts))
						# Alias netmasks last
						self._edit_config(self._client_configuration.root_mount_point + "/etc/conf.d/net", "netmask_" + interface, string.join(alias_netmasks))

				#
				# DHCP IP
				#
				else:
					self._edit_config(self._client_configuration.root_mount_point + "/etc/conf.d/net", "iface_" + interface, "dhcp")
							
	def set_root_password(self):
		"Sets the root password"
		# Dependency checking		
		self._depends("emerge_system")
		
		exitstatus = self._run('echo "root:' + self._install_profile.get_root_pass_hash() + '" | chpasswd -e', True)
		if exitstatus != 0:
			raise "SetRootPasswordError", "Failure to set root password!"

	def set_users(self):
		"Sets up the new users for the system"
		# Dependency checking
		self._depends("emerge_system")
		
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
			exitstatus = self._run('useradd ' + string.join(options) + ' ' + username, True)
			if exitstatus != 0:
				raise "AddUserError", "Failure to add user " + username
				
	def unmount_devices(self):
		"Unmounts mounted devices after installation"
		# Dependency checking		
		self._depends()
