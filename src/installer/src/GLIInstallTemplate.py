import os, sys, shutil, GLIUtility

class GLIInstallTemplate:

	_install_profile = None
	_client_configuration = None
	
	def __init__(self, install_profile, client_configuration):
		"Sets the install_profile and client_configuration referances"
		
		self._install_profile = install_profile
		self._client_configuration = client_configuration
		
		
	def _log(self, data):
		"Logs the lines/file-object passed.  Accepts str, tuple, list, file object."
		
		# If the user passed a file object
		if type(data) == file:
		
			# Open logfile
			log_file = open(self._client_configuration.log_file, "a")
		
			# Loop until the file is done
			while True:
			
				# Get a line from the data
				line = data.readline()
				
				# If the line is not null...
				if line:
				
					# Write it to the log
					log_file.writeline(line)
					
				# If the line is null, exit the loop
				else:
					break
			
			# Close the logfile
			log_file.close()
					
		elif type(data) in [ str, tuple, list ]:
			
			# Open logfile
			log_file = open(self._client_configuration.log_file, "a")		# Convert string to list

			# If data is a string, convert it to a list for easy parsing
			if type(data) == str:
				data = [ data ]
			
			# Check for newline char
			# Add a newline char if not found
			for i in range(len(data)):
				if data[i][-1] != '\n':
					data[i] = data[i] + '\n'
			
			# Append lines to logfile
			log_file.writelines(data)
			log_file.close()
			
		else:
			raise "LoggingError", "Data to be logged must be a string, a list/tuple of strings or a file object!"
			
		
		
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

		# If chroot is true, execute in chroot
		if chroot:

			# Set the chroot log. The path is relative to the chroot.
			# ie. '/mnt/gentoo' + chroot_log_file to access outside of the chroot
			chroot_log_file = "/tmp/chroot.log"
	
			# Chroot needs to be in a child process
			pid = fork()
	
			# If you are the child process
			if pid == 0:
	
				# Chroot to /mnt/gentoo and run the command, then exit
				os.chroot(self._client_configuration.root_mount_point)
				exitstatus = os.WEXITSTATUS(os.system(command + " > " + chroot_log_file))
				sys.exit(exitstatus)
	
			# If you are the parent process...
			else:
				
				# Wait for the child, kids can be so slow sometimes... 
				child_exitstatus = os.WEXITSTATUS(os.wait()[1])
				
				# Open the chroot log and append it to the install log
				chroot_log = open(self._client_configuration.root_mount_point + chroot_log_file, "r")
				self._log(chroot_log)
				chroot_log.close()
				
				# Remove the now useless chroot log
				os.unlink(self._client_configuration.root_mount_point + chroot_log_file)
				
				# Return the exitstatus from the chroot
				return(child_exitstatus)
		
		# If chroot is false, execute in livecd env		
		else:
			
			# Generate a log file name
			livecd_log_file = os.tempnam()
		
			# Execute the command and log to the temp log file
			exitstatus = os.WEXITSTATUS(os.system(command + " > " + livecd_log_file))
			
			# Open the temp log file and log it
			livecd_log = open(livecd_log_file, "r")
			self._log(livecd_log)
			livecd_log.close()
			
			# Return the exitstatus from the command
			return(exitstatus)

	def _edit_config(file_name, key, value, enabled=True, delimeter='=', quotes_around_value=True):
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
		if uri.split('/')[0] == "file:":
		
			# Just copy the file to the destination
			shutil.copy(uri[7:], dest)
			
		else:
			
			# Wget the file
			exitstatus = self._run("wget " + uri + " -O " + dest)
			if exitstatus != 0:
				raise "URIError", "Could not retrieve " + uri + "!"
			
	def setup_network_pre(self):
		"Sets up the network on the live CD environment"
		pass

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
			#
			# Download/copy snapshot and unpack it
			#
			pass
			
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

		# Emerge Logging Daemon
		exitstatus = self._emerge(self._install_profile.get_logging_daemon_pkg())
		if exitstatus != 0:
			raise "LoggingDaemonError", "Could not emerge " + self._install_profile.get_logging_daemon_pkg() + "!"

		# Add Logging Daemon to default runlevel
		exitstatus = self._run("rc-update add " + self._install_profile.get_logging_daemon_pkg().split('/')[-1].lower() + " default", True)
		if exitstatus != 0:
			raise "LoggingDaemonError", "Failure adding " + self._install_profile.get_logging_daemon_pkg().split('/')[-1].lower() + " to default runlevel!"

	def install_cron_daemon(self):
		"Installs and sets up cron"
		# Dependency checking		
		self._depends("emerge_system")

		# Emerge Cron Daemon
		exitstatus = self._emerge(self._install_profile.get_cron_daemon_pkg())
		if exitstatus != 0:
			raise "CronDaemonError", "Could not emerge " + self._install_profile.get_cron_daemon_pkg() + "!"

		# Add Cron Daemon to default runlevel
		exitstatus = self._run("rc-update add " + self._install_profile.get_cron_daemon_pkg().split('/')[-1].lower() + " default", True)
		if exitstatus != 0:
			raise "CronDaemonError", "Failure adding " + self._install_profile.get_cron_daemon_pkg().split('/')[-1].lower() + " to default runlevel!"
		
		# If the Cron Daemon is not vixie-cron, run crontab			
		if self._install_profile.get_cron_daemon_pkg().split('/')[-1].lower() != "vixie-cron":
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

	def install_rp-pppoe(self):
		"Installs rp-pppoe"
		# Dependency checking		
		self._depends("emerge_system")
		
		# If user wants us to install rp-pppoe, then do so
		if self._install_profile.get_install_rp-pppoe():
			exitstatus = self._emerge("rp-pppoe")
			if exitstatus != 0:
				raise "RP-PPPOEError", "Could not emerge rp-pppoe!"
				
		# Should we add a section here to automatically configure rp-pppoe?
		# I think it should go into the setup_network_post section
				
	def install_pcmcia-cs(self):
		"Installs and sets up pcmcia-cs"
		# Dependency checking		
		self._depends("build_kernel")
		
		# If user wants us to install pcmcia-cs, then do so
		if self._install_profile.get_install_pcmcia-cs():
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
