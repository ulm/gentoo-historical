"""
Gentoo Linux Installer

$Id: GLIArchitectureTemplate.py,v 1.14 2004/11/21 06:42:32 agaffney Exp $
Copyright 2004 Gentoo Technologies Inc.


The ArchitectureTemplate is largely meant to be an abstract class and an 
interface (yes, it is both at the same time!). The purpose of this is to create 
subclasses that populate all the methods with working methods for that architecture. 
The only definitions that are filled in here are architecture independent. 

"""

import GLIUtility
from signal import SIGUSR1
from GLIException import *
# Until I switch my partition code to GLIUtility.spawn()
import commands

class ArchitectureTemplate:

	def __init__(self,configuration=None, install_profile=None, client_controller=None):
		self._configuration = configuration
		self._install_profile = install_profile
		self._cc = client_controller

		# This will get used a lot, so it's probably
		# better to store it in a variable than to call
		# this method 100000 times.
		self._chroot_dir = self._configuration.get_root_mount_point()

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
		
        def _depends(self, depends):
		# Type checking
		if type(depends) not in [ list, str, tuple ]:
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

	def get_install_steps(self):
		return self._install_steps

	# It is possible to override these methods in each Arch Template.
	# It might be necessary to do so, if the arch needs something 'weird'.

	def stage1(self):
		"Stage 1 install -- bootstraping"
		# Dependency checking
		self._depends("preinstall")

		# If we are doing a stage 1 install, then bootstrap 
		if self._install_profile.get_install_stage() == 1:
			exitstatus = GLIUtility.spawn("/usr/portage/scripts/bootstrap.sh", True)
			if not GLIUtility.exitsuccess(exitstatus):
				raise Stage1Error('fatal','stage1', "Bootstrapping failed!")

		self._configuration.add_install_steps_completed("stage1")

	def stage2(self):
		# Dependency checking
		self._depends("stage1")

		# If we are doing a stage 1 or 2 install, then emerge system
		if self._install_profile.get_install_stage() in [ 1, 2 ]:
			exitstatus = GLIUtility.emerge("system")
			if not GLIUtility.exitsuccess(exitstatus):
				raise Stage2Error('fatal','stage2', "Building the system failed!")

		self._configuration.add_install_steps_completed("stage2")

	def unpack_stage_tarball(self):
		if not os.path.isdir(self._chroot_dir):
			os.makedirs(self._chroot_dir)
		GLIUtility.fetch_and_unpack_tarball(self._install_profile.get_stage_tarball_uri(), self._chroot_dir, keep_permissions=True)

	def prepare_chroot(self):
		ret = GLIUtility.spawn("cp -L /etc/resolv.conf /mnt/gentoo/etc/resolv.conf",True)
		if not GLIUtility.exitsuccess(ret):
			raise CopyError('warning','preinstall','Could not copy resolv.conf!',True)

		ret = GLIUtility.spawn("mount -t proc none /mnt/gentoo /proc")
		if not GLIUtility.exitsuccess(ret):
			raise MountError('fatal','preinstall','Could not mount /proc')

		# Set USE flags here
		# might want to rewrite/use _edit_config from the GLIInstallTemplate
		# Then you should be done... at least with the preinstall.

	def notify_frontend(self, type, data):
		self._cc.addNotification(type, data)

	def install_packages(self):
		"Will install any extra software!"
		# Dependency checking
		self._depends("emerge system")
		installpackages = self._install_profile.get_install_packages()
		for package in installpackages:
			status = GLIUtility.emerge(package)
			if not GLIUtility.exit_success(status):
				raise "InstallPackagesError", "Could not emerge " + package + "!"

	# This is part of the interface... subclasses MUST
	# provide these methods filled in.
	def stage3(self):
		# This should probably start with building the kernel,
		# that might be the only thing this actually needs
		# to do.
		pass

	def postinstall(self):
		pass

	def partition(self):
		pass

