import os, sys

class GLIInstallTemplate

	def _depends(self, install_profile, client_configureation, depends):
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
			if not dependency in client_configuration.install_steps_completed:

				#If ignore is on, just print a warning
				if install_profile.ignore_install_step_depends:
					print "Warning: You chose to ignore install step dependencies.  The " + dependency + " was not met.  Ignoring."
				#If ignore is off, then raise exception
				else:
					raise "InstallTemplateError: Install step dependency not met!"

	def _exec_in_chroot(self, command):
		"Runs a command in the chroot environment."

		# Chroot needs to be in a child process
		pid = fork()

		# If you are the child process
		if pid == 0:

			# Chroot to /mnt/gentoo and run the command, then exit
			os.chroot("/mnt/gentoo")
			os.system(command)
			sys.exit()

		# If you are the parent process, just wait for the child
		# Kids can be so slow sometimes... 
		else:
			os.wait()

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
					
		f = open(file_name, 'w')
		for line in file:
			f.write(line)
		f.close()

	def setup_network_pre(self, install_profile, client_configuration):
		"Sets up the network on the live CD environment"
		pass

	def partition_local_devices(self, install_profile, client_configuration):
		"Partitions local devices (hard drives, memory sticks, etc)"
		pass

	def mount_local_partitions(self, install_profile, client_configuration):
		"Mounts all partitions that are on the local machine"
		pass

	def mount_network_shares(self, install_profile, client_configuration):
		"Mounts all network shares to the local machine"
		pass

	def unpack_tarball(self, install_profile, client_configuration):
		"Unpacks the appropriate stage tarball"
		pass

	def fetch_sources_from_cd(self, install_profile, client_configuration):
		"Gets sources from CD (required for non-network installation)"
		pass

	def fetch_grp_from_cd(self, install_profile, client_configuration):
		"Gets grp binary packages from CD (required for non-network binary installation)"
		pass

	def prepare_chroot(self, install_profile, client_configuration):
		"Copies resolve.conf to the chroot environment and mounts /dev and /proc"
		pass

	def configure_make_conf(self, install_profile, client_configuration):
		"Configures make.conf"
		pass

	def emerge_sync(self, install_profile, client_configuration):
		"Get/update the portage tree"
		pass

	def bootstrap(self, install_profile, client_configuration):
		"Stage 1 install -- bootstraping"
		pass

	def emerge_system(self, install_profile, client_configuration):
		"Stage 1 and 2 install -- build system"
		pass

	def set_timezone(self, install_profile, client_configuration):
		"Sets the timezone for the new environment"
		pass

	def configure_fstab(self, install_profile, client_configuration):
		"Configures fstab"
		pass

	def emerge_kernel_sources(self, install_profile, client_configuration):
		"Fetches desired kernel sources"
		pass

	def build_kernel(self, install_profile, client_configuration):
		"Builds kernel"
		pass

	def setup_network_post(self, install_profile, client_configuration):
		"Sets up the network for the first boot"
		pass

	def install_system_utilities(self, install_profile, client_configuration):
		"Installs and sets up logger, cron, fstools, rp-pppoe, pcmcia-cs"
		pass

	def install_bootloader(self, install_profile, client_configuration):
		"Installs and configures bootloader"
		pass

	def configure_rc_conf(self, install_profile, client_configuration):
		"Configures rc.conf"
		pass

	def update_config_files(self, install_profile, client_configuration):
		"Runs etc-update (overwriting all config files), then re-configures the modified ones"
		pass

	def set_root_password(self, install_profile, client_configuration):
		"Sets the root password"
		pass

	def set_users(self, install_profile, client_configuration):
		"Sets up the new users for the system"
		pass

	def unmount_devices(self, install_profile, client_configuration):
		"Unmounts mounted devices after installation"
