"""
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
Gentoo Linux Installer

$Id: x86ArchitectureTemplate.py,v 1.145 2006/09/01 23:08:55 agaffney Exp $
Copyright 2004 Gentoo Technologies Inc.


This fills in x86 specific functions.
"""

import GLIUtility, string, time
from GLIArchitectureTemplate import ArchitectureTemplate
from GLIException import *

class x86ArchitectureTemplate(ArchitectureTemplate):
	def __init__(self,configuration=None, install_profile=None, client_controller=None):
		ArchitectureTemplate.__init__(self, configuration, install_profile, client_controller)
		self._architecture_name = 'x86'
		self._kernel_bzimage = "arch/i386/boot/bzImage"

	def install_bootloader(self):
		"Installs and configures bootloader"
		#
		# THIS IS ARCHITECTURE DEPENDANT!!!
		# This is the x86 way.. it uses grub

		bootloader_pkg = self._install_profile.get_boot_loader_pkg()

		# first install bootloader
		if bootloader_pkg and bootloader_pkg.lower() != "none":
			exitstatus = self._portage.emerge(bootloader_pkg)
#			if not GLIUtility.exitsuccess(exitstatus):
#				raise GLIException("BootLoaderEmergeError", 'fatal', 'install_bootloader', "Could not emerge bootloader!")
#			else:
			self._logger.log("Emerged the selected bootloader.")
		
		# now configure said bootloader
		# null boot-loader first
		if bootloader_pkg.lower() == "none":
			return
		elif "grub" in bootloader_pkg: # this catches 'grub-static' as well as '=sys-boot/grub-0.95*'
			self._configure_grub()
		elif "lilo" in bootloader_pkg:
			self._configure_lilo()
		# probably should add in some more bootloaders
		# dvhtool, raincoat, netboot, gnu-efi, cromwell, syslinux, psoload
		else:
			raise GLIException("BootLoaderError",'fatal','install_bootloader',"Don't know how to configure this bootloader: "+bootloader_pkg)
		
	def _configure_grub(self):
		self.build_mode = self._install_profile.get_kernel_build_method()
		self._gather_grub_drive_info()
		root = self._chroot_dir
		exitstatus2, kernel_names = GLIUtility.spawn("ls -1 --color=no " + root + "/boot/kernel-*", return_output=True)
		self._logger.log("Output of Kernel Names:\n"+kernel_names)
		if not GLIUtility.exitsuccess(exitstatus2):
			raise GLIException("BootloaderError", 'fatal', '_configure_grub', "Error listing the kernels in /boot")
		if self.build_mode == "genkernel" or self._install_profile.get_kernel_source_pkg() == "livecd-kernel":
			exitstatus3, initrd_names = GLIUtility.spawn("ls -1 --color=no " + root + "/boot/init*", return_output=True)
			self._logger.log("Output of Initrd Names:\n"+initrd_names)
		if not GLIUtility.exitsuccess(exitstatus3):
			raise GLIException("BootloaderError", 'fatal', '_configure_grub', "Error listing the initrds")
		self._logger.log("Bootloader: the three information gathering commands have been run")
		
		if not kernel_names[0]:
			raise GLIException("BootloaderError", 'fatal', '_configure_grub',"Error: We have no kernel in /boot to put in the grub.conf file!")
			
		#-------------------------------------------------------------
		#OK, now that we have all the info, let's build that grub.conf
		newgrubconf = ""
		newgrubconf += "default 0\ntimeout 30\n"
		if self.foundboot:  #we have a /boot
			newgrubconf += "splashimage=(" + self.grub_boot_drive + "," + self.grub_boot_minor + ")/grub/splash.xpm.gz\n"
		else: #we have / and /boot needs to be included
			newgrubconf += "splashimage=(" + self.grub_boot_drive + "," + self.grub_boot_minor + ")/boot/grub/splash.xpm.gz\n"
		if self._install_profile.get_bootloader_kernel_args(): 
			bootloader_kernel_args = self._install_profile.get_bootloader_kernel_args()
		else: bootloader_kernel_args = ""

		kernel_names = map(string.strip, kernel_names.strip().split("\n"))
		initrd_names = map(string.strip, initrd_names.strip().split("\n"))
		grub_kernel_name = kernel_names[-1].split(root)[-1]
		if initrd_names: grub_initrd_name = initrd_names[-1].split(root)[-1]
