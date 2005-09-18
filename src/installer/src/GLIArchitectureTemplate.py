"""
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
Gentoo Linux Installer

$Id: GLIArchitectureTemplate.py,v 1.204 2005/09/18 01:13:21 codeman Exp $

The ArchitectureTemplate is largely meant to be an abstract class and an 
interface (yes, it is both at the same time!). The purpose of this is to create 
subclasses that populate all the methods with working methods for that architecture. 
The only definitions that are filled in here are architecture independent. 

"""

import GLIUtility, GLILogger, os, string, sys, shutil, re, time
from GLIException import *

class ArchitectureTemplate:
	##
	# Initialization of the ArchitectureTemplate.  Called from some other arch template.
	# @param selfconfiguration=None    A Client Configuration
	# @param install_profile=None      An Install Profile
	# @param client_controller=None    Client Controller.  not same as configuration.
	def __init__(self,configuration=None, install_profile=None, client_controller=None):
		self._client_configuration = configuration
		self._install_profile = install_profile
		self._cc = client_controller

		# This will get used a lot, so it's probably
		# better to store it in a variable than to call
		# this method 100000 times.
		self._chroot_dir = self._client_configuration.get_root_mount_point()
		self._logger = GLILogger.Logger(self._client_configuration.get_log_file())
		self._compile_logfile = "/tmp/compile_output.log"
		
		# This will cleanup the logfile if it's a dead link (pointing
		# to the chroot logfile when partitions aren't mounted, else
		# no action needs to be taken

		if os.path.islink(self._compile_logfile) and not os.path.exists(self._compile_logfile):
			os.unlink(self._compile_logfile)

		# cache the list of successfully mounted swap devices here
		self._swap_devices = []

		# These must be filled in by the subclass. _steps is a list of
		# functions, that will carry out the installation. They must be
		# in order.
		#
		# For example, self._steps might be: [preinstall, stage1, stage2, stage3, postinstall],
		# where each entry is a function (with no arguments) that carries out the desired actions.
		# Of course, steps will be different depending on the install_profile

		self._architecture_name = "generic"
		self._install_steps = [
								 (self.partition, "Partition"),
								 (self.mount_local_partitions, "Mount local partitions"),
								 (self.mount_network_shares, "Mount network (NFS) shares"),
								 (self.unpack_stage_tarball, "Unpack stage tarball"),
								 (self.update_config_files, "Updating config files"),
								 (self.configure_make_conf, "Configure /etc/make.conf"),
								 (self.prepare_chroot, "Preparing chroot"),
								 (self.install_portage_tree, "Syncing the Portage tree"),
								 (self.stage1, "Performing bootstrap"),
								 (self.stage2, "Performing 'emerge system'"),
								 (self.set_root_password, "Set the root password"),
								 (self.set_timezone, "Setting timezone"),
								 (self.emerge_kernel_sources, "Emerge kernel sources"),
								 (self.build_kernel, "Building kernel"),
								 (self.install_distcc, "Install distcc"),
								 (self.install_mta, "Installing MTA"),
								 (self.install_logging_daemon, "Installing system logger"),
								 (self.install_cron_daemon, "Installing Cron daemon"),
								 (self.install_filesystem_tools, "Installing filesystem tools"),
								 (self.setup_network_post, "Configuring post-install networking"),
								 (self.install_bootloader, "Configuring and installing bootloader"),
								 (self.update_config_files, "Re-Updating config files"),
#                                 (self.configure_rc_conf, "Updating /etc/rc.conf"),
                                 (self.set_users, "Add additional users."),
                                 (self.install_packages, "Installing additional packages."),
				 # services for startup need to come after installing extra packages
				 # otherwise some of the scripts will not exist.
                                 (self.set_services, "Setting up services for startup"),
                                 (self.run_post_install_script, "Running custom post-install script"),
                                 (self.finishing_cleanup, "Cleanup and unmounting local filesystems.")
                                ]


	##
	# Returns the steps and their comments in an array
	def get_install_steps(self):
		return self._install_steps

	##
	# Tells the frontend something
	# @param type type of data
	# @param data the data itself.  usually a number.
	def notify_frontend(self, type, data):
		self._cc.addNotification(type, data)

	# It is possible to override these methods in each Arch Template.
	# It might be necessary to do so, if the arch needs something 'weird'.

	##
	# Private function to add a /etc/init.d/ script to the given runlevel in the chroot environement
	# @param script_name the script to be added
	# @param runlevel="default" the runlevel to add to
	def _add_to_runlevel(self, script_name, runlevel="default"):
		if not GLIUtility.is_file(self._chroot_dir + '/etc/init.d/' + script_name):
			#raise GLIException("RunlevelAddError", 'fatal', '_add_to_runlevel', "Failure adding " + script_name + " to runlevel " + runlevel + "!")
			#This is not a fatal error.  If the init script is important it will exist.
			self._logger.log("ERROR! Failure adding" + script_name + " to runlevel " + runlevel + " because it was not found!")
		status = GLIUtility.spawn("rc-update add " + script_name + " " + runlevel, display_on_tty8=True, chroot=self._chroot_dir, logfile=self._compile_logfile, append_log=True)
		if not GLIUtility.exitsuccess(status):
			#raise GLIException("RunlevelAddError", 'fatal', '_add_to_runlevel', "Failure adding " + script_name + " to runlevel " + runlevel + "!")
			#Again, an error here will not prevent a new system from booting.  But it is important to log the error.
			self._logger.log("ERROR! Could not add " + script_name + " to runlevel " + runlevel + ". returned a bad status code.")
		else:
			self._logger.log("Added "+script_name+" to runlevel "+runlevel)

	##
	# Private Function.  Will return a list of packages to be emerged for a given command.  Not yet used.
	# @param cmd full command to run ('/usr/portage/scripts/bootstrap.sh --pretend' or 'emerge -p system')
	def _get_packages_to_emerge(self, cmd):
#		self._logger.log("_get_packages_to_emerge() called with '%s'" % cmd)
		return GLIUtility.spawn(cmd + r" 2>/dev/null | grep -e '\[ebuild' | sed -e 's:\[ebuild .\+ \] ::' -e 's: \[.\+\] ::' -e 's: \+$::'", chroot=self._chroot_dir, return_output=True)[1].strip().split("\n")

	##
	# Private function.  For binary installs it will attempt to quickpkg packages that are on the livecd.
	# @param package package to be quickpkg'd.
	def _quickpkg_deps(self, package, nodeps=False):
#		self._logger.log("_quickpkg_deps() called with '%s'" % package)
		PKGDIR = "/usr/portage/packages"
		PORTAGE_TMPDIR = "/var/tmp"
		make_conf = self._install_profile.get_make_conf()
		if "PKGDIR" in make_conf and make_conf['PKGDIR']: PKGDIR = make_conf['PKGDIR']
		if "PORTAGE_TMPDIR" in make_conf and make_conf['PORTAGE_TMPDIR']: PORTAGE_TMPDIR = make_conf['PORTAGE_TMPDIR']
		GLIUtility.spawn("mkdir -p " + self._chroot_dir + PKGDIR, logfile=self._compile_logfile, append_log=True)
		GLIUtility.spawn("mkdir -p " + self._chroot_dir + PORTAGE_TMPDIR, logfile=self._compile_logfile, append_log=True)
		if nodeps:
			packages = package.split()
		else:
			packages = self._get_packages_to_emerge("emerge -p " + package)
