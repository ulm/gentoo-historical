"""
Gentoo Linux Installer

$Id: x86ArchitectureTemplate.py,v 1.6 2005/01/07 05:07:23 codeman Exp $
Copyright 2004 Gentoo Technologies Inc.


This fills in x86 specific functions.
"""

import GLIUtility, string
from GLIArchitectureTemplate import ArchitectureTemplate
from GLIException import *


class x86ArchitectureTemplate(ArchitectureTemplate):
        def __init__(self,configuration=None, install_profile=None, client_controller=None):
		ArchitectureTemplate.__init__(self, configuration, install_profile, client_controller)
		self._architecture_name = 'x86'
	#	self._install_steps = [self.stage1, self.stage2, self.stage3] um, we ain't doin this this way anymore folks.

	def install_bootloader(self):
		"Installs and configures bootloader"
		#
		# THIS IS ARCHITECTURE DEPENDANT!!!
		# This is the x86 way.. it uses grub
		
		if self._install_profile.get_boot_loader_pkg():
			exitstatus = self._emerge(self._install_profile.get_boot_loader_pkg())
			if exitstatus != 0:
				raise GLIException("BootLoaderEmergeError", 'fatal', 'install_bootloader', "Could not emerge bootloader!")
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
		root = self._chroot_dir
		file_name  = root + "/boot/grub/bootdevice"
		file_name1 = root + "/boot/grub/rootdevice"
		file_name2 = root + "/boot/grub/device.map"
		file_name3 = root + "/boot/grub/kernel_name"
		foundboot = False
		#partitions = self._install_profile.get_fstab()
		parts = self._install_profile.get_partition_tables()
		for device in parts:
		#in parts['/dev/hda']
			for partition in parts[device]:
				#print parts[device][partition]
				mountpoint = parts[device][partition]['mountpoint']
				if (mountpoint == "/boot"):
					foundboot = True
				if (( (mountpoint == "/") and (not foundboot) ) or (mountpoint == "/boot")):
					boot_minor = str(parts[device][partition]['minor'])
					grub_boot_minor = str(parts[device][partition]['minor'] - 1)
					boot_device = device
				if mountpoint == "/":
					root_minor = str(parts[device][partition]['minor'])
					grub_root_minor = str(parts[device][partition]['minor'] - 1)
					root_device = device
				
					
		#for partition in partitions:
			#if find a /boot then stop.. else we'll take a / and overwrite with a /boot if we find it too.
		#	if (partition == "/boot"):
				#try to get the drive LETTER from /dev/hdc1 8th character
		#		boot_minor = partitions[partition][0][8]
		#		grub_boot_minor = str(int(boot_minor) - 1)
		#		boot_device = partitions[partition][0][0:8]
		#		foundboot = True
		#	if ( (partition == "/") and (not foundboot) ):
		#		boot_minor = partitions[partition][0][8]
		#		grub_boot_minor = str(int(boot_minor) - 1)
		#		boot_device = partitions[partition][0][0:8]
				#Foundboot IS STILL FALSE
		#	if partition == "/":
		#		root_minor = partitions[partition][0][8]
		#		grub_root_minor = str(int(root_minor) - 1)
		#		root_device = partitions[partition][0][0:8]
		
		exitstatus0 = GLIUtility.spawn("ls -l " + boot_device + " > " + file_name)
		exitstatus1 = GLIUtility.spawn("ls -l " + root_device + " > " + file_name1)
		exitstatus2 = GLIUtility.spawn("echo quit | "+ root+"/sbin/grub --device-map="+file_name2)
		exitstatus3 = GLIUtility.spawn("ls "+root+"/boot/kernel-* > "+file_name3)
		exitstatus4 = GLIUtility.spawn("ls "+root+"/boot/initrd-* >> "+file_name3)
		if (exitstatus0 != 0) or (exitstatus1 != 0) or (exitstatus2 != 0) or (exitstatus3 != 0) or (exitstatus4 != 0):
			raise GLIException("BootloaderError", 'fatal', 'install_bootloader', "Error in one of THE FOUR run commands")
		
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
			raise GLIException("BootloaderError", 'fatal', 'install_bootloader',"Couldn't find the drive num in the list from the device.map")

		g = open(file_name3)
		kernel_name = g.readlines()
		g.close()
		if not kernel_name[0]:
			raise GLIException("BootloaderError", 'fatal', 'install_bootloader',"Error: We have no kernel in /boot to put in the grub.conf file!")
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
		exitstatus = GLIUtility.spawn(grubinstallstring,chroot=self._chroot_dir)
		if exitstatus != 0:
			raise GLIException("GrubInstallError", 'fatal', 'install_bootloader', "Could not install grub!")
			
		#now make the grub.conf file
		file_name = root + "/boot/grub/grub.conf"	
		try:
			shutil.move(file_name, file_name + ".OLDdefault")
		except:
			pass
		f = open(file_name, 'w')
		f.writelines(newgrubconf)
		f.close()