#		for i in range(len(kernel_names)):
#			grub_kernel_name = kernel_names[i].split(root)[-1]
#		for i in range(len(initrd_names)):  #this should be okay if blank.
#			grub_initrd_name = initrd_names[i].split(root)[-1]
		#i think this means take the last one it finds.. i.e. the newest.
		
		newgrubconf += "title=Gentoo Linux\n"
		newgrubconf += "root (" + self.grub_boot_drive + "," + self.grub_boot_minor + ")\n"
		if self.build_mode != "genkernel" and self._install_profile.get_kernel_source_pkg() != "livecd-kernel":  #using CUSTOM kernel
			if self.foundboot:
				newgrubconf += "kernel " + grub_kernel_name[5:] + " root="+self.root_device+self.root_minor+"\n"
			else:
				newgrubconf += "kernel /boot"+ grub_kernel_name[5:] + " root="+self.root_device+self.root_minor+"\n"
		else: #using genkernel so it has an initrd.
			if self.foundboot:
				newgrubconf += "kernel " + grub_kernel_name[5:] + " root=/dev/ram0 init=/linuxrc ramdisk=8192 real_root="
				newgrubconf += self.root_device + self.root_minor + " " + bootloader_kernel_args + "\n"
				newgrubconf += "initrd " + grub_initrd_name[5:] + "\n"
			else:
				newgrubconf += "kernel /boot" + grub_kernel_name[5:] + " root=/dev/ram0 init=/linuxrc ramdisk=8192 real_root="
				newgrubconf += self.root_device + self.root_minor + " " + bootloader_kernel_args + "\n"
				newgrubconf += "initrd /boot" + grub_initrd_name[5:] + "\n"
		newgrubconf = self._grub_add_windows(newgrubconf)
		#now make the grub.conf file
		file_name = root + "/boot/grub/grub.conf"	
		try:
			shutil.move(file_name, file_name + ".OLDdefault")
		except:
			pass
		f = open(file_name, 'w')
		f.writelines(newgrubconf)
		f.close()
		self._logger.log("Grub installed and configured. Contents of grub.conf:\n"+newgrubconf)
		self._logger.log("Grub has not yet been run.  If a normal install, it will now be run.")
		
	def _gather_grub_drive_info(self):
		self.boot_minor = ""
		self.boot_device = ""
		self.root_device = ""
		self.root_minor = ""
		self.mbr_device = ""
		self.grub_root_minor = ""
		self.grub_boot_minor = ""
		self.grub_boot_drive = ""
		self.grub_root_drive = ""
		self.grub_mbr_drive = ""
		minornum = 0
		#Assign root to the root mount point to make lines more readable
		root = self._chroot_dir


		self.foundboot = False
		parts = self._install_profile.get_partition_tables()
		for device in parts:
			tmp_partitions = parts[device] #.get_install_profile_structure()
			for partition in tmp_partitions:
				mountpoint = tmp_partitions[partition]['mountpoint']
				if (mountpoint == "/boot"):
					self.foundboot = True
				if (( (mountpoint == "/") and (not self.foundboot) ) or (mountpoint == "/boot")):
					self.boot_minor = str(int(tmp_partitions[partition]['minor']))
					self.grub_boot_minor = str(int(tmp_partitions[partition]['minor']) - 1)
					self.boot_device = device
					self.mbr_device = device
				if mountpoint == "/":
					self.root_minor = str(int(tmp_partitions[partition]['minor']))
					self.grub_root_minor = str(int(tmp_partitions[partition]['minor']) - 1)
					self.root_device = device
		#RESET the boot device if one is stored already
		if self._install_profile.get_boot_device():
			self.mbr_device = self._install_profile.get_boot_device()
			self._logger.log("Found a mbr device: " + self.mbr_device)
		
		self.grub_boot_drive = self._map_device_to_grub_device(self.boot_device)
		self.grub_root_drive = self._map_device_to_grub_device(self.root_device)
		self.grub_mbr_drive = self._map_device_to_grub_device(self.mbr_device)
		
		if (not self.grub_root_drive) or (not self.grub_boot_drive):
			raise GLIException("BootloaderError", 'fatal', '_gather_grub_drive_info',"Couldn't find the drive num in the list from the device.map")

	def _grub_add_windows(self, newgrubconf):
		parts = self._install_profile.get_partition_tables()
		for device in parts:
			tmp_partitions = parts[device] #.get_install_profile_structure()
			for partition in tmp_partitions:
				if (tmp_partitions[partition]['type'] == "fat32") or (tmp_partitions[partition]['type'] == "ntfs"):
					grub_dev = self._map_device_to_grub_device(device)
					newgrubconf += "\ntitle=Possible Windows P"+str(int(tmp_partitions[partition]['minor']))+"\n"
					newgrubconf += "rootnoverify ("+grub_dev+","+str(int(tmp_partitions[partition]['minor'] -1))+")\n"
					newgrubconf += "makeactive\nchainloader +1\n\n"
		return newgrubconf

	def _configure_lilo(self):
		self.build_mode = self._install_profile.get_kernel_build_method()
		self._gather_lilo_drive_info()
		root = self._chroot_dir
		file_name3 = root + "/boot/kernel_name"
		root = self._chroot_dir
		exitstatus0 = GLIUtility.spawn("ls "+root+"/boot/kernel-* > "+file_name3)
		if (exitstatus0 != 0):
			raise GLIException("BootloaderError", 'fatal', '_configure_lilo', "Could not list kernels in /boot or no kernels found.")
		if self.build_mode == "genkernel" or self._install_profile.get_kernel_source_pkg() == "livecd-kernel":
			exitstatus1 = GLIUtility.spawn("ls "+root+"/boot/init* >> "+file_name3)
			if (exitstatus1 != 0):
				raise GLIException("BootloaderError", 'fatal', '_configure_lilo', "Could not list initrds in /boot")
		g = open(file_name3)
		kernel_name = g.readlines()
		g.close()
		if not kernel_name[0]:
			raise GLIException("BootloaderError", 'fatal', '_configure_lilo',"Error: We have no kernel in /boot to put in the grub.conf file!")
		kernel_name = map(string.strip, kernel_name)
		kernel_name[0] = kernel_name[0].split(root)[1]
		kernel_name[1] = kernel_name[1].split(root)[1]
		if self._install_profile.get_bootloader_kernel_args(): bootloader_kernel_args = self._install_profile.get_bootloader_kernel_args()
		else: bootloader_kernel_args = ""
		#-------------------------------------------------------------
		#time to build the lilo.conf
		newliloconf = ""
		if self._install_profile.get_boot_loader_mbr():
			newliloconf += "boot="+self.mbr_device+"   # Install LILO in the MBR \n"
		else:
			newliloconf += "boot="+self.boot_device+self.boot_minor+"   # Install LILO in the MBR \n"
		newliloconf += "prompt                    # Give the user the chance to select another section\n"
		newliloconf += "timeout=50                # Wait 5 (five) seconds before booting the default section\n"
		newliloconf += "default=gentoo            # When the timeout has passed, boot the \"gentoo\" section\n"
		newliloconf += "# Only if you use framebuffer. Otherwise remove the following line:\n"
		if not self._install_profile.get_kernel_bootsplash():
			newliloconf += "#"
		newliloconf += "vga=788                   # Framebuffer setting. Adjust to your own will\n"
		newliloconf += "image=/boot"+kernel_name[0][5:]+" \n"
		newliloconf += "  label=gentoo \n  read-only \n"
		if self.build_mode != "genkernel" and self._install_profile.get_kernel_source_pkg() != "livecd-kernel": 
			newliloconf += "  root="+self.root_device+self.root_minor+" \n"
			if bootloader_kernel_args:
				newliloconf += "  append=\""+bootloader_kernel_args+"\" \n"
		else:
			newliloconf += "  root=/dev/ram0 \n"
			newliloconf += "  append=\"init=/linuxrc ramdisk=8192 real_root="+self.root_device+self.root_minor + " " + bootloader_kernel_args + "\" \n"
			newliloconf += "  initrd=/boot"+kernel_name[1][5:] + "\n\n"
		newliloconf = self._lilo_add_windows(newliloconf)
		#now make the lilo.conf file
		file_name = root + "/etc/lilo.conf"	
		try:
			shutil.move(file_name, file_name + ".OLDdefault")
		except:
			pass
		f = open(file_name, 'w')
		f.writelines(newliloconf)
		f.close()
		self._logger.log("Lilo installed and configured.  Not run yet.")
		
	def _gather_lilo_drive_info(self):
		self.boot_device = ""
		self.boot_minor = ""
		self.root_device = ""
		self.root_minor = ""
		self.mbr_device = ""
		minornum = 0
		#Assign root to the root mount point to make lines more readable
		root = self._chroot_dir
		self.foundboot = False
		parts = self._install_profile.get_partition_tables()
		for device in parts:
			tmp_partitions = parts[device] #.get_install_profile_structure()
			for partition in tmp_partitions:
				mountpoint = tmp_partitions[partition]['mountpoint']
				if (mountpoint == "/boot"):
					self.foundboot = True
				if (( (mountpoint == "/") and (not self.foundboot) ) or (mountpoint == "/boot")):
					self.boot_minor = str(int(tmp_partitions[partition]['minor']))
					self.boot_device = device
					self.mbr_device = device
				if mountpoint == "/":
					self.root_minor = str(int(tmp_partitions[partition]['minor']))
					self.root_device = device
		#RESET the boot device if one is stored already
		if self._install_profile.get_boot_device():
			self.mbr_device = self._install_profile.get_boot_device()
			self._logger.log("Found a mbr device: " + self.mbr_device)			
		
	def _lilo_add_windows(self, newliloconf):
		parts = self._install_profile.get_partition_tables()
		for device in parts:
			tmp_partitions = parts[device] #.get_install_profile_structure()
			for partition in tmp_partitions:
				if (tmp_partitions[partition]['type'] == "fat32") or (tmp_partitions[partition]['type'] == "ntfs"):
					newliloconf += "other="+device+str(int(tmp_partitions[partition]['minor']))+"\n"
					newliloconf += "label=Windows_P"+str(int(tmp_partitions[partition]['minor']))+"\n\n"
		return newliloconf
		
	def _map_device_to_grub_device(self, device):
		file_name = self._chroot_dir + "/boot/grub/glidevice.map"
		#If we can't find it, make it.  If we STILL can't find it. die.
		if not GLIUtility.is_file(file_name):
			exitstatus1 = GLIUtility.spawn("echo quit | "+ self._chroot_dir+"/sbin/grub --batch --no-floppy --device-map="+file_name, logfile=self._compile_logfile, append_log=True)
		if not GLIUtility.is_file(file_name):
			raise GLIException("BootloaderError", 'fatal', '_configure_grub', "Error making the new device map.")
		"""
		read the device map.  sample looks like this:
		(fd0)   /dev/floppy/0
		(hd0)   /dev/sda
		(hd1)   /dev/hda
		(hd2)   /dev/hdb
		"""
		
		# Search for the key
		f = open(file_name)  #open the device map
		file = f.readlines()
		f.close()	
		for i in range(len(file)):
			if file[i][6:-1] == device:
				return file[i][1:4]
		raise GLIException("BootloaderError", 'fatal', '_map_device_to_grub_device', "ERROR, could not map"+device+" to anything in the device map")

	def setup_and_run_bootloader(self):
		bootloader_pkg = self._install_profile.get_boot_loader_pkg()
		if bootloader_pkg.lower() == "none":
			return
		elif "grub" in bootloader_pkg: # this catches 'grub-static' as well as '=sys-boot/grub-0.95*'
			self._setup_grub()
		elif "lilo" in bootloader_pkg:
			self._setup_lilo()
		# probably should add in some more bootloaders
		# dvhtool, raincoat, netboot, gnu-efi, cromwell, syslinux, psoload
		else:
			raise GLIException("BootLoaderError",'fatal','setup_and_run_bootloader',"Don't know how to configure this bootloader: "+bootloader_pkg)

	def _setup_grub(self):
		#-------------------------------------------------------------
		#OK, now that the file is built.  Install grub.
		#cp /proc/mounts /etc/mtab
		#grub-install --root-directory=/boot /dev/hda
		#shutil.copy("/proc/mounts",root +"/etc/mtab")
		self._gather_grub_drive_info()
		grubinstallstring = "echo -en 'root ("+self.grub_boot_drive + "," + self.grub_boot_minor + ")\n"
		if not self._install_profile.get_boot_loader_mbr():
			grubinstallstring +="setup ("+self.grub_boot_drive + "," + self.grub_boot_minor + ")\n"
		else:
			grubinstallstring +="setup ("+self.grub_mbr_drive+")\n"
		grubinstallstring += "quit\n' | "+self._chroot_dir+"/sbin/grub --batch --no-floppy"
		if self._debug: self._logger.log("DEBUG: _configure_grub(): Grub install string: " + grubinstallstring)
		exitstatus = GLIUtility.spawn(grubinstallstring, logfile=self._compile_logfile, append_log=True)
		if not GLIUtility.exitsuccess(exitstatus):
			raise GLIException("GrubInstallError", 'fatal', '_setup_grub', "Could not install grub!")
		self._logger.log("Bootloader: grub has been installed!")

	def _setup_lilo(self):
		#-------------------------------------------------------------
		#OK, now that the file is built.  Install lilo.
		exitstatus = GLIUtility.spawn("/sbin/lilo",chroot=self._chroot_dir, logfile=self._compile_logfile, append_log=True)
		if exitstatus != 0:
			raise GLIException("LiloInstallError", 'fatal', '_setup_lilo', "Running lilo failed!")
		self._logger.log("Bootloader: lilo has been run/installed!")