#		self._logger.log("packages obtained from _get_packages_to_emerge(): %s" % str(packages))
		for pkg in packages:
			if not pkg: continue
			self._logger.log("Trying to quickpkg '" + pkg + "'")
			pkgparts = pkg.split('/')
			if not len(pkgparts) == 2: continue
			if not GLIUtility.is_file(self._chroot_dir + PKGDIR + "/All/" + pkgparts[1] + ".tbz2"):
				ret = GLIUtility.spawn("env PKGDIR='" + self._chroot_dir + PKGDIR + "' PORTAGE_TMPDIR='" + self._chroot_dir + PORTAGE_TMPDIR + "' quickpkg =" + pkg)
				if not GLIUtility.exitsuccess(ret):
					# This package couldn't be quickpkg'd. This may be an error in the future
					pass

	##
	# Private Function.  Will emerge a given package in the chroot environment.
	# @param package package to be emerged
	# @param binary=False defines whether to try a binary emerge (if GRP this gets ignored either way)
	# @param binary_only=False defines whether to only allow binary emerges.
	def _emerge(self, package, binary=True, binary_only=False, quickpkg=True):
		#Error checking of this function is to be handled by the parent function.
#		self._logger.log("_emerge() called with: package='%s', binary='%s', binary_only='%s', grp_install='%s'" % (package, str(binary), str(binary_only), str(self._install_profile.get_grp_install())))
		# now short-circuit for GRP
		if self._install_profile.get_grp_install():
			if quickpkg:
				self._quickpkg_deps(package)
			cmd="emerge -k " + package
		# now normal installs
		else:
			if binary_only:
				cmd="emerge -K " + package
			elif binary:
				cmd="emerge -k " + package
			else:
				cmd="emerge " + package

		self._logger.log("Calling emerge: "+cmd)
		return GLIUtility.spawn(cmd, display_on_tty8=True, chroot=self._chroot_dir, logfile=self._compile_logfile, append_log=True)

	##
	# Returns the full version of a package to be emerged when given a short name
	# @param package short name of package (i.e. xorg-x11)
	def _portage_best_visible(self, package):
		return GLIUtility.spawn("portageq best_visible / " + package, chroot=self._chroot_dir, return_output=True)[1].strip()

	##
	# Private Function.  Will edit a config file and insert a value or two overwriting the previous value
	# (actually it only just comments out the old one)
	# @param filename 			file to be edited
	# @param newvalues 			a dictionary of VARIABLE:VALUE pairs
	# @param delimeter='=' 			what is between the key and the value
	# @param quotes_around_value=True 	whether there are quotes around the value or not (ex. "local" vs. localhost)
	# @param only_value=False		Ignore the keys and output only a value.
	# @param create_file=True		Create the file if it does not exist.
	def _edit_config(self, filename, newvalues, delimeter='=', quotes_around_value=True, only_value=False,create_file=True):
		# don't use 'file' as a normal variable as it conflicts with the __builtin__.file
		newvalues = newvalues.copy()
		self._logger.log("_edit_config() called with " + str(newvalues))
		if GLIUtility.is_file(filename):
			f = open(filename)
			contents = f.readlines()
			f.close()
		elif create_file:
			contents = []
		else:
			raise GLIException("NoSuchFileError", 'notice','_edit_config',filename + ' does not exist!')
	
		for key in newvalues.keys():
			regexpr = '^\s*#?\s*' + key + '\s*' + delimeter + '.*$'
			regexpr = re.compile(regexpr)
	
			for i in range(0, len(contents)):
				if regexpr.match(contents[i]):
					if not contents[i][0] == '#':
						contents[i] = '#' + contents[i]
	
			##contents.append('\n# Added by GLI\n')
			##commentprefix = "" ##unused
			if key == "SPACER":
				contents.append('\n')
			elif key == "COMMENT":
				contents.append('# ' + newvalues[key] + '\n')
			elif newvalues[key] == "##comment##" or newvalues[key] == "##commented##":
				contents.append('#' + key + delimeter + '""' + "\n")
			else:
				if quotes_around_value:
					newvalues[key] = '"' + newvalues[key] + '"'
				#Only the printing of values is required.
				if only_value:
					contents.append(newvalues[key] + '\n')
				else:
					contents.append(key + delimeter + newvalues[key]+'\n')
	
		f = open(filename,'w')
		f.writelines(contents)
		f.flush()
		f.close()
		self._logger.log("Edited Config file "+filename)

	##
	# Stage 1 install -- bootstraping the system
	# If we are doing a stage 1 install, then bootstrap 
	def stage1(self):
		if self._install_profile.get_install_stage() == 1:
			self._logger.mark()
			self._logger.log("Starting bootstrap.")
			pkgs = self._get_packages_to_emerge("/usr/portage/scripts/bootstrap.sh --pretend")
			exitstatus = GLIUtility.spawn("/usr/portage/scripts/bootstrap.sh", chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("Stage1Error", 'fatal','stage1', "Bootstrapping failed!")
			self._logger.log("Bootstrap complete.")

	##
	# Stage 2 install -- emerge -e system
	# If we are doing a stage 1 or 2 install, then emerge system
	def stage2(self):
		if self._install_profile.get_install_stage() in [ 1, 2 ]:
			self._logger.mark()
			self._logger.log("Starting emerge system.")
			pkgs = self._get_packages_to_emerge("emerge -p system")  #currently quite the useless
			exitstatus = self._emerge("--emptytree system")
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("Stage2Error", 'fatal','stage2', "Building the system failed!")
			self._logger.log("Emerge system complete.")

	##
	# Unpacks the stage tarball that has been specified in the profile (it better be there!)
	def unpack_stage_tarball(self):
		if not os.path.isdir(self._chroot_dir):
			os.makedirs(self._chroot_dir)
		if self._install_profile.get_install_stage() == 3 and self._install_profile.get_dynamic_stage3():
			# stage3 generation code here
			if not GLIUtility.is_file("/usr/livecd/systempkgs.txt"):
				raise GLIException("CreateStage3Error", "fatal", "unpack_stage_tarball", "Required file /usr/livecd/systempkgs.txt does not exist")
			make_conf = self._install_profile.get_make_conf()
			PKGDIR = '/usr/portage/packages'
			PORTAGE_TMPDIR = '/var/tmp'
			if 'PKGDIR' in make_conf: PKGDIR = make_conf['PKGDIR']
			if 'PORTAGE_TMPDIR' in make_conf: PORTAGE_TMPDIR = make_conf['PORTAGE_TMPDIR']
			GLIUtility.spawn("mkdir -p " + self._chroot_dir + PKGDIR)
			GLIUtility.spawn("mkdir -p " + self._chroot_dir + PORTAGE_TMPDIR)
			os.environ["PKGDIR"] = self._chroot_dir + PKGDIR
			os.environ["PORTAGE_TMPDIR"] = self._chroot_dir + PORTAGE_TMPDIR
			ret = GLIUtility.spawn("quickpkg $(sed -e 's:^:=:' /usr/livecd/systempkgs.txt)", display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if not GLIUtility.exitsuccess(ret):
				raise GLIException("CreateStage3Error", "fatal", "unpack_stage_tarball", "Could not quickpkg necessary packages for generating stage3")
			ret = GLIUtility.spawn("env ROOT=" + self._chroot_dir + " emerge -KO $(sed -e 's:^:=:' /usr/livecd/systempkgs.txt)", display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if not GLIUtility.exitsuccess(ret):
				raise GLIException("CreateStage3Error", "fatal", "unpack_stage_tarball", "Could not emerge necessary packages in chroot for generating stage3")
			del os.environ["PKGDIR"]
			del os.environ["PORTAGE_TMPDIR"]
			GLIUtility.spawn("cp /etc/make.conf " + self._chroot_dir + "/etc/make.conf")
			GLIUtility.spawn("ln -s `readlink /etc/make.profile` " + self._chroot_dir + "/etc/make.profile")
			GLIUtility.spawn("cp -f /etc/inittab.old " + self._chroot_dir + "/etc/inittab")
			chrootscript = r"""
			#!/bin/bash

			source /etc/make.conf
			export LDPATH="/usr/lib/gcc-lib/${CHOST}/$(cd /usr/lib/gcc-lib/${CHOST} && ls -1 | head -n 1)"

			ldconfig $LDPATH
			gcc-config 1
			env-update
			source /etc/profile
			modules-update
			[ -f /usr/bin/binutils-config ] && binutils-config 1
			source /etc/profile
			mount -t proc none /proc
			cd /dev
			/sbin/MAKEDEV generic-i386
			umount /proc
			"""
			script = open(self._chroot_dir + "/tmp/extrastuff.sh", "w")
			script.write(chrootscript)
			script.close()
			GLIUtility.spawn("chmod 755 /tmp/extrastuff.sh && /tmp/extrastuff.sh", chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			GLIUtility.spawn("rm -rf /var/tmp/portage/* /usr/portage /tmp/*", chroot=self._chroot_dir)
			self._logger.log("Stage3 was generated successfully")
		else:
			GLIUtility.fetch_and_unpack_tarball(self._install_profile.get_stage_tarball_uri(), self._chroot_dir, temp_directory=self._chroot_dir, keep_permissions=True)
			self._logger.log(self._install_profile.get_stage_tarball_uri()+" was unpacked.")

	##
	# Prepares the Chroot environment by copying /etc/resolv.conf and mounting proc and dev
	def prepare_chroot(self):
		# Copy resolv.conf to new env
		try:
			shutil.copy("/etc/resolv.conf", self._chroot_dir + "/etc/resolv.conf")
		except:
			pass
		ret = GLIUtility.spawn("mount -t proc none "+self._chroot_dir+"/proc")
		if not GLIUtility.exitsuccess(ret):
			raise GLIException("MountError", 'fatal','prepare_chroot','Could not mount /proc')
		bind_mounts = [ '/dev', '/dev/shm', '/dev/pts' ]
		uname = os.uname()
		if uname[0] == 'Linux' and uname[2].split('.')[1] == '6':
			bind_mounts.append('/sys')
		for mount in bind_mounts:
			ret = GLIUtility.spawn('mount -o bind %s %s%s' % (mount,self._chroot_dir,mount))
			if not GLIUtility.exitsuccess(ret):
				raise GLIException("MountError", 'fatal','prepare_chroot','Could not mount '+mount)
		GLIUtility.spawn("mv " + self._compile_logfile + " " + self._chroot_dir + self._compile_logfile + " && ln -s " + self._chroot_dir + self._compile_logfile + " " + self._compile_logfile)
		self._logger.log("Chroot environment ready.")

	##
	# Installs a list of packages specified in the profile. Will install any extra software!
	# In the future this function will lead to better things.  It may even wipe your ass for you.
	def install_packages(self):
		installpackages = self._install_profile.get_install_packages()
		failed_list = []
		installpackages2 = []
		for package in installpackages:
#			self._logger.log("Determing best_visible for package " + package)
			tmppkg = self._portage_best_visible(package)
			if not tmppkg:
				self._logger.log("Cannot determine best_visible for package '" + package + "'...skipping")
			else:
#				self._logger.log("best_visible for package '" + package + "' is " + tmppkg)
				installpackages2.append(tmppkg)
		if not installpackages2:
#			self._logger.log("Nothing in installpackages2 to emerge")
			return
		all_packages = self._get_packages_to_emerge("emerge -p =" + " =".join(installpackages2))
		self._quickpkg_deps(" ".join(all_packages), nodeps=True)

		# This is here until I figure out why some packages are missed during quickpkg'ing
		more_packages = self._get_packages_to_emerge("emerge -pk =" + " =".join(installpackages2))
		self._quickpkg_deps(" ".join(more_packages), nodeps=True)

		for i, package in enumerate(all_packages):
			self.notify_frontend("progress", (float(i) / len(all_packages), "Emerging " + package))
			#look for special cases first:
			if package == "pcmcia-cs":
				self.install_pcmcia_cs()
			else:
				self._logger.log("Starting emerge " + package)
				if package in installpackages2:
					status = self._emerge("=" + package, quickpkg=False)
				else:
					status = self._emerge("-1 =" + package, quickpkg=False)
				if not GLIUtility.exitsuccess(status):
					self._logger.log("Could not emerge " + package + "!")
					failed_list.append(package)
				else:
					self._logger.log("Emerged package: " + package)
		# error checking is important!
		if len(failed_list) > 0:
			self._logger.log("ERROR! Could not emerge " + str(failed_list) + "!")
			
		if GLIUtility.is_file(self._chroot_dir+"/etc/X11"):
			#Now copy the XF86Config
			exitstatus = GLIUtility.spawn("cp /etc/X11/xorg.conf " + self._chroot_dir + "/etc/X11/xorg.conf")
			if not GLIUtility.exitsuccess(exitstatus):
				self._logger.log("Could NOT copy the xorg configuration from the livecd to the new system!")
			else:
				self._logger.log("xorg.conf copied to new system.  X should be ready to roll!")

	##
	# Will set the list of services to runlevel default.  This is a temporary solution!
	def set_services(self):
		services = self._install_profile.get_services()
		for service in services:
			self._add_to_runlevel(service)
				
	##
	# Will grab partition info from the profile and mount all partitions with a specified mountpoint (and swap too)
	def mount_local_partitions(self):
		#{   1: {   'end': 1999871,          'format': False,            'mb': 0,
		#'mountopts': '',   'mountpoint': '',   'start': 63,    'type': 'linux-swap'},
		#2: {   'end': 240121727, 'format': False,  'mb': 0, 'mountopts': '',  
		#'mountpoint': '',  'start': 1999872,  'type': 'ext3'}}
		
		parts = self._install_profile.get_partition_tables()
		parts_to_mount = {}
		for device in parts:
			tmp_partitions = parts[device].get_install_profile_structure()
			tmp_minor = -1
			for minor in tmp_partitions:
				if not tmp_partitions[minor]['type'] == "free":
					tmp_minor = minor
					break
			time.sleep(1)
			if tmp_minor == -1: continue
			# now sleep until it exists
			while not GLIUtility.is_file(parts[device].get_device() + str(tmp_minor)):
				self._logger.log("Waiting for device node " + parts[device].get_device() + str(tmp_minor) + " to exist...")
				time.sleep(1)
			# one bit of extra sleep is needed, as there is a blip still
			time.sleep(1)
			for partition in tmp_partitions:
				mountpoint = tmp_partitions[partition]['mountpoint']
				mountopts = tmp_partitions[partition]['mountopts']
				minor = str(int(tmp_partitions[partition]['minor']))
				partition_type = tmp_partitions[partition]['type']
				if mountpoint:
					if mountopts:
						mountopts = "-o " + mountopts + " "
					if partition_type:
						partition_type = "-t " + partition_type + " "
					parts_to_mount[mountpoint]= (mountopts, partition_type, device + minor)
					
				if partition_type == "linux-swap":
					ret = GLIUtility.spawn("swapon " + device + minor)
					if not GLIUtility.exitsuccess(ret):
						self._logger.log("ERROR! : Could not activate swap (" + device + minor + ")!")
					#	raise GLIException("MountError", 'warning','mount_local_partitions','Could not activate swap')
					else:
						self._swap_devices.append(device + minor)
		sorted_list = parts_to_mount.keys()
		sorted_list.sort()
		
		if not GLIUtility.is_file(self._chroot_dir):
			exitstatus = GLIUtility.spawn("mkdir -p " + self._chroot_dir)
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("MkdirError", 'fatal','mount_local_partitions', "Making the ROOT mount point failed!")
			else:
				self._logger.log("Created root mount point")
		for mountpoint in sorted_list:
			mountopts = parts_to_mount[mountpoint][0]
			partition_type = parts_to_mount[mountpoint][1]
			partition = parts_to_mount[mountpoint][2]
			if not GLIUtility.is_file(self._chroot_dir + mountpoint):
				exitstatus = GLIUtility.spawn("mkdir -p " + self._chroot_dir + mountpoint)
				if not GLIUtility.exitsuccess(exitstatus):
					raise GLIException("MkdirError", 'fatal','mount_local_partitions', "Making the mount point failed!")
				else:
					self._logger.log("Created mountpoint" + mountpoint)
			ret = GLIUtility.spawn("mount " + partition_type + mountopts + partition + " " + self._chroot_dir + mountpoint, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if not GLIUtility.exitsuccess(ret):
				raise GLIException("MountError", 'fatal','mount_local_partitions','Could not mount a partition')
			# double check in /proc/mounts
			# This current code doesn't work and needs to be fixed, because there is a case that it is needed for - robbat2
			#ret, output = GLIUtility.spawn('awk \'$2 == "%s" { print "Found" }\' /proc/mounts | head -n1' % (self._chroot_dir + mountpoint), display_on_tty8=True, return_output=True)
			#if output.strip() != "Found":
			#	raise GLIException("MountError", 'fatal','mount_local_partitions','Could not mount a partition (failed in double-check)')
			self._logger.log("Mounted mountpoint: " + mountpoint)

	##
	# Mounts all network shares to the local machine
	def mount_network_shares(self):
		"""
		<agaffney> it'll be much easier than mount_local_partitions
		<agaffney> make sure /etc/init.d/portmap is started
		<agaffney> then mount each one: mount -t nfs -o <mountopts> <host>:<export> <mountpoint>
		"""
		nfsmounts = self._install_profile.get_network_mounts()
		for netmount in nfsmounts:
			if netmount['type'] == "NFS" or netmount['type'] == "nfs":
				mountopts = netmount['mountopts']
				if mountopts:
					mountopts = "-o " + mountopts
				host = netmount['host']
				export = netmount['export']
				mountpoint = netmount['mountpoint']
				if not GLIUtility.is_file(self._chroot_dir + mountpoint):
					exitstatus = GLIUtility.spawn("mkdir -p " + self._chroot_dir + mountpoint)
					if not GLIUtility.exitsuccess(exitstatus):
						raise GLIException("MkdirError", 'fatal','mount_network_shares', "Making the mount point failed!")
				ret = GLIUtility.spawn("mount -t nfs " + mountopts + " " + host + ":" + export + " " + self._chroot_dir + mountpoint, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
				if not GLIUtility.exitsuccess(ret):
					raise GLIException("MountError", 'fatal','mount_network_shares','Could not mount an NFS partition')
				self._logger.log("Mounted netmount at mountpoint: " + mountpoint)
			else:
				self._logger.log("Netmount type " + netmount['type'] + " not supported...skipping " + netmount['mountpoint'])


	##
	# Configures the new /etc/make.conf
	def configure_make_conf(self):
		# Get make.conf options
		make_conf = self._install_profile.get_make_conf()
		
		# For each configuration option...
		filename = self._chroot_dir + "/etc/make.conf"
		self._edit_config(filename, {"COMMENT": "GLI additions ===>"})
		for key in make_conf.keys():
			# Add/Edit it into make.conf
			self._edit_config(filename, {key: make_conf[key]})
		self._edit_config(filename, {"COMMENT": "<=== End GLI additions"})

		self._logger.log("Make.conf configured")
		# now make any directories that emerge needs, otherwise it will fail
		# this must take place before ANY calls to emerge.
		# otherwise emerge will fail (for PORTAGE_TMPDIR anyway)
		# defaults first
		# this really should use portageq or something.
		PKGDIR = '/usr/portage/packages'
		PORTAGE_TMPDIR = '/var/tmp'
		PORT_LOGDIR = None
		PORTDIR_OVERLAY = None
		# now other stuff
		if 'PKGDIR' in make_conf: PKGDIR = make_conf['PKGDIR']
		if 'PORTAGE_TMPDIR' in make_conf: PORTAGE_TMPDIR = make_conf['PORTAGE_TMPDIR']
		if 'PORT_LOGDIR' in make_conf: PORT_LOGDIR = make_conf['PORT_LOGDIR']
		if 'PORTDIR_OVERLAY' in make_conf: PORTDIR_OVERLAY = make_conf['PORTDIR_OVERLAY']
		GLIUtility.spawn("mkdir -p " + self._chroot_dir + PKGDIR, logfile=self._compile_logfile, append_log=True)
		GLIUtility.spawn("mkdir -p " + self._chroot_dir + PORTAGE_TMPDIR, logfile=self._compile_logfile, append_log=True)
		if PORT_LOGDIR != None: 
			GLIUtility.spawn("mkdir -p " + self._chroot_dir + PORT_LOGDIR, logfile=self._compile_logfile, append_log=True)
		if PORTDIR_OVERLAY != None: 
			GLIUtility.spawn("mkdir -p " + self._chroot_dir + PORTDIR_OVERLAY, logfile=self._compile_logfile, append_log=True)

	##
	# This will get/update the portage tree.  If you want to snapshot or mount /usr/portage use "custom".
	def install_portage_tree(self):
		# Check the type of portage tree fetching we'll do
		# If it is custom, follow the path to the custom tarball and unpack it

		# This is a hack to copy the LiveCD's rsync into the chroot since it has the sigmask patch
		GLIUtility.spawn("cp -a /usr/bin/rsync " + self._chroot_dir + "/usr/bin/rsync")
		GLIUtility.spawn("cp -a /usr/lib/libpopt* " + self._chroot_dir + "/usr/lib")
		
		sync_type = self._install_profile.get_portage_tree_sync_type()
		if sync_type == "snapshot" or sync_type == "custom": # Until this is finalized
		
			# Get portage tree info
			portage_tree_snapshot_uri = self._install_profile.get_portage_tree_snapshot_uri()
			if portage_tree_snapshot_uri:
				# Fetch and unpack the tarball
				GLIUtility.fetch_and_unpack_tarball(portage_tree_snapshot_uri, self._chroot_dir + "/usr/", self._chroot_dir + "/")
			self._logger.log("Portage tree install was custom.")
		elif sync_type == "sync":
				exitstatus = GLIUtility.spawn("emerge sync", chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
				if not GLIUtility.exitsuccess(exitstatus):
					self._logger.log("ERROR!  Could not sync the portage tree using emerge sync.  Falling back to emerge-webrsync as a backup.")
					sync_type = "webrsync"
				else:
					self._logger.log("Portage tree sync'd")
		# If the type is webrsync, then run emerge-webrsync
		elif sync_type == "webrsync":
			exitstatus = GLIUtility.spawn("emerge-webrsync", chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("EmergeWebRsyncError", 'fatal','install_portage_tree', "Failed to retrieve portage tree using webrsync!")
			self._logger.log("Portage tree sync'd using webrsync")
		# Otherwise, spit out a message because its probably a bad thing.
		else:
			self._logger.log("NOTICE!  No valid portage tree sync method was selected.  This will most likely result in a failed installation unless the tree is mounted.")
			
	##
	# Sets the timezone for the new environment
	def set_timezone(self):
		
		# Set symlink
		if os.access(self._chroot_dir + "/etc/localtime", os.W_OK):
			GLIUtility.spawn("rm "+self._chroot_dir + "/etc/localtime")
		GLIUtility.spawn("ln -s ../usr/share/zoneinfo/" + self._install_profile.get_time_zone() + " /etc/localtime", chroot=self._chroot_dir)
		if not (self._install_profile.get_time_zone() == "UTC"):
			self._edit_config(self._chroot_dir + "/etc/rc.conf", {"CLOCK":"local"})
		self._logger.log("Timezone set.")
		
	##
	# Configures /etc/fstab on the new envorinment 
	def configure_fstab(self):
		newfstab = ""
		parts = self._install_profile.get_partition_tables()
		for device in parts:
			tmp_partitions = parts[device].get_install_profile_structure()
			for partition in tmp_partitions:
				mountpoint = tmp_partitions[partition]['mountpoint']
				minor = str(int(tmp_partitions[partition]['minor']))
				partition_type = tmp_partitions[partition]['type']
				mountopts = tmp_partitions[partition]['mountopts']
				if not mountopts.strip(): mountopts = "defaults"
				if mountpoint:
					if not GLIUtility.is_file(self._chroot_dir+mountpoint):
						exitstatus = GLIUtility.spawn("mkdir -p " + self._chroot_dir + mountpoint)
						if not GLIUtility.exitsuccess(exitstatus):
							raise GLIException("MkdirError", 'fatal','configure_fstab', "Making the mount point failed!")
					newfstab += device+minor+"\t "+mountpoint+"\t "+partition_type+"\t "+mountopts+"\t\t "
					if mountpoint == "/boot":
						newfstab += "1 2\n"
					elif mountpoint == "/":
						newfstab += "0 1\n"
					else:
						newfstab += "0 0\n"
				if partition_type == "linux-swap":
					newfstab += device+minor+"\t none            swap            sw              0 0\n"
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
		self._logger.log("fstab configured.")

	##
	# Fetches desired kernel sources, unless you're using a livecd-kernel in which case it does freaky stuff.
	def emerge_kernel_sources(self):
		self._logger.log("Starting emerge_kernel")
		kernel_pkg = self._install_profile.get_kernel_source_pkg()
#		if kernel_pkg:
		# Special case, no kernel installed
		if kernel_pkg == "none":
			return
		# Special case, livecd kernel
		elif kernel_pkg == "livecd-kernel":
			PKGDIR = "/usr/portage/packages"
			PORTAGE_TMPDIR = "/var/tmp"
			make_conf = self._install_profile.get_make_conf()
			if "PKGDIR" in make_conf: PKGDIR = make_conf['PKGDIR']
			if "PORTAGE_TMPDIR" in make_conf: PORTAGE_TMPDIR = make_conf['PORTAGE_TMPDIR']
			# directories are created previously
			ret = GLIUtility.spawn("env PKGDIR=" + self._chroot_dir + PKGDIR + " PORTAGE_TMPDIR=" + self._chroot_dir + PORTAGE_TMPDIR + " quickpkg livecd-kernel")
			ret = GLIUtility.spawn("env PKGDIR=" + PKGDIR + " emerge -K sys-kernel/livecd-kernel", chroot=self._chroot_dir)
			# these should really be error-checked...
			
			#these are the hotplug/coldplug steps from build_kernel copied over here.  they will NOT be run there.
#			exitstatus = self._emerge("hotplug")
#			if not GLIUtility.exitsuccess(exitstatus):
#				raise GLIException("EmergeHotplugError", 'fatal','build_kernel', "Could not emerge hotplug!")
#			self._logger.log("Hotplug emerged.")
			exitstatus = self._emerge("coldplug")
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("EmergeColdplugError", 'fatal','build_kernel', "Could not emerge coldplug!")
			self._logger.log("Coldplug emerged.  Now they should be added to the default runlevel.")
			
#			self._add_to_runlevel("hotplug")
			self._add_to_runlevel("coldplug", runlevel="boot")
		# normal case
		else:
			exitstatus = self._emerge(kernel_pkg)
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("EmergeKernelSourcesError", 'fatal','emerge_kernel_sources',"Could not retrieve kernel sources!")
			try:
				os.stat(self._chroot_dir + "/usr/src/linux")
			except:
				kernels = os.listdir(self._chroot_dir+"/usr/src")
				found_a_kernel = False
				counter = 0
				while not found_a_kernel:
					if kernels[counter][0:6]=="linux-":
						exitstatus = GLIUtility.spawn("ln -s /usr/src/"+kernels[counter]+ " /usr/src/linux",chroot=self._chroot_dir)
						if not GLIUtility.exitsuccess(exitstatus):
							raise GLIException("EmergeKernelSourcesError", 'fatal','emerge_kernel_sources',"Could not make a /usr/src/linux symlink")
						found_a_kernel = True
					else:
						counter = counter + 1
			self._logger.log("Kernel sources:"+kernel_pkg+" emerged and /usr/src/linux symlinked.")

	##
	# Builds the kernel using genkernel or regularly if given a custom .config file in the profile
	def build_kernel(self):
		self._logger.mark()
		self._logger.log("Starting build_kernel")

		build_mode = self._install_profile.get_kernel_build_method()

		# No building necessary if using the LiveCD's kernel/initrd
		# or using the 'none' kernel bypass
		if self._install_profile.get_kernel_source_pkg() in ["livecd-kernel","none"]: 
			return
		# Get the uri to the kernel config
		kernel_config_uri = self._install_profile.get_kernel_config_uri()

		# is there an easier way to do this?
		ret, kernel_major = GLIUtility.spawn("awk '/^PATCHLEVEL/{print $3}' /usr/src/linux/Makefile",chroot=self._chroot_dir,return_output=True)
		# 6 == 2.6 kernel, 4 == 2.4 kernel
		kernel_major = int(kernel_major)
			
		#Copy the kernel .config to the proper location in /usr/src/linux
		if kernel_config_uri != '':
			try:
				GLIUtility.get_uri(kernel_config_uri, self._chroot_dir + "/var/tmp/kernel_config")
			except:
				raise GLIException("KernelBuildError", 'fatal', 'build_kernel', "Could not copy kernel config!")
			
		# the && stuff is important so that we can catch any errors.
		kernel_compile_script =  "#!/bin/bash\n"
		kernel_compile_script += "cp /var/tmp/kernel_config /usr/src/linux/.config && "
		kernel_compile_script += "cd /usr/src/linux && "
		# required for 2.[01234] etc kernels
		if kernel_major in [0,1,2,3,4]:
			kernel_compile_script += " yes 'n' | make oldconfig && make symlinks && make dep"
		# not strictly needed, but recommended by upstream
		else: #elif kernel_major in [5,6]:
			kernel_compile_script += "make prepare"
		
		# bypass to install a kernel, but not compile it
		if build_mode == "none":
			return
		# this mode is used to install kernel sources, and have then configured
		# but not actually build the kernel. This is needed for netboot
		# situations when you have packages that require kernel sources
		# to build.
		elif build_mode == "prepare-only":
			f = open(self._chroot_dir+"/var/tmp/kernel_script", 'w')
			f.writelines(kernel_compile_script)
			f.close()
			#Build the kernel
			exitstatus1 = GLIUtility.spawn("chmod u+x "+self._chroot_dir+"/var/tmp/kernel_script")
			exitstatus2 = GLIUtility.spawn("/var/tmp/kernel_script", chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if (exitstatus1 != 0) or (exitstatus2 != 0):
				raise GLIException("KernelBuildError", 'fatal', 'build_kernel', "Could not handle prepare-only build!")
						
			#i'm sure i'm forgetting something here.
			#cleanup
			exitstatus = GLIUtility.spawn("rm -f "+self._chroot_dir+"/var/tmp/kernel_script "+self._chroot_dir+"/var/tmp/kernel_config")
			#it's not important if this fails.
			self._logger.log("prepare-only build complete")
		# Genkernel mode, including custom kernel_config. Initrd always on.
		elif build_mode == "genkernel":  
			exitstatus = self._emerge("genkernel")
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("EmergeGenKernelError", 'fatal','build_kernel', "Could not emerge genkernel!")
			self._logger.log("Genkernel emerged.  Beginning kernel compile.")
			# Null the genkernel_options
			genkernel_options = ""
	
			# If the uri for the kernel config is not null, then
			if kernel_config_uri != "":
				GLIUtility.get_uri(kernel_config_uri, self._chroot_dir + "/var/tmp/kernel_config")
				genkernel_options = genkernel_options + " --kernel-config=/var/tmp/kernel_config"
				
			# Decide whether to use bootsplash or not
			if self._install_profile.get_kernel_bootsplash():
				genkernel_options = genkernel_options + " --bootsplash"
			else:
				genkernel_options = genkernel_options + " --no-bootsplash"
			# Run genkernel in chroot
			#print "genkernel all " + genkernel_options
			exitstatus = GLIUtility.spawn("genkernel all " + genkernel_options, chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("KernelBuildError", 'fatal', 'build_kernel', "Could not build kernel!")
			
#			exitstatus = self._emerge("hotplug")
#			if not GLIUtility.exitsuccess(exitstatus):
#				raise GLIException("EmergeHotplugError", 'fatal','build_kernel', "Could not emerge hotplug!")
#			self._logger.log("Hotplug emerged.")
			exitstatus = self._emerge("coldplug")
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("EmergeColdplugError", 'fatal','build_kernel', "Could not emerge coldplug!")
			self._logger.log("Coldplug emerged.  Now they should be added to the default runlevel.")
			
#			self._add_to_runlevel("hotplug")
			self._add_to_runlevel("coldplug", runlevel="boot")
			self._logger.log("Genkernel complete.")
		elif build_mode == "custom":  #CUSTOM CONFIG
			
			kernel_compile_script += " && make && make modules && make modules_install"

			#Ok now that it's built, copy it to /boot/kernel-* for bootloader code to find it
			if self._client_configuration.get_architecture_template() == "x86":
				kernel_compile_script += " && cp /usr/src/linux/arch/i386/boot/bzImage /boot/kernel-custom\n"
			elif self._client_configuration.get_architecture_template() == "amd64":
				kernel_compile_script += " && cp /usr/src/linux/arch/x86_64/boot/bzImage /boot/kernel-custom\n"
			elif self._client_configuration.get_architecture_template() == "ppc":
				kernel_compile_script += " && cp /usr/src/linux/vmlinux /boot/kernel-custom\n"
				
			f = open(self._chroot_dir+"/var/tmp/kernel_script", 'w')
			f.writelines(kernel_compile_script)
			f.close()
			#Build the kernel
			exitstatus1 = GLIUtility.spawn("chmod u+x "+self._chroot_dir+"/var/tmp/kernel_script")
			exitstatus2 = GLIUtility.spawn("/var/tmp/kernel_script", chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if (exitstatus1 != 0) or (exitstatus2 != 0):
				raise GLIException("KernelBuildError", 'fatal', 'build_kernel', "Could not build custom kernel!")
						
			#i'm sure i'm forgetting something here.
			#cleanup
			exitstatus = GLIUtility.spawn("rm -f "+self._chroot_dir+"/var/tmp/kernel_script "+self._chroot_dir+"/var/tmp/kernel_config")
			#it's not important if this fails.
			self._logger.log("Custom kernel complete")
			
	##
	# Installs and starts up distccd if the user has it set, so that it will get used for the rest of the install
	def install_distcc(self):
		if self._install_profile.get_install_distcc():
			exitstatus = GLIUtility.spawn("USE='-*' emerge --nodeps sys-devel/distcc", chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if not GLIUtility.exitsuccess(exitstatus):
				self._logger.log("ERROR! : Could not emerge distcc!")
			else:
				self._logger.log("distcc emerged.")	
	
	##
	# Installs mail MTA. Does not put into runlevel, as this is not simple with MTAs.
	def install_mta(self):
		# Get MTA info
		mta_pkg = self._install_profile.get_mta_pkg()
		if mta_pkg:
			# Emerge MTA
			exitstatus = self._emerge(mta_pkg)
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("MTAError", 'fatal','install_mta', "Could not emerge " + mta_pkg + "!")
			self._logger.log("MTA installed: "+mta_pkg)

	##
	# Installs and sets up logging daemon on the new system.  adds to runlevel too.
	def install_logging_daemon(self):
		
		# Get loggin daemon info
		logging_daemon_pkg = self._install_profile.get_logging_daemon_pkg()
		if logging_daemon_pkg:
			# Emerge Logging Daemon
			exitstatus = self._emerge(logging_daemon_pkg)
			if not GLIUtility.exitsuccess(exitstatus):
				raise GLIException("LoggingDaemonError", 'fatal','install_logging_daemon', "Could not emerge " + logging_daemon_pkg + "!")

			# Add Logging Daemon to default runlevel
			# After we find the name of it's initscript
			# This current code is a hack, and should be better.
			initscript = logging_daemon_pkg[(logging_daemon_pkg.find('/')+1):]
			self._add_to_runlevel(initscript)
			self._logger.log("Logging daemon installed: "+logging_daemon_pkg)
	##
	# Installs and sets up cron package.
	def install_cron_daemon(self):
		# Get cron daemon info
		cron_daemon_pkg = self._install_profile.get_cron_daemon_pkg()
		if cron_daemon_pkg:
			if cron_daemon_pkg == "none":
				self._logger.log("Skipping installation of cron daemon")
			else:
				# Emerge Cron Daemon
				exitstatus = self._emerge(cron_daemon_pkg)
				if not GLIUtility.exitsuccess(exitstatus):
					raise GLIException("CronDaemonError", 'fatal', 'install_cron_daemon', "Could not emerge " + cron_daemon_pkg + "!")

				# Add Cron Daemon to default runlevel
				# After we find the name of it's initscript
				# This current code is a hack, and should be better.
				initscript = cron_daemon_pkg[(cron_daemon_pkg.find('/')+1):]
				self._add_to_runlevel(initscript)

				# If the Cron Daemon is not vixie-cron, run crontab			
				if "vixie-cron" not in cron_daemon_pkg:
					exitstatus = GLIUtility.spawn("crontab /etc/crontab", chroot=self._chroot_dir, display_on_tty8=True)
					if not GLIUtility.exitsuccess(exitstatus):
						raise GLIException("CronDaemonError", 'fatal', 'install_cron_daemon', "Failure making crontab!")
				self._logger.log("Cron daemon installed and configured: "+cron_daemon_pkg)
	
	##
	# This will parse the partitions looking for types that require fstools and emerge them if found.
	def install_filesystem_tools(self):
		"Installs and sets up fstools"
		# Get the list of file system tools to be installed
		parts = self._install_profile.get_partition_tables()
		# don't use an array, use a set instead
		filesystem_types = {}
		for device in parts:
			tmp_partitions = parts[device].get_install_profile_structure()
			for partition in tmp_partitions:
				partition_type = tmp_partitions[partition]['type'].lower()
				if partition_type not in filesystem_types:
					filesystem_types[partition_type] = None

		package_list = []
		for filesystem in filesystem_types.keys():
			if filesystem == 'xfs':
				package_list.append('sys-fs/xfsprogs')
			elif filesystem == 'reiserfs':
				package_list.append('sys-fs/reiserfsprogs')
			elif filesystem == 'jfs':
				package_list.append('sys-fs/jfsutils')
			elif filesystem == 'ntfs':
				package_list.append('sys-fs/ntfsprogs')
			elif filesystem in ['fat','vfat', 'msdos', 'umsdos']:
				package_list.append('sys-fs/dosfstools')
			elif filesystem == 'hfs':
				# should check with the PPC guys on this
				package_list.append('sys-fs/hfsutils')
				package_list.append('sys-fs/hfsplusutils')
			#else:
			# should be code here for every FS type!

		failed_list = []
		for package in package_list:
			exitstatus = self._emerge(package)
			if not GLIUtility.exitsuccess(exitstatus):
				self._logger.log("ERROR! : Could not emerge "+package+"!")
				failed_list.append(package)
			else:
				self._logger.log("FileSystemTool "+package+" was emerged successfully.")
		# error checking is important!
		if len(failed_list) > 0:
			raise GLIException("InstallFileSystemToolsError", 'warning', 'install_filesystem_tools', "Could not emerge " + failed_list + "!")
					
	##
	# Installs rp-pppoe but does not configure it.  This function is quite the unknown.
	def install_rp_pppoe(self):
		# If user wants us to install rp-pppoe, then do so
		if self._install_profile.get_install_rp_pppoe():
			exitstatus = self._emerge("rp-pppoe")
			if not GLIUtility.exitsuccess(exitstatus):
				self._logger.log("ERROR! : Could not emerge rp-pppoe!")
			#	raise GLIException("RP_PPPOEError", 'warning', 'install_rp_pppoe', "Could not emerge rp-pppoe!")
			else:
				self._logger.log("rp-pppoe emerged but not set up.")	
		# Should we add a section here to automatically configure rp-pppoe?
		# I think it should go into the setup_network_post section
		# What do you guys think? <-- said by unknown. samyron or npmcallum
				
	##
	# Installs and sets up pcmcia-cs if selected in the profile
	def install_pcmcia_cs(self):
		exitstatus = self._emerge("pcmcia-cs")
		if not GLIUtility.exitsuccess(exitstatus):
			self._logger.log("ERROR! : Could not emerge pcmcia-cs!")
			
		# Add pcmcia-cs to the default runlevel
		else:
			self._add_to_runlevel('pcmcia')
			self._logger.log("PCMCIA_CS emerged and configured.")
			
	##
	# This runs etc-update and then re-overwrites the files by running the configure_*'s to keep our values.
	def update_config_files(self):
		"Runs etc-update (overwriting all config files), then re-configures the modified ones"
		# Run etc-update overwriting all config files
		status = GLIUtility.spawn('echo "-5" | chroot '+self._chroot_dir+' etc-update', display_on_tty8=True)
		if not GLIUtility.exitsuccess(status):
			self._logger.log("ERROR! : Could not update the config files!")
		#	raise GLIException("EtcUpdateError", 'warning', 'update_config_files', "Could not update config files!")
		else:	
#			self.configure_make_conf()
			self.configure_fstab()
#			self.configure_rc_conf()
			etc_files = self._install_profile.get_etc_files()
			for etc_file in etc_files:
				if isinstance(etc_files[etc_file], dict):
					self._edit_config(self._chroot_dir + "/etc/" + etc_file, etc_files[etc_file])
				else:
					for entry in etc_files[etc_file]:
						self._edit_config(self._chroot_dir + "/etc/" + etc_file, { "0": entry }, only_value=True)
			self._logger.log("Config files updated using etc-update.  make.conf/fstab/rc.conf restored.")

	##
	# Configures /etc/rc.conf (deprecated by above code)
	def configure_rc_conf(self):
		
		# Get make.conf options
		options = self._install_profile.get_rc_conf()
		
		# For each configuration option...
		filename = self._chroot_dir + "/etc/rc.conf"
		self._edit_config(filename, {"COMMENT": "GLI additions ===>"})
		for key in options.keys():
			# Add/Edit it into rc.conf
			self._edit_config(filename, {key: options[key]})
		self._edit_config(filename, {"COMMENT": "<=== End GLI additions"})
		self._logger.log("rc.conf configured.")
		
	##
	# Sets up the network for the first boot
	def setup_network_post(self):
		
		# Get hostname, domainname and nisdomainname
		hostname = self._install_profile.get_hostname()
		domainname = self._install_profile.get_domainname()
		nisdomainname = self._install_profile.get_nisdomainname()
		
		# Write the hostname to the hostname file		
		#open(self._chroot_dir + "/etc/hostname", "w").write(hostname + "\n")
		self._edit_config(self._chroot_dir + "/etc/conf.d/hostname", {"HOSTNAME": hostname})
		
		# Write the domainname to the nisdomainname file
		if domainname:
			#open(self._chroot_dir + "/etc/dnsdomainname", "w").write(domainname + "\n")
			self._edit_config(self._chroot_dir + "/etc/conf.d/domainname", {"DNSDOMAIN": domainname})
			self._add_to_runlevel("domainname")
		
		# Write the nisdomainname to the nisdomainname file
		if nisdomainname:
			#open(self._chroot_dir + "/etc/nisdomainname", "w").write(nisdomainname + "\n")
			self._edit_config(self._chroot_dir + "/etc/conf.d/domainname", {"NISDOMAIN": nisdomainname})
			self._add_to_runlevel("domainname")
			
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
		self._edit_config(self._chroot_dir + "/etc/hosts", {hosts_ip: hosts_line}, delimeter='\t', quotes_around_value=False)

		#
		# SET DEFAULT GATEWAY
		#

		# Get default gateway
		default_gateway = self._install_profile.get_default_gateway()
		
		# If the default gateway exists, add it
		if default_gateway:
			default_gateway_string = default_gateway[0] + "/" + default_gateway[1]
			self._edit_config(self._chroot_dir + "/etc/conf.d/net", {"gateway": default_gateway_string})
			
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
		emerge_dhcp = False
		# Parse each interface
		for interface in interfaces.keys():
		
			# Set what kind of interface it is
			interface_type = interface[:3]
		
			# Check to see if there is a startup script for this interface, if there isn't link to the proper script
			try:
				os.stat(self._chroot_dir + "/etc/init.d/net." + interface)
			except:
				os.symlink("net." + interface_type +  "0", self._chroot_dir + "/etc/init.d/net." + interface)
		
			# If we are going to load the network at boot...
			#if interfaces[interface][2]:  #THIS FEATURE NO LONGER EXISTS
				
			# Add it to the default runlevel
			self._add_to_runlevel("net."+interface)	# moved a bit <-- for indentation

			#
			# ETHERNET
			#
			if interface_type == "eth":

				#
				# STATIC IP
				#
				# If the post-install device info is not None, then it is a static ip addy
				if interfaces[interface][0] != "dhcp":
					ip = interfaces[interface][0]
					broadcast = interfaces[interface][1]
					netmask = interfaces[interface][2]
			#		aliases = interfaces[interface][1][3]
			#		alias_ips = []
			#		alias_broadcasts = []
			#		alias_netmasks = []
					
					# Write the static ip config to /etc/conf.d/net
					self._edit_config(self._chroot_dir + "/etc/conf.d/net", {"iface_" + interface: ip + " broadcast " + broadcast + " netmask " + netmask})
					
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
					dhcpcd_options = interfaces[interface][1]
					if dhcpcd_options is None:
						dhcpcd_options = ""
					self._edit_config(self._chroot_dir + "/etc/conf.d/net", {"iface_" + interface: "dhcp", "dhcpcd_" + interface: dhcpcd_options})
					emerge_dhcp = True
		if emerge_dhcp:
			exitstatus = self._emerge("dhcpcd")
			if not GLIUtility.exitsuccess(exitstatus):
				self._logger.log("ERROR! : Could not emerge dhcpcd!")
			else:
				self._logger.log("dhcpcd emerged.")		
		
	##
	# Sets the root password
	def set_root_password(self):
		status = GLIUtility.spawn('echo \'root:' + self._install_profile.get_root_pass_hash() + '\' | chroot '+self._chroot_dir+' chpasswd -e')
		if not GLIUtility.exitsuccess(status):
			raise GLIException("SetRootPasswordError", 'fatal', 'set_root_password', "Failure to set root password!")
		self._logger.log("Root Password set on the new system.")
		
	##
	# Sets up the new users for the system
	def set_users(self):
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
			
			options = [ "-m", "-p '" + password_hash + "'" ]
			
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
					
				# Attempt to add the group (will return success when group exists)
				for group in groups:
					# Add the user
					exitstatus = GLIUtility.spawn('groupadd -f ' + group, chroot=self._chroot_dir, logfile=self._compile_logfile, append_log=True, display_on_tty8=True)
					if not GLIUtility.exitsuccess(exitstatus):
						self._logger.log("ERROR! : Failure to add group " + group+" and it wasn't that the group already exists!")
					
			
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
			exitstatus = GLIUtility.spawn('useradd ' + string.join(options) + ' ' + username, chroot=self._chroot_dir, logfile=self._compile_logfile, append_log=True, display_on_tty8=True)
			if not GLIUtility.exitsuccess(exitstatus):
				self._logger.log("ERROR! : Failure to add user " + username)
			#	raise GLIException("AddUserError", 'warning', 'set_users', "Failure to add user " + username)
			else:
				self._logger.log("User "+username+"was added.")
			
	##
	# This function will handle the various cleanup tasks as well as unmounting the filesystems for reboot.
	def finishing_cleanup(self):
		#These are temporary until I come up with a nicer idea.
		#get rid of the compile_output file so the symlink doesn't get screwed up.
		
		#we copy the log over to the new system.
		install_logfile = self._client_configuration.get_log_file()
		try:
			shutil.copy(install_logfile, self._chroot_dir + install_logfile)
		except:
			pass
		#Now we're done logging as far as the new system is concerned.
		GLIUtility.spawn("cp /tmp/installprofile.xml " + self._chroot_dir + "/root/installprofile.xml")
		GLIUtility.spawn("cp /tmp/clientconfiguration.xml " + self._chroot_dir + "/root/clientconfiguration.xml")
		
		#Unmount mounted fileystems in preparation for reboot
		mounts = GLIUtility.spawn(r"mount | sed -e 's:^.\+ on \(.\+\) type .\+$:\1:' | grep -e '^" + self._chroot_dir + "' | sort -r", return_output=True)[1].split("\n")
		for mount in mounts:
			GLIUtility.spawn("umount -l " + mount)
			
		# now turn off all swap as well.
		# we need to find the swap devices
		for swap_device in self._swap_devices:
			ret = GLIUtility.spawn("swapoff "+swap_device)
			if not GLIUtility.exitsuccess(ret):
				self._logger.log("ERROR! : Could not deactivate swap ("+swap_device+")!")
		
		#OLD WAY: Unmount the /proc and /dev that we mounted in prepare_chroot
		#There really isn't a reason to log errors here.
		#ret = GLIUtility.spawn("umount "+self._chroot_dir+"/proc", display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
		#ret = GLIUtility.spawn("umount "+self._chroot_dir+"/dev", display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
		#temp hack to unmount the new root.
		#ret = GLIUtility.spawn("umount "+self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
		#insert code here to unmount the swap partition, if there is one.

		GLIUtility.spawn("rm /tmp/compile_output.log && rm " + install_logfile)
		
	##
	# This is a stub function to be done by the individual arch.  I don't think it's even needed here.
	# but it's nice having it just incase.
	def install_bootloader(self):
		"THIS FUNCTION MUST BE DONE BY THE INDIVIDUAL ARCH"
		pass

	def run_post_install_script(self):
		if self._install_profile.get_post_install_script_uri():
			try:
				GLIUtility.get_uri(self._install_profile.get_post_install_script_uri(), self._chroot_dir + "/var/tmp/post-install")
				GLIUtility.spawn("chmod a+x /var/tmp/post-install && /var/tmp/post-install", chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			except:
				raise GLIException("RunPostInstallScriptError", 'fatal', 'run_post_install_script', "Failed to retrieve and/or execute post-install script")

	##
	# This function should only be called in the event of an install failure. It performs
	# general cleanup to prepare the system for another installer run.
	def install_failed_cleanup(self):
		mounts = GLIUtility.spawn(r"mount | sed -e 's:^.\+ on \(.\+\) type .\+$:\1:' | grep -e '^" + self._chroot_dir + "' | sort -r", return_output=True)[1].split("\n")
		for mount in mounts:
			GLIUtility.spawn("umount -l " + mount)
			
		# now turn off all swap as well.
		# we need to find the swap devices
		for swap_device in self._swap_devices:
			ret = GLIUtility.spawn("swapoff "+swap_device)
			if not GLIUtility.exitsuccess(ret):
				self._logger.log("ERROR! : Could not deactivate swap ("+swap_device+")!")
		
		GLIUtility.spawn("rm /tmp/compile_output.log")