# **************************************************************************************

	def _add_to_runlevel(self, script_name, runlevel="default"):
		"Adds the script named 'script_name' to the runlevel 'runlevel' in the chroot environement"
		
		# Do it
		status = GLIUtility._run("rc-update add " + script_name + " " + runlevel, chroot=self._chroot_dir)
		if not GLIUtility.exit_success(status):
			raise "RunlevelAddError", "Failure adding " + script_name + " to runlevel " + runlevel + "!"
			
	def mount_local_partitions(self):
		"Mounts all partitions that are on the local machine"
		# Dependency checking		
		self._depends("partition_local_drives")

	def mount_network_shares(self):
		"Mounts all network shares to the local machine"
		# Dependency checking		
		self._depends([ "setup_network_pre", "mount_local_partitions" ])

	def fetch_sources_from_cd(self):
		"Gets sources from CD (required for non-network installation)"
		# Dependency checking		
		self._depends("unpack_tarball")

	def fetch_grp_from_cd(self):
		"Gets grp binary packages from CD (required for non-network binary installation)"
		# Dependency checking		
		self._depends("unpack_tarball")

	def configure_make_conf(self):
		"Configures make.conf"
		# Dependency checking		
		self._depends("prepare_chroot")
		
		# Get make.conf options
		options = self._install_profile.get_make_conf()
		
		# For each configuration option...
		for key in options.keys():
		
			# Add/Edit it into make.conf
			GLIUtility.edit_config(self._chroot_dir + "/etc/make.conf", key, options[key])

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
			self._fetch_and_unpack_tarball(portage_tree_snapshot_uri, self._client_configuration.get_root_mount_point() + "/usr/", self._client_configuration.get_root_mount_point() + "/")
			if not GLIUtility.is_file(self._client_configuration.get_root_mount_point()+"/usr/portage/distfiles"):
				exitstatus = self._run("mkdir /usr/portage/distfiles",True)
				if exitstatus != 0:
					raise "MkdirError","Making the distfiles directory failed."
			exitstatus = self._run("cp /mnt/cdrom/distfiles/* "+self._client_configuration.get_root_mount_point()+"/usr/portage/distfiles/")
			if exitstatus != 0:
				raise "PortageError","Failed to copy the distfiles to the new system"
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
		
	def set_timezone(self):
		"Sets the timezone for the new environment"

		# Dependency checking		
		self._depends("unpack_tarball")
		#self._process_desc("Setting the timezone")

		# Set symlink
		if not os.access(self._client_configuration.get_root_mount_point() + "/etc/localtime", os.W_OK):
			os.symlink(self._client_configuration.get_root_mount_point() + "/usr/share/zoneinfo/" + self._install_profile.get_time_zone(), self._client_configuration.get_root_mount_point() + "/etc/localtime")
		if not (self._install_profile.get_time_zone() == "UTC"):
			self._edit_config(self._client_configuration.get_root_mount_point() + "/etc/rc.conf", "CLOCK", "local")
		
	def configure_fstab(self):
		"Configures fstab"
		# Dependency checking		
		self._depends("unpack_tarball")
		newfstab = ""
		partitions = self._install_profile.get_fstab()
		for partition in partitions:
			if not GLIUtility.is_file(self._client_configuration.get_root_mount_point()+partition):
				exitstatus = self._run("mkdir " + partition, True)
				if exitstatus != 0:
					raise "MkdirError", "Making the mount point failed!"
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
			
		file_name = self._client_configuration.get_root_mount_point() + "/etc/fstab"	
		try:
			shutil.move(file_name, file_name + ".OLDdefault")
		except:
			pass
		f = open(file_name, 'w')
		f.writelines(newfstab)
		f.close()


	def emerge_kernel_sources(self):
		"Fetches desired kernel sources"
		# Dependency checking		
		self._depends("emerge_system")
		exitstatus = self._emerge(self._install_profile.get_kernel_source_pkg())
		if exitstatus != 0:
			raise "EmergeKernelSourcesError", "Could not retrieve kernel sources!"
		try:
			os.stat(self._client_configuration.get_root_mount_point() + "/usr/src/linux")
		except:
			kernels = os.listdir(self._client_configuration.get_root_mount_point()+"/usr/src")
			found_a_kernel = False
			counter = 0
			while not found_a_kernel:
				if kernels[counter][0:6]=="linux-":
					exitstatus = self._run("ln -s /usr/src/"+kernels[counter]+ " /usr/src/linux",True)
					found_a_kernel = True
				else:
					counter = counter + 1

	def build_kernel(self):
		"Builds kernel"
		# Dependency checking		
		self._depends("emerge_kernel_sources")
		
		exitstatus = self._emerge("genkernel")
		if exitstatus != 0:
			raise "EmergeGenKernelError", "Could not emerge genkernel!"

		
		# Null the genkernel_options
		genkernel_options = ""

		# Get the uri to the kernel config
		kernel_config_uri = self._install_profile.get_kernel_config_uri()
		
		# If the uri for the kernel config is not null, then
		if kernel_config_uri != "":
			self._get_uri(kernel_config_uri, self._client_configuration.get_root_mount_point() + "/root/kernel_config")
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
		exitstatus = self._run("genkernel all " + genkernel_options, True)
		if exitstatus != 0:
			raise "KernelBuildError", "Could not build kernel!"
			
	def install_logging_daemon(self):
		"Installs and sets up logger"
		# Dependency checking		
		self._depends("emerge_system")
		
		# Get loggin daemon info
		logging_daemon_pkg = self._install_profile.get_logging_daemon_pkg()
		if logging_daemon_pkg:
			# Emerge Logging Daemon
			exitstatus = self._emerge(logging_daemon_pkg)
			if exitstatus != 0:
				raise "LoggingDaemonError", "Could not emerge " + logging_daemon_pkg + "!"

			# Add Logging Daemon to default runlevel
			self._add_to_runlevel(logging_daemon_pkg)

	def install_cron_daemon(self):
		"Installs and sets up cron"
		# Dependency checking		
		self._depends("emerge_system")
		
		# Get cron daemon info
		cron_daemon_pkg = self._install_profile.get_cron_daemon_pkg()
		if cron_daemon_pkg:
			# Emerge Cron Daemon
			exitstatus = self._emerge(cron_daemon_pkg)
			if exitstatus != 0:
				raise "CronDaemonError", "Could not emerge " + cron_daemon_pkg + "!"

			# Add Cron Daemon to default runlevel
			self._add_to_runlevel(cron_daemon_pkg)
		
			# If the Cron Daemon is not vixie-cron, run crontab			
			if cron_daemon_pkg != "vixie-cron":
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
		# This is the x86 way.. it uses grub
		# Dependency checking		
		self._depends("build_kernel")
		
		if self._install_profile.get_boot_loader_pkg():
			exitstatus = self._emerge(self._install_profile.get_boot_loader_pkg())
			if exitstatus != 0:
				raise "BootLoaderEmergeError", "Could not emerge bootloader!"
		else:
			pass
		
		boot_device = ""
		boot_minor = ""
		root_device = ""
		root_minor = ""
		grub_root_minor = ""
		grub_boot_minor = ""
		grub_boot_drive = ""
		grub_root_drive = ""
		minornum = 0
		#Assign root to the root mount point to make lines more readable
		root = self._client_configuration.get_root_mount_point()
		file_name  = root + "/boot/grub/bootdevice"
		file_name1 = root + "/boot/grub/rootdevice"
		file_name2 = root + "/boot/grub/device.map"
		file_name3 = root + "/boot/grub/kernel_name"
		foundboot = False
		partitions = self._install_profile.get_fstab()
		for partition in partitions:
			#if find a /boot then stop.. else we'll take a / and overwrite with a /boot if we find it too.
			if (partition == "/boot"):
				#try to get the drive LETTER from /dev/hdc1 8th character
				boot_minor = partitions[partition][0][8]
				grub_boot_minor = str(int(boot_minor) - 1)
				boot_device = partitions[partition][0][0:8]
				foundboot = True
			if ( (partition == "/") and (not foundboot) ):
				boot_minor = partitions[partition][0][8]
				grub_boot_minor = str(int(boot_minor) - 1)
				boot_device = partitions[partition][0][0:8]
				#Foundboot IS STILL FALSE
			if partition == "/":
				root_minor = partitions[partition][0][8]
				grub_root_minor = str(int(root_minor) - 1)
				root_device = partitions[partition][0][0:8]
		
		exitstatus0 = self._run("ls -l " + boot_device + " > " + file_name)
		exitstatus1 = self._run("ls -l " + root_device + " > " + file_name1)
		exitstatus2 = self._run("echo quit | "+ root+"/sbin/grub --device-map="+file_name2)
		exitstatus3 = self._run("ls "+root+"/boot/kernel-* > "+file_name3)
		exitstatus4 = self._run("ls "+root+"/boot/initrd-* >> "+file_name3)
		if (exitstatus0 != 0) or (exitstatus1 != 0) or (exitstatus2 != 0) or (exitstatus3 != 0) or (exitstatus4 != 0):
			raise "Bootloadererror", "Error in one of THE FOUR run commands"
		
		"""
		read the device map.  sample looks like this:
		(fd0)   /dev/floppy/0
		(hd0)   /dev/ide/host2/bus0/target0/lun0/disc
		(hd1)   /dev/ide/host0/bus0/target0/lun0/disc
		(hd2)   /dev/ide/host0/bus0/target1/lun0/disc
		"""
		e = open(file_name)   #Looking for the boot device
		ls_output = e.readlines()
		e.close()
		# looks like lr-xr-xr-x  1 root root 32 Oct  1 16:09 /dev/hda -> ide/host0/bus0/target0/lun0/disc
		ls_output = ls_output[0].split(">")[-1]
		ls_output = ls_output[1:]

		eb = open(file_name1)  #Looking for the root device
		ls_outputb = eb.readlines()
		eb.close()
		ls_outputb = ls_outputb[0].split(">")[-1]
		ls_outputb = ls_outputb[1:]
		
		# Search for the key
		f = open(file_name2)
		file = f.readlines()
		f.close()
		for i in range(len(file)):
			if file[i][11:] == ls_output:
				#eurika we found the drivenum
				grub_boot_drive = file[i][1:4]
			if file[i][11:] == ls_outputb:
				grub_root_drive = file[i][1:4]
		if (not grub_root_drive) or (not grub_boot_drive):
			raise "BootloaderError","Couldn't find the drive num in the list from the device.map"
				
		g = open(file_name3)
		kernel_name = g.readlines()
		g.close()
		if not kernel_name[0]:
			raise "BootloaderError","Error: We have no kernel in /boot to put in the grub.conf file!"
		kernel_name = map(string.strip, kernel_name)
		kernel_name[0] = kernel_name[0].split(root)[1]
		kernel_name[1] = kernel_name[1].split(root)[1]
		#-------------------------------------------------------------
		#OK, now that we have all the info, let's build that grub.conf
		newgrubconf = ""
		newgrubconf += "default 0\ntimeout 30\n"
		if foundboot:  #we have a /boot
			newgrubconf += "splashimage=(" + grub_boot_drive + "," + grub_boot_minor + ")/grub/splash.xpm.gz\n"
		else: #we have / and /boot needs to be included
			newgrubconf += "splashimage=(" + grub_boot_drive + "," + grub_boot_minor + ")/boot/grub/splash.xpm.gz\n"
			
		newgrubconf += "title=Gentoo Linux\n"
		newgrubconf += "root (" + grub_boot_drive + "," + grub_boot_minor + ")\n"
		if foundboot:
			newgrubconf += "kernel " + kernel_name[0][5:] + " root=/dev/ram0 init=/linuxrc ramdisk=8192 real_root="
			newgrubconf += root_device + root_minor + "\n"
			newgrubconf += "initrd " + kernel_name[1][5:] + "\n"
		else:
			newgrubconf += "kernel /boot" + kernel_name[0][5:] + " root=/dev/ram0 init=/linuxrc ramdisk=8192 real_root="
			newgrubconf += root_device + root_minor + "\n"
			newgrubconf += "initrd /boot" + kernel_name[1][5:] + "\n"
		
		#-------------------------------------------------------------
		#OK, now that the file is built.  Install grub.
		#cp /proc/mounts /etc/mtab
		#grub-install --root-directory=/boot /dev/hda
		#shutil.copy("/proc/mounts",root +"/etc/mtab")
		grubinstallstring = "echo -en 'root ("+grub_boot_drive + "," + grub_boot_minor + ")\n"
		if not self._install_profile.get_boot_loader_mbr():
			grubinstallstring +="setup ("+grub_boot_drive + "," + grub_boot_minor + ")\n"
		else:
			grubinstallstring +="setup ("+grub_boot_drive+")\n"
		grubinstallstring += "quit\n' | "+root+"/sbin/grub"
		print grubinstallstring
		exitstatus = self._run(grubinstallstring,True)
		if exitstatus != 0:
			raise "GrubInstallError", "Could not install grub!"
			
		#now make the grub.conf file
		file_name = root + "/boot/grub/grub.conf"	
		try:
			shutil.move(file_name, file_name + ".OLDdefault")
		except:
			pass
		f = open(file_name, 'w')
		f.writelines(newgrubconf)
		f.close()
		
	def update_config_files(self):
		"Runs etc-update (overwriting all config files), then re-configures the modified ones"
		# Dependency checking		
		self._depends("emerge_system")
		
		# Run etc-update overwriting all config files
		status = GLIUtility.spawn('echo "-5" | etc-update', chroot=self._chroot_dir)
		if not GLIUtility.exit_success(status):
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
			self._edit_config(self._client_configuration.get_root_mount_point() + "/etc/rc.conf", key, option[key])
			
	def setup_network_post(self):
		"Sets up the network for the first boot"
		# Dependency checking		
		self._depends("unpack_tarball")
		
		# Get hostname, domainname and nisdomainname
		hostname = self._install_profile.get_hostname()
		domainname = self._install_profile.get_domainname()
		nisdomainname = self._install_profile.get_nisdomainname()
		
		# Write the hostname to the hostname file		
		open(self._client_configuration.get_root_mount_point() + "/etc/hostname", "w").write(hostname + "\n")
		
		# Write the domainname to the nisdomainname file
		if domainname:
			open(self._client_configuration.get_root_mount_point() + "/etc/dnsdomainname", "w").write(domainname + "\n")
		
		# Write the nisdomainname to the nisdomainname file
		if nisdomainname:
			open(self._client_configuration.get_root_mount_point() + "/etc/nisdomainname", "w").write(nisdomainname + "\n")
			
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
		self._edit_config(self._client_configuration.get_root_mount_point() + "/etc/hosts", hosts_ip, hosts_line, True, '\t', False)

		#
		# SET DEFAULT GATEWAY
		#

		# Get default gateway
		default_gateway = self._install_profile.get_default_gateway()
		
		# If the default gateway exists, add it
		if default_gateway:
			self._edit_config(self._client_configuration.get_root_mount_point() + "/etc/conf.d/net", "gateway", default_gateway)
			
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
		resolve_conf = open(self._client_configuration.get_root_mount_point() + "/etc/resolv.conf", "w")
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
					exitstatus = self._run("rc-update add net." + interface + " default", True)
					if exitstatus != 0:
						raise "NetStartupError", "Cannot add interface " + interface + " to the default runlevel!"

			# Set what kind of interface it is
			interface_type = interface[:3]
		
			# Check to see if there is a startup script for this interface, if there isn't link to the proper script
			try:
				os.stat(self._client_configuration.get_root_mount_point() + "/etc/init.d/net." + interface)
			except:
				os.symlink(self._client_configuration.get_root_mount_point() + "/etc/init.d/net." + interface_type +  "0", self._client_configuration.get_root_mount_point() + "/etc/init.d/net." + interface)				
		
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
					self._edit_config(self._client_configuration.get_root_mount_point() + "/etc/conf.d/net", "iface_" + interface, ip + " broadcast " + broadcast + " netmask " + netmask)
					
					# If aliases are set
			#		if aliases:
					
						# Parse aliases to format alias info
			#			for alias in aliases:
			#				alias_ips.append(alias[0])
			#				alias_broadcasts.append(alias[1])
			#				alias_netmasks.append(allias[2])
						
						# Once the alias info has been gathered, then write it out
						# Alias ips first
			#			self._edit_config(self._client_configuration.get_root_mount_point() + "/etc/conf.d/net", "alias_" + interface, string.join(alias_ips))
						# Alias broadcasts next
			#			self._edit_config(self._client_configuration.get_root_mount_point() + "/etc/conf.d/net", "broadcast_" + interface, string.join(alias_broadcasts))
						# Alias netmasks last
			#			self._edit_config(self._client_configuration.get_root_mount_point() + "/etc/conf.d/net", "netmask_" + interface, string.join(alias_netmasks))

				#
				# DHCP IP
				#
				else:
					self._edit_config(self._client_configuration.get_root_mount_point() + "/etc/conf.d/net", "iface_" + interface, "dhcp")
							
	def set_root_password(self):
		"Sets the root password"
		# Dependency checking		
		self._depends("emerge_system")
		
		status = GLIUtility.spawn('echo "root:' + self._install_profile.get_root_pass_hash() + '" | chpasswd -e', chroot=self._chroot_dir)
		if not GLIUtility.exit_success(status):
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
			exitstatus = GLIUtility.spawn('useradd ' + string.join(options) + ' ' + username, chroot=self._chroot_dir)
			if not GLIUtility.exit_success(exitstatus):
				raise "AddUserError", "Failure to add user " + username

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
