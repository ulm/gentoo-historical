import os, sys

class GLIInstallTemplate:

	_install_profile = None
	_client_configuration = None
	
	def __init__(self, install_profile, client_configuration):
		"Sets the install_profile and client_configuration referances"
		
		self._install_profile = install_profile
		self._client_configuration = client_configuration

	def _emerge_sync(self):
		"A private method to run emerge sync in the chroot environment"
		
		# Run the sync and return the exitstatus
		return self._exec_in_chroot("emerge sync")
		
	def _emerge(self, package, binary=False, binary_only=False):
		"A private method to emerge a program in the chroot environment"
		
		# Decide which to run
		if binary:
			return self._exec_in_chroot("emerge -k " + package)
		elif binary_only:
			return self._exec_in_chroot("emerge -K " + package)
		else:
			return self._exec_in_chroot("emerge " + package)	

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

	def _exec_in_chroot(self, command):
		"Runs a command in the chroot environment."

		# Chroot needs to be in a child process
		pid = fork()

		# If you are the child process
		if pid == 0:

			# Chroot to /mnt/gentoo and run the command, then exit
			os.chroot("/mnt/gentoo")
			exitstatus = os.system(command)
			sys.exit(exitstatus)

		# If you are the parent process, just wait for the child
		# Kids can be so slow sometimes... 
		else:
			child_exitstatus = os.wait()[1]
			return(child_exitstatus)

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

	def setup_network_pre(self):
		"Sets up the network on the live CD environment"
		pass

	def partition_local_devices(self):
		"Partitions local devices (hard drives, memory sticks, etc)"
		pass

	def mount_local_partitions(self):
		"Mounts all partitions that are on the local machine"
		pass

	def mount_network_shares(self):
		"Mounts all network shares to the local machine"
		pass

	def unpack_tarball(self):
		"Unpacks the appropriate stage tarball"
		pass

	def fetch_sources_from_cd(self):
		"Gets sources from CD (required for non-network installation)"
		pass

	def fetch_grp_from_cd(self):
		"Gets grp binary packages from CD (required for non-network binary installation)"
		pass

	def prepare_chroot(self):
		"Copies resolve.conf to the chroot environment and mounts /dev and /proc"
		pass

	def configure_make_conf(self):
		"Configures make.conf"
		pass

	def emerge_sync(self):
		"Get/update the portage tree"
		pass

	def bootstrap(self):
		"Stage 1 install -- bootstraping"
		pass

	def emerge_system(self):
		"Stage 1 and 2 install -- build system"
		pass

	def set_timezone(self):
		"Sets the timezone for the new environment"
		
		self._depends("unpack_tarball")
		
		# Set symlink
		os.symlink("../usr/share/zoneinfo/" + self._install_profile.get_time_zone(), "/mnt/gentoo/etc/localtime")

	def configure_fstab(self):
		"Configures fstab"
		pass

	def emerge_kernel_sources(self):
		"Fetches desired kernel sources"
		pass

	def build_kernel(self):
		"Builds kernel"
		pass

	def setup_network_post(self):
		"Sets up the network for the first boot"
		pass

	def install_system_utilities(self):
		"Installs and sets up logger, cron, fstools, rp-pppoe, pcmcia-cs"
		pass

	def install_bootloader(self):
		"Installs and configures bootloader"
		pass

	def configure_rc_conf(self):
		"Configures rc.conf"
		pass

	def update_config_files(self):
		"Runs etc-update (overwriting all config files), then re-configures the modified ones"
		pass

	def set_root_password(self):
		"Sets the root password"
		pass

	def set_users(self):
		"Sets up the new users for the system"
		pass

	def unmount_devices(self):
		"Unmounts mounted devices after installation"
