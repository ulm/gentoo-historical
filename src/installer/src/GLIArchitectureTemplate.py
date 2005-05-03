"""
Gentoo Linux Installer

$Id: GLIArchitectureTemplate.py,v 1.106 2005/05/03 17:12:37 agaffney Exp $
Copyright 2004 Gentoo Technologies Inc.

The ArchitectureTemplate is largely meant to be an abstract class and an 
interface (yes, it is both at the same time!). The purpose of this is to create 
subclasses that populate all the methods with working methods for that architecture. 
The only definitions that are filled in here are architecture independent. 

"""

import GLIUtility, GLILogger, os, string, sys, shutil, re
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
                                 (self.configure_make_conf, "Configure /etc/make.conf"),
                                 (self.prepare_chroot, "Preparing chroot"),
                                 (self.install_portage_tree, "Portage tree voodoo"),
                                 (self.stage1, "Performing bootstrap"),
                                 (self.stage2, "Performing 'emerge system'"),
                                 (self.set_root_password, "Set the root password"),
                                 (self.set_timezone, "Setting timezone"),
                                 (self.emerge_kernel_sources, "Emerge kernel sources"),
                                 (self.build_kernel, "Building kernel"),
                                 (self.install_logging_daemon, "Logger"),
                                 (self.install_cron_daemon, "Cron daemon"),
                                 (self.install_filesystem_tools, "Installing filesystem tools"),
                                 (self.setup_network_post, "Configuring post-install networking"),
                                 (self.install_bootloader, "Configuring and installing bootloader"),
                                 (self.update_config_files, "Updating config files"),
                                 (self.configure_rc_conf, "Updating /etc/rc.conf"),
                                 (self.set_services, "Setting up services for startup"),
                                 (self.set_users, "Add additional users."),
                                 (self.install_packages, "Installing additional packages."),
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

		status = GLIUtility.spawn("rc-update add " + script_name + " " + runlevel, display_on_tty8=True, chroot=self._chroot_dir, logfile=self._compile_logfile, append_log=True)
		if not GLIUtility.exitsuccess(status):
			raise GLIException("RunlevelAddError", 'fatal', '_add_to_runlevel', "Failure adding " + script_name + " to runlevel " + runlevel + "!")
		self._logger.log("Added "+script_name+" to runlevel "+runlevel)

	##
	# Private Function.  Will return a list of packages to be emerged for a given command.  Not yet used.
	# @param cmd full command to run ('/usr/portage/scripts/bootstrap.sh --pretend' or 'emerge -p system')
	def _get_packages_to_emerge(self, cmd):
		return GLIUtility.spawn(cmd + r" | grep -e '\[ebuild' | sed -e 's:\[ebuild .\+ \] ::' -e 's: \[.\+\] ::' -e 's: +$::'", chroot=self._chroot_dir, return_output=True)[1].split("\n")

	##
	# Private function.  For binary installs it will attempt to quickpkg packages that are on the livecd.
	# @param package package to be quickpkg'd.
	def _quickpkg_deps(self, package):
		# These need to be changed to pull values from the make.conf stuff
		PKGDIR = "/usr/portage/packages"
		PORTAGE_TMPDIR = "/var/tmp"
		make_conf = self._install_profile.get_make_conf()
		if "PKGDIR" in make_conf and make_conf['PKGDIR']: PKGDIR = make_conf['PKGDIR']
		if "PORTAGE_TMPDIR" in make_conf and make_conf['PORTAGE_TMPDIR']: PORTAGE_TMPDIR = make_conf['PORTAGE_TMPDIR']
		GLIUtility.spawn("mkdir -p " + self._chroot_dir + PKGDIR, logfile=self._compile_logfile, append_log=True)
		GLIUtility.spawn("mkdir -p " + self._chroot_dir + PORTAGE_TMPDIR, logfile=self._compile_logfile, append_log=True)
		packages = self._get_packages_to_emerge("emerge -p " + package)
		for pkg in packages:
			if not GLIUtility.is_file(self._chroot_dir + PKGDIR + "/All/" + pkg.split('/')[1] + ".tbz2"):
				ret = GLIUtility.spawn("env PKGDIR='" + self._chroot_dir + PKGDIR + "' PORTAGE_TMPDIR='" + self._chroot_dir + PORTAGE_TMPDIR + "' quickpkg =" + pkg)
				if ret:
					# This package couldn't be quickpkg'd. This may be an error in the future
					pass

	##
	# Private Function.  Will emerge a given package in the chroot environment.
	# @param package package to be emerged
	# @param binary=False defines whether to try a binary emerge (if GRP this gets ignored either way)
	# @param binary_only=False defines whether to only allow binary emerges.
	def _emerge(self, package, binary=False, binary_only=False):
		#Error checking of this function is to be handled by the parent function.
		if self._install_profile.get_grp_install():
			self._quickpkg_deps(package)
			return GLIUtility.spawn("emerge -k " + package, display_on_tty8=True, chroot=self._chroot_dir, logfile=self._compile_logfile, append_log=True)
		else:
			if binary_only:
				return GLIUtility.spawn("emerge -K " + package, display_on_tty8=True, chroot=self._chroot_dir, logfile=self._compile_logfile, append_log=True)
			elif binary:
				return GLIUtility.spawn("emerge -k " + package, display_on_tty8=True, chroot=self._chroot_dir, logfile=self._compile_logfile, append_log=True)
			else:
				return GLIUtility.spawn("emerge " + package, display_on_tty8=True, chroot=self._chroot_dir, logfile=self._compile_logfile, append_log=True)

	##
	# Private Function.  Will edit a config file and insert a value or two overwriting the previous value
	# (actually it only just comments out the old one)
	# @param filename file to be edited
	# @param newvalues a dictionary of VARIABLE:VALUE pairs
	# @param delimeter='=' what is between the key and the value
	# @param quotes_around_value=True whether there are quotes around the value or not (ex. "local" vs. localhost)
	def _edit_config(self, filename, newvalues, delimeter='=', quotes_around_value=True):
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
			commentprefix = ""
			if newvalues[key] == "COMMENT" or newvalues[key] == "##comment##" or newvalues[key] == "##commented##":
				commentprefix = "#"
			if quotes_around_value:
				file.append(commentprefix + key + delimeter + '"' + newvalues[key] + '"\n')
			else:
				file.append(commentprefix + key + delimeter + newvalues[key]+'\n')
	
		f = open(filename,'w')
		f.writelines(file)
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
		ret = GLIUtility.spawn("mount -o bind /dev " + self._chroot_dir + "/dev")
		if not GLIUtility.exitsuccess(ret):
			raise GLIException("MountError", 'fatal','prepare_chroot','Could not mount /dev')
		GLIUtility.spawn("mv " + self._compile_logfile + " " + self._chroot_dir + self._compile_logfile + " && ln -s " + self._chroot_dir + self._compile_logfile + " " + self._compile_logfile)
		self._logger.log("Chroot environment ready.")

	##
	# Installs a list of packages specified in the profile. Will install any extra software!
	# In the future this function will lead to better things.  It may even wipe your ass for you.
	def install_packages(self):
		installpackages = self._install_profile.get_install_packages()
		for package in installpackages:
			status = self._emerge(package)
			if not GLIUtility.exitsuccess(status):
				self._logger.log("Could not emerge " + package + "!")
			#	raise GLIException("InstallPackagesError", 'warning', 'install_packages', "Could not emerge " + package + "!")
			else:
				self._logger.log("Emerged package: "+package)

	##
	# Will set the list of services to runlevel default.  This is a temporary solution!
	def set_services(self):
		services = self._install_profile.get_services()
		for service in services:
			status = self._add_to_runlevel(service)
			
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
		#in parts['/dev/hda']
			for partition in parts[device]:
				#print parts[device][partition]
				mountpoint = parts[device][partition]['mountpoint']
				mountopts = parts[device][partition]['mountopts']
				minor = str(int(parts[device][partition]['minor']))
				partition_type = parts[device][partition]['type']
				if mountpoint:
					if mountopts:
						mountopts = "-o "+mountopts+" "
					if partition_type:
						partition_type = "-t "+partition_type+" "
					parts_to_mount[mountpoint]= {0: mountopts, 1: partition_type, 2: minor}
					
				if partition_type == "linux-swap":
					ret = GLIUtility.spawn("swapon "+device+minor)
					if not GLIUtility.exitsuccess(ret):
						self._logger.log("ERROR! : Could not activate swap!")
					#	raise GLIException("MountError", 'warning','mount_local_partitions','Could not activate swap')
		sorted_list = []
		for key in parts_to_mount.keys(): sorted_list.append(key)
		sorted_list.sort()
		
		for mountpoint in sorted_list:
			mountopts = parts_to_mount[mountpoint][0]
			partition_type = parts_to_mount[mountpoint][1]
			minor = parts_to_mount[mountpoint][2]
			if not GLIUtility.is_file(self._chroot_dir+mountpoint):
				exitstatus = GLIUtility.spawn("mkdir -p " + self._chroot_dir + mountpoint)
				if exitstatus != 0:
					raise GLIException("MkdirError", 'fatal','mount_local_partitions', "Making the mount point failed!")
			ret = GLIUtility.spawn("mount "+partition_type+mountopts+device+minor+" "+self._chroot_dir+mountpoint, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if not GLIUtility.exitsuccess(ret):
				raise GLIException("MountError", 'fatal','mount_local_partitions','Could not mount a partition')
			self._logger.log("Mounted mountpoint:"+mountpoint)
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
					mountopts = "-o "+mountopts
				host = netmount['host']
				export = netmount['export']
				mountpoint = netmount['mountpoint']
				if not GLIUtility.is_file(self._chroot_dir+mountpoint):
					exitstatus = GLIUtility.spawn("mkdir -p " + self._chroot_dir + mountpoint)
					if exitstatus != 0:
						raise GLIException("MkdirError", 'fatal','mount_network_shares', "Making the mount point failed!")
				ret = GLIUtility.spawn("mount -t nfs "+mountopts+" "+host+":"+export+" "+self._chroot_dir+mountpoint, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
				if not GLIUtility.exitsuccess(ret):
					raise GLIException("MountError", 'fatal','mount_network_shares','Could not mount an NFS partition')
				self._logger.log("Mounted netmount at mountpoint:"+mountpoint)

	##
	# Gets sources from CD (required for non-network installation)
	# WARNING: There will no longer be sources on the future livecds.  this will have to change!
	def fetch_sources_from_cd(self):
		"""
		THIS FUNCTION IS NO LONGER VALID
		if not GLIUtility.is_file(self._chroot_dir+"/usr/portage/distfiles"):
			exitstatus = GLIUtility.spawn("mkdir -p /usr/portage/distfiles",chroot=self._chroot_dir)
			if exitstatus != 0:
				raise GLIException("MkdirError", 'fatal','install_portage_tree',"Making the distfiles directory failed.")
		exitstatus = GLIUtility.spawn("cp /mnt/cdrom/distfiles/* "+self._chroot_dir+"/usr/portage/distfiles/", display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
		if exitstatus != 0:
			raise GLIException("PortageError", 'fatal','install_portage_tree',"Failed to copy the distfiles to the new system")
		"""
		self._logger.log("Distfiles copied from cd. NOT!")
		
	##
	# Gets grp binary packages from CD (required for non-network binary installation)
	# This will not work anymore at all.  I don't know why it's even still here.
	def fetch_grp_from_cd(self):
		pass
	
	##
	# Configures the new /etc/make.conf
	def configure_make_conf(self):
		# Get make.conf options
		options = self._install_profile.get_make_conf()
		
		# For each configuration option...
		for key in options.keys():
		
			# Add/Edit it into make.conf
			self._edit_config(self._chroot_dir + "/etc/make.conf", {key: options[key]})
		self._logger.log("Make.conf configured")

	##
	# This will get/update the portage tree.  If you want to snapshot or mount /usr/portage use "custom".
	def install_portage_tree(self):
		# Check the type of portage tree fetching we'll do
		# If it is custom, follow the path to the custom tarball and unpack it

		# This is a hack to copy the LiveCD's rsync into the chroot since it has the sigmask patch
		GLIUtility.spawn("cp -a /usr/bin/rsync " + self._chroot_dir + "/usr/bin/rsync")
		GLIUtility.spawn("cp -a /usr/lib/libpopt* " + self._chroot_dir + "/usr/lib")

		if self._install_profile.get_portage_tree_sync_type() == "snapshot" or self._install_profile.get_portage_tree_sync_type() == "custom": # Until this is finalized
		
			# Get portage tree info
			portage_tree_snapshot_uri = self._install_profile.get_portage_tree_snapshot_uri()
			if portage_tree_snapshot_uri:
				# Fetch and unpack the tarball
				GLIUtility.fetch_and_unpack_tarball(portage_tree_snapshot_uri, self._chroot_dir + "/usr/", self._chroot_dir + "/")
			self._logger.log("Portage tree install was custom.")
		# If the type is webrsync, then run emerge-webrsync
		elif self._install_profile.get_portage_tree_sync_type() == "webrsync":
			exitstatus = GLIUtility.spawn("emerge-webrsync", chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if exitstatus != 0:
				raise GLIException("EmergeWebRsyncError", 'fatal','install_portage_tre', "Failed to retrieve portage tree!")
			self._logger.log("Portage tree sync'd using webrsync")
		# Otherwise, just run emerge sync
		else:
			exitstatus = self._emerge("sync")
			if exitstatus != 0:
				raise GLIException("EmergeSyncError", 'fatal','install_portage_tree', "Failed to retrieve portage tree!")
			self._logger.log("Portage tree sync'd")
			
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
		#in parts['/dev/hda']
			for partition in parts[device]:
				#print parts[device][partition]
				mountpoint = parts[device][partition]['mountpoint']
				minor = str(int(parts[device][partition]['minor']))
				partition_type = parts[device][partition]['type']
				mountopts = parts[device][partition]['mountopts']
				if not mountopts.strip(): mountopts = "defaults"
				if mountpoint:
					if not GLIUtility.is_file(self._chroot_dir+mountpoint):
						exitstatus = GLIUtility.spawn("mkdir -p " + self._chroot_dir + mountpoint)
						if exitstatus != 0:
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
		
		kernel_pkg = self._install_profile.get_kernel_source_pkg()
#		if kernel_pkg:
		if kernel_pkg == "livecd-kernel":
			PKGDIR = "/usr/portage/packages"
			PORTAGE_TMPDIR = "/var/tmp"
			make_conf = self._install_profile.get_make_conf()
			if "PKGDIR" in make_conf: PKGDIR = make_conf['PKGDIR']
			if "PORTAGE_TMPDIR" in make_conf: PORTAGE_TMPDIR = make_conf['PORTAGE_TMPDIR']
			GLIUtility.spawn("mkdir -p " + self._chroot_dir + PKGDIR, logfile=self._compile_logfile, append_log=True)
			GLIUtility.spawn("mkdir -p " + self._chroot_dir + PORTAGE_TMPDIR, logfile=self._compile_logfile, append_log=True)
			ret = GLIUtility.spawn("env PKGDIR=" + self._chroot_dir + PKGDIR + " PORTAGE_TMPDIR=" + self._chroot_dir + PORTAGE_TMPDIR + " quickpkg livecd-kernel")
			ret = GLIUtility.spawn("env PKGDIR=" + PKGDIR + " emerge -K sys-kernel/livecd-kernel", chroot=self._chroot_dir)
			
			#these are the hotplug/coldplug steps from build_kernel copied over here.  they will NOT be run there.
			exitstatus = self._emerge("hotplug")
			if exitstatus != 0:
				raise GLIException("EmergeHotplugError", 'fatal','build_kernel', "Could not emerge hotplug!")
			self._logger.log("Hotplug emerged.")
			exitstatus = self._emerge("coldplug")
			if exitstatus != 0:
				raise GLIException("EmergeColdplugError", 'fatal','build_kernel', "Could not emerge coldplug!")
			self._logger.log("Coldplug emerged.  Now they should be added to the default runlevel.")
			
			self._add_to_runlevel("hotplug")
			self._add_to_runlevel("coldplug", runlevel="boot")
		else:
			exitstatus = self._emerge(kernel_pkg)
			if exitstatus != 0:
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
						if exitstatus != 0:
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
		# No building necessary if using the LiveCD's kernel/initrd
		if self._install_profile.get_kernel_source_pkg() == "livecd-kernel": return
		# Get the uri to the kernel config
		kernel_config_uri = self._install_profile.get_kernel_config_uri()
		if kernel_config_uri == "":  #use genkernel if no specific config
		
			exitstatus = self._emerge("genkernel")
			if exitstatus != 0:
				raise GLIException("EmergeGenKernelError", 'fatal','build_kernel', "Could not emerge genkernel!")
			self._logger.log("Genkernel emerged.  Beginning kernel compile.")
			# Null the genkernel_options
			genkernel_options = ""
	
			# If the uri for the kernel config is not null, then
			if kernel_config_uri != "":
				GLIUtility.get_uri(kernel_config_uri, self._chroot_dir + "/root/kernel_config")
				genkernel_options = genkernel_options + " --kernel-config=/root/kernel_config"
				
			# Decide whether to use bootsplash or not
			if self._install_profile.get_kernel_bootsplash():
				genkernel_options = genkernel_options + " --bootsplash"
			else:
				genkernel_options = genkernel_options + " --no-bootsplash"
			# Run genkernel in chroot
			#print "genkernel all " + genkernel_options
			exitstatus = GLIUtility.spawn("genkernel all " + genkernel_options, chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if exitstatus != 0:
				raise GLIException("KernelBuildError", 'fatal', 'build_kernel', "Could not build kernel!")
			
			exitstatus = self._emerge("hotplug")
			if exitstatus != 0:
				raise GLIException("EmergeHotplugError", 'fatal','build_kernel', "Could not emerge hotplug!")
			self._logger.log("Hotplug emerged.")
			exitstatus = self._emerge("coldplug")
			if exitstatus != 0:
				raise GLIException("EmergeColdplugError", 'fatal','build_kernel', "Could not emerge coldplug!")
			self._logger.log("Coldplug emerged.  Now they should be added to the default runlevel.")
			
			self._add_to_runlevel("hotplug")
			self._add_to_runlevel("coldplug", runlevel="boot")
			self._logger.log("Genkernel complete.")
		else:  #CUSTOM CONFIG
			#Copy the kernel .config to the proper location in /usr/src/linux
			try:
				GLIUtility.get_uri(kernel_config_uri, self._chroot_dir + "/root/kernel_config")
			except:
				raise GLIException("KernelBuildError", 'fatal', 'build_kernel', "Could not copy kernel config!")
			
			kernel_compile_script =  "#!/bin/bash\n"
			kernel_compile_script += "cp /root/kernel_config /usr/src/linux/.config\n"
			kernel_compile_script += "cd /usr/src/linux\n"
			kernel_compile_script += "make \nmake modules_install \n"

			#Ok now that it's built, copy it to /boot/kernel-* for bootloader code to find it
			if self._client_configuration.get_architecture_template() == "x86":
				kernel_compile_script += "cp /usr/src/linux/arch/i386/boot/bzImage /boot/kernel-custom\n"
			f = open(self._chroot_dir+"/root/kernel_script", 'w')
			f.writelines(kernel_compile_script)
			f.close()
			#Build the kernel
			exitstatus1 = GLIUtility.spawn("chmod u+x "+self._chroot_dir+"/root/kernel_script")
			exitstatus2 = GLIUtility.spawn("/root/kernel_script", chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			if (exitstatus1 != 0) or (exitstatus2 != 0):
				raise GLIException("KernelBuildError", 'fatal', 'build_kernel', "Could not build custom kernel!")
						
			#i'm sure i'm forgetting something here.
			#cleanup
			exitstatus = GLIUtility.spawn("rm "+self._chroot_dir+"/root/kernel_script")
			#it's not important if this fails.
			self._logger.log("Custom kernel complete")
			
	##
	# Installs and sets up logging daemon on the new system.  adds to runlevel too.
	def install_logging_daemon(self):
		
		# Get loggin daemon info
		logging_daemon_pkg = self._install_profile.get_logging_daemon_pkg()
		if logging_daemon_pkg:
			# Emerge Logging Daemon
			exitstatus = self._emerge(logging_daemon_pkg)
			if exitstatus != 0:
				raise GLIException("LoggingDaemonError", 'fatal','install_logging_daemon', "Could not emerge " + logging_daemon_pkg + "!")

			# Add Logging Daemon to default runlevel
			self._add_to_runlevel(logging_daemon_pkg)
			self._logger.log("Logging daemon installed: "+logging_daemon_pkg)
	##
	# Installs and sets up cron package.
	def install_cron_daemon(self):
		
		# Get cron daemon info
		cron_daemon_pkg = self._install_profile.get_cron_daemon_pkg()
		if cron_daemon_pkg:
			# Emerge Cron Daemon
			exitstatus = self._emerge(cron_daemon_pkg)
			if exitstatus != 0:
				raise GLIException("CronDaemonError", 'fatal', 'install_cron_daemon', "Could not emerge " + cron_daemon_pkg + "!")

			# Add Cron Daemon to default runlevel
			self._add_to_runlevel(cron_daemon_pkg)
		
			# If the Cron Daemon is not vixie-cron, run crontab			
			if cron_daemon_pkg != "vixie-cron":
				exitstatus = GLIUtility.spawn("crontab /etc/crontab", chroot=self._chroot_dir, display_on_tty8=True)
				if exitstatus != 0:
					raise GLIException("CronDaemonError", 'fatal', 'install_cron_daemon', "Failure making crontab!")
			self._logger.log("Cron daemon installed and configured: "+cron_daemon_pkg)
	##
	# This will parse the partitions looking for types that require fstools and emerge them if found.
	def install_filesystem_tools(self):
		"Installs and sets up fstools"
		# Get the list of file system tools to be installed
		parts = self._install_profile.get_partition_tables()
		filesystem_tools = []
		for device in parts:
		#in parts['/dev/hda']
			for partition in parts[device]:
				#print parts[device][partition]
				partition_type = parts[device][partition]['type']
				if partition_type not in filesystem_tools:
					filesystem_tools.append(partition_type)
		for filesystem in filesystem_tools:
			if filesystem.lower() == "xfs":
				exitstatus = self._emerge("xfsprogs")
				if exitstatus != 0:
					self._logger.log("ERROR! : Could not emerge xfsprogs!")
				else:
					self._logger.log("FileSystemTool xfsprogs was emerged successfully.")
			if filesystem.lower() == "reiserfs":
				exitstatus = self._emerge("reiserfsprogs")
				if exitstatus != 0:
					self._logger.log("ERROR! : Could not emerge reiserfsprogs!")
				else:
					self._logger.log("FileSystemTool reiserfsprogs was emerged successfully.")
			if filesystem.lower() == "jfs":
				exitstatus = self._emerge("jfsutils")
				if exitstatus != 0:
					self._logger.log("ERROR! : Could not emerge jfsutils!")
				else:
					self._logger.log("FileSystemTool jfsutils was emerged successfully.")
					
	##
	# Installs rp-pppoe but does not configure it.  This function is quite the unknown.
	def install_rp_pppoe(self):
		
		# If user wants us to install rp-pppoe, then do so
		if self._install_profile.get_install_rp_pppoe():
			exitstatus = self._emerge("rp-pppoe")
			if exitstatus != 0:
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
		# If user wants us to install pcmcia-cs, then do so
		if self._install_profile.get_install_pcmcia_cs():
			exitstatus = self._emerge("pcmcia-cs")
			if exitstatus != 0:
				self._logger.log("ERROR! : Could not emerge pcmcia-cs!")
			#	raise GLIException("PCMCIA_CSError", 'warning', 'install_pcmcia_cs', "Could not emerge pcmcia-cs!")
				
			# Add pcmcia-cs to the default runlevel
			else:
				self._add_to_runlevel(pcmcia)
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
			self.configure_make_conf()
			self.configure_fstab()
			self.configure_rc_conf()
			self._logger.log("Config files updated using etc-update.  make.conf/fstab/rc.conf restored.")

	##
	# Configures /etc/rc.conf
	def configure_rc_conf(self):
		
		# Get make.conf options
		options = self._install_profile.get_rc_conf()
		
		# For each configuration option...
		for key in options.keys():
		
			# Add/Edit it into rc.conf
			self._edit_config(self._chroot_dir + "/etc/rc.conf", {key: options[key]})
		self._logger.log("rc.conf configured.")
		
	##
	# Sets up the network for the first boot
	def setup_network_post(self):
		
		# Get hostname, domainname and nisdomainname
		hostname = self._install_profile.get_hostname()
		domainname = self._install_profile.get_domainname()
		nisdomainname = self._install_profile.get_nisdomainname()
		
		# Write the hostname to the hostname file		
		open(self._chroot_dir + "/etc/hostname", "w").write(hostname + "\n")
		
		# Write the domainname to the nisdomainname file
		if domainname:
			open(self._chroot_dir + "/etc/dnsdomainname", "w").write(domainname + "\n")
			self._add_to_runlevel("domainname")
		
		# Write the nisdomainname to the nisdomainname file
		if nisdomainname:
			open(self._chroot_dir + "/etc/nisdomainname", "w").write(nisdomainname + "\n")
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
				os.symlink(self._chroot_dir + "/etc/init.d/net." + interface_type +  "0", self._chroot_dir + "/etc/init.d/net." + interface)				
		
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
				if interfaces[interface][1]:
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
					self._edit_config(self._chroot_dir + "/etc/conf.d/net", {"iface_" + interface: "dhcp"})
					emerge_dhcp = True
		if emerge_dhcp:
			exitstatus = self._emerge("dhcpcd")
			if exitstatus != 0:
				self._logger.log("ERROR! : Could not emerge dhcpcd!")
			else:
				self._logger.log("dhcpcd emerged.")		
		
	##
	# Sets the root password
	def set_root_password(self):
		status = GLIUtility.spawn('echo \'root:' + self._install_profile.get_root_pass_hash() + '\' | chroot '+self._chroot_dir+' chpasswd -e', quiet=True)
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
		
		#Unmount the /proc and /dev that we mounted in prepare_chroot
		#There really isn't a reason to log errors here.
		ret = GLIUtility.spawn("umount "+self._chroot_dir+"/proc", display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
		ret = GLIUtility.spawn("umount "+self._chroot_dir+"/dev", display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
		#temp hack to unmount the new root.
		ret = GLIUtility.spawn("umount "+self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
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
				GLIUtility.get_uri(self._install_profile.get_post_install_script_uri(), self._chroot_dir + "/tmp/post-install")
				GLIUtility.spawn("chmod a+x /tmp/post-install && /tmp/post-install", chroot=self._chroot_dir, display_on_tty8=True, logfile=self._compile_logfile, append_log=True)
			except:
				raise GLIException("RunPostInstallScriptError", 'fatal', 'run_post_install_script', "Failed to retrieve and/or execute post-install script")
