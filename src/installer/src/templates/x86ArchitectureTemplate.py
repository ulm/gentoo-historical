"""
Gentoo Linux Installer

$Id: x86ArchitectureTemplate.py,v 1.25 2005/03/26 20:11:49 codeman Exp $
Copyright 2004 Gentoo Technologies Inc.


This fills in x86 specific functions.
"""

import GLIUtility, string
from GLIArchitectureTemplate import ArchitectureTemplate
from GLIException import *
import parted

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
		
		if self._install_profile.get_boot_loader_pkg():
			exitstatus = self._emerge(self._install_profile.get_boot_loader_pkg())
			if exitstatus != 0:
				raise GLIException("BootLoaderEmergeError", 'fatal', 'install_bootloader', "Could not emerge bootloader!")
		else:
			self._logger.log("Emerged the selected bootloader.")
		
		if self._install_profile.get_boot_loader_pkg() == "grub":
			self._install_grub()
		elif self._install_profile.get_boot_loader_pkg() == "lilo":
			self._install_lilo()
		else:
			raise GLIException("BootLoaderError",'fatal','install_bootloader',"Invalid bootloader selected:"+self._install_profile.get_boot_loader_pkg())
		
	def _sectors_to_megabytes(self, sectors, sector_bytes=512):
		return float((float(sectors) * sector_bytes)/ float(1024*1024))

	def _add_partition(self, disk, start, end, type, fs):
		types = { 'primary': parted.PARTITION_PRIMARY, 'extended': parted.PARTITION_EXTENDED, 'logical': parted.PARTITION_LOGICAL }
		fsTypes = {}
		fs_type = parted.file_system_type_get_next ()
		while fs_type:
			fsTypes[fs_type.name] = fs_type
			fs_type = parted.file_system_type_get_next (fs_type)
		fstype = None
		if fs: fstype = fsTypes[fs]
		newpart = disk.partition_new(types[type], fstype, start, end)
		constraint = disk.dev.constraint_any()
		disk.add_partition(newpart, constraint)

	def partition(self):
		import GLIStorageDevice
		import pprint

		MEGABYTE = 1024 * 1024
		devices_old = {}
		parts_old = {}
		parts_new = self._install_profile.get_partition_tables()
		drives = GLIStorageDevice.detect_devices()
		drives.sort()
		for drive in drives:
			devices_old[drive] = GLIStorageDevice.Device(drive)
			devices_old[drive].set_partitions_from_disk()
		for part in devices_old.keys(): parts_old[part] = devices_old[part].get_install_profile_structure()

#		pp = pprint.PrettyPrinter(indent=4)
#		pp.pprint(parts_old)
#		pp.pprint(parts_new)

		for dev in parts_old.keys():
			parted_dev = parted.PedDevice.get(dev)
			parted_disk = parted.PedDisk.new(parted_dev)
			if not parts_new.has_key(dev) or not parts_new[dev]:
				self._logger.log("Partition table for " + dev + " does not exist in install profile")
				#print "Partition table for " + dev + " does not exist in install profile"
				continue
			if parts_new[dev][parts_new[dev].keys()[0]]['mb']:
				# Change MB/%/* into sectors
				total_sectors = parted_dev.length
				sector_size = parted_dev.sector_size
				total_mb = float(total_sectors * sector_size) / MEGABYTE
				start_sector = 63
				mb_left = total_mb
				for part in parts_new[dev]:
					tmppart = parts_new[dev][part]
					if tmppart['type'] == "extended": continue
					if tmppart['mb'][-1] == "%":
						tmppart['mb'] = float(tmppart['mb'][:-1]) / 100 * total_mb
					mb_left = mb_left - float(tmppart['mb'])
				partlist = parts_new.keys()
				partlist.sort()
				for part in partlist:
					if part > 4: continue
					tmppart = parts_new[dev][part]
					if tmppart['type'] == "extended":
						for part_log in partlist:
							if part < 5: continue
							tmppart_log = parts_new[dev][part_log]
							if not tmppart['start']:
								tmppart['start'] = start_sector
							if tmppart_log['mb'] == "*":
								tmppart_log['mb'] = mb_left
							part_bytes = int(tmppart_log['mb'] * MEGABYTE)
							part_sectors = round(part_bytes / sector_size)
							tmppart_log['start'] = start_sector
							tmppart_log['end'] = start_sector + part_sectors - 1
							tmppart['end'] = tmppart_log['end']
							start_sector = start_sector + part_sectors
						continue
					if tmppart['mb'] == "*":
						tmppart['mb'] = mb_left
					part_bytes = int(tmppart['mb'] * MEGABYTE)
					part_sectors = round(part_bytes / sector_size)
					tmppart['start'] = start_sector
					tmppart['end'] = start_sector + part_sectors - 1
					start_sector = start_sector + part_sectors
			else:
				table_changed = 1
				for part in parts_old[dev]:
					oldpart = parts_old[dev][part]
					newpart = parts_new[dev][part]
					if oldpart['type'] == newpart['type'] and oldpart['start'] == newpart['start'] and oldpart['end'] == newpart['end'] and newpart['format'] == False:
						table_changed = 0
					else:
						table_changed = 1
						break
				if not table_changed:
					self._logger.log("Partition table for " + dev + " is unchanged")
					#print "Partition table for " + dev + " is unchanged"
					continue
			parts_active = []
			parts_lba = []
			self._logger.log("Processing "+dev+"...")
			#print "\nProcessing " + dev + "..."
			# First pass to delete old partitions that aren't resized
			for part in parts_old[dev]:
				if part > 4: continue
				oldpart = parts_old[dev][part]
				matchingminor = 0
				delete = 0
				if oldpart['type'] == "extended":
					logical_to_resize = 0
					for part_log in parts_old[dev]:
						if part_log < 5: continue
						matchingminor = 0
						delete_log = 0
						for new_part in parts_new[dev]:
							if new_part < 5: continue
							tmppart = parts_new[dev][new_part]
							if int(tmppart['start']) == int(oldpart['start']) and tmppart['format'] == False and tmppart['type'] == oldpart['type'] and int(tmppart['end']) == int(oldpart['end']):
								matchingminor = new_part
								self._logger.log("  Deleting old minor " + str(part_log) + " to be recreated later")
								#print "  Deleting old minor " + str(part_log) + " to be recreated later"
								delete_log = 1
								break
							if int(tmppart['start']) == int(oldpart['start']) and tmppart['format'] == False and tmppart['type'] == oldpart['type'] and int(tmppart['end']) != int(oldpart['end']):
								matchingminor = new_part
								self._logger.log("  Ignoring old minor " + str(part_log) + " to resize later")
								#print "  Ignoring old minor " + str(part_log) + " to resize later"
								logical_to_resize = 1
								break
						if not matchingminor:
							self._logger.log("  No match found...deleting partition " + str(part_log))
							#print "  No match found...deleting partition " + str(part_log)
							parted_disk.delete_partition(parted_disk.get_partition(part_log))
						else:
							if parted_disk.get_partition(part_log).get_flag(1): # Active/boot
								self._logger.log("  Partition " + str(part_log) + " was active...noted")
								#print "  Partition " + str(part_log) + " was active...noted"
								parts_active.append(int(matchingminor))
							if parted_disk.get_partition(part_log).get_flag(7): # LBA
								self._logger.log("  Partition " + str(part_log) + " was LBA...noted")
								#print "  Partition " + str(part_log) + " was LBA...noted"
								parts_lba.append(int(matchingminor))
							if delete_log:
								parted_disk.delete_partition(parted_disk.get_partition(part_log))
					if not logical_to_resize:
						self._logger.log("  Deleting old minor " + str(part))
						#print "  Deleting old minor " + str(part)
						parted_disk.delete_partition(parted_disk.get_partition(part))
					continue
				for new_part in parts_new[dev]:
					tmppart = parts_new[dev][new_part]
					if int(tmppart['start']) == int(oldpart['start']) and tmppart['format'] == False and tmppart['type'] == oldpart['type'] and int(tmppart['end']) == int(oldpart['end']):
						matchingminor = new_part
						self._logger.log("  Deleting old minor " + str(part) + " to be recreated later")
						#print "  Deleting old minor " + str(part) + " to be recreated later"
						delete = 1
						break
					if int(tmppart['start']) == int(oldpart['start']) and tmppart['format'] == False and tmppart['type'] == oldpart['type'] and int(tmppart['end']) != int(oldpart['end']):
						matchingminor = new_part
						self._logger.log("  Ignoring old minor " + str(part) + " to resize later")
						#print "  Ignoring old minor " + str(part) + " to resize later"
						break
				if not matchingminor:
					self._logger.log("  No match found...deleting partition " + str(part))
					#print "  No match found...deleting partition " + str(part)
					parted_disk.delete_partition(parted_disk.get_partition(part))
				else:
					if parted_disk.get_partition(part).get_flag(1): # Active/boot
						self._logger.log("  Partition " + str(part) + " was active...noted")
						#print "  Partition " + str(part) + " was active...noted"
						parts_active.append(int(matchingminor))
					if parted_disk.get_partition(part).get_flag(7): # LBA
						self._logger.log("  Partition " + str(part) + " was LBA...noted")
						#print "  Partition " + str(part) + " was LBA...noted"
						parts_lba.append(int(matchingminor))
					if delete:
						parted_disk.delete_partition(parted_disk.get_partition(part))
			parted_disk.commit()
			# Second pass to resize old partitions that need to be resized
			self._logger.log("Partitioning: Second pass...")
			#print " Second pass..."
			for part in parts_old[dev]:
				oldpart = parts_old[dev][part]
				for new_part in parts_new[dev]:
					tmppart = parts_new[dev][new_part]
					if int(tmppart['start']) == int(oldpart['start']) and tmppart['format'] == False and tmppart['type'] == oldpart['type'] and int(tmppart['end']) != int(oldpart['end']):
						self._logger.log("  Resizing old minor " + str(part) + " from " + str(oldpart['start']) + "-" + str(oldpart['end'])+  " to " + str(tmppart['start']) + "-" + str(tmppart['end']))
						#print "  Resizing old minor " + str(part) + " from " + str(oldpart['start']) + "-" + str(oldpart['end'])+  " to " + str(tmppart['start']) + "-" + str(tmppart['end'])
						type = tmppart['type']
						device = dev
						minor = part
						start = tmppart['start']
						end = tmppart['end']
						if type == "ext2" or type == "ext3":
							total_sectors = end - start + 1
							ret = GLIUtility.spawn("resize2fs " + device + str(minor) + " " + str(total_sectors) + "s")
							if ret: # Resize error
								raise GLIException("PartitionResizeError", 'fatal', 'partition', "could not resize " + dev + str(minor))
						elif type == "ntfs":
							total_sectors = end - start + 1
							total_bytes = int(total_sectors) * 512
							ret = GLIUtility.spawn("ntfsresize --size " + str(total_bytes) + " " + device + str(minor))
							if ret: # Resize error
								raise GLIException("PartitionResizeError", 'fatal', 'partition', "could not resize " + dev + str(minor))
						else:
							parted_fs = parted_disk.get_partition(part).geom.file_system_open()
							resize_constraint = parted_fs.get_resize_constraint()
							if end < (start + resize_constraint.min_size) or start != resize_constraint.start_range.start:
								raise GLIException("PartitionError", 'fatal', 'partition', "New size specified for " + dev + str(minor) + " is not within allowed boundaries")
							new_geom = resize_constraint.start_range.duplicate()
							new_geom.set_start(start)
							new_geom.set_end(end)
							try:
								parted_fs.resize(new_geom)
							except:
								raise GLIException("PartitionResizeError", 'fatal', 'partition', "could not resize " + dev + str(minor))
						self._logger.log("  Deleting old minor " + str(part) + " to be recreated in 3rd pass")
						#print "  Deleting old minor " + str(part) + " to be recreated in 3rd pass"
						parted_disk.delete_partition(parted_disk.get_partition(part))
						break
			parted_disk.delete_all()
			parted_disk.commit()
			# Third pass to create new partition table
			self._logger.log("Partitioning: Third pass.")
			#print " Third pass..."
			for part in parts_new[dev]:
				newpart = parts_new[dev][part]
				new_start, new_end = newpart['start'], newpart['end']
				if newpart['type'] == "extended":
					self._logger.log("  Adding extended partition from " + str(newpart['start']) + " to " + str(newpart['end']))
					#print "  Adding extended partition from " + str(newpart['start']) + " to " + str(newpart['end'])
					self._add_partition(parted_disk, new_start, new_end, "extended", "")
				elif int(part) < 5:
					self._logger.log("  Adding primary partition from " + str(newpart['start']) + " to " + str(newpart['end']))
					#print "  Adding primary partition from " + str(newpart['start']) + " to " + str(newpart['end'])
					self._add_partition(parted_disk, new_start, new_end, "primary", newpart['type'])
				elif int(part) > 4:
					self._logger.log("  Adding logical partition from " + str(newpart['start']) + " to " + str(newpart['end']))
					#print "  Adding logical partition from " + str(newpart['start']) + " to " + str(newpart['end'])
					self._add_partition(parted_disk, new_start, new_end, "logical", newpart['type'])
				if int(part) in parts_active and not newpart['format']:
					self._logger.log("   Partition was previously active...setting")
					#print "   Partition was previously active...setting"
					parted_disk.get_partition(part).set_flag(1)
				if int(part) in parts_lba and not newpart['format']:
					self._logger.log("   Partition was previously LBA...setting")
					#print "   Partition was previously LBA...setting"
					parted_disk.get_partition(part).set_flag(7)
				parted_disk.commit()
				if newpart['format']:
					if newpart['type'] == "ext2":
						if GLIUtility.spawn("mke2fs " + dev + str(part)):
							raise GLIException("PartitionFormatError", 'fatal', 'partition', "could't create ext2 filesystem on " + dev + str(part))
					elif newpart['type'] == "ext3":
						if GLIUtility.spawn("mke2fs -j " + dev + str(part)):
							raise GLIException("PartitionFormatError", 'fatal', 'partition', "could't create ext3 filesystem on " + dev + str(part))
					elif newpart['type'] == "linux-swap":
						if GLIUtility.spawn("mkswap " + dev + str(part)):
							raise GLIException("PartitionFormatError", 'fatal', 'partition', "could't create swap on " + dev + str(part))
					elif newpart['type'] == "fat32":
						if GLIUtility.spawn("mkfs.vfat -F 32 " + dev + str(part)):
							raise GLIException("PartitionFormatError", 'fatal', 'partition', "could't create fat32 filesystem on " + dev + str(part))
					elif newpart['type'] == "ntfs":
						if GLIUtility.spawn("mkntfs " + dev + str(part)):
							raise GLIException("PartitionFormatError", 'fatal', 'partition', "could't create ntfs filesystem on " + dev + str(part))

	def _install_grub(self):
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
		file_name2 = root + "/boot/grub/device.map"
		file_name3 = root + "/boot/grub/kernel_name"
		file_name4 = root + "/boot/grub/initrd_name"
		foundboot = False
		parts = self._install_profile.get_partition_tables()
		for device in parts:
			for partition in parts[device]:
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
		if GLIUtility.is_file(root+file_name2):
			exitstatus = GLIUtility.spawn("rm "+root+file_name2)		
		exitstatus1 = GLIUtility.spawn("echo quit | "+ root+"/sbin/grub --device-map="+file_name2)
		exitstatus2 = GLIUtility.spawn("ls "+root+"/boot/kernel-* > "+file_name3)
		exitstatus3 = GLIUtility.spawn("ls "+root+"/boot/initrd-* > "+file_name4)
		if (exitstatus1 != 0) or (exitstatus2 != 0) or (exitstatus3 != 0):
			raise GLIException("BootloaderError", 'fatal', '_install_grub', "Error in one of THE THREE run commands")
		self._logger.log("Bootloader: the three information gathering commands have been run")
		"""
		read the device map.  sample looks like this:
		(fd0)   /dev/floppy/0
		(hd0)   /dev/ide/host2/bus0/target0/lun0/disc
		(hd1)   /dev/ide/host0/bus0/target0/lun0/disc
		(hd2)   /dev/ide/host0/bus0/target1/lun0/disc
		"""
		
		# Search for the key
		f = open(file_name2)  #open the device map
		file = f.readlines()
		f.close()
		for i in range(len(file)):
			if file[i][6:-1] == boot_device:
				#eurika we found the drivenum
				grub_boot_drive = file[i][1:4]
			if file[i][6:-1] == root_device:
				grub_root_drive = file[i][1:4]
		if (not grub_root_drive) or (not grub_boot_drive):
			raise GLIException("BootloaderError", 'fatal', '_install_grub',"Couldn't find the drive num in the list from the device.map")

		g = open(file_name3)
		h = open(file_name4)
		initrd_name = h.readlines()
		kernel_name = g.readlines()
		g.close()
		h.close()
		if not kernel_name[0]:
			raise GLIException("BootloaderError", 'fatal', '_install_grub',"Error: We have no kernel in /boot to put in the grub.conf file!")
		kernel_name = map(string.strip, kernel_name)
		initrd_name = map(string.strip, initrd_name)
		for i in range(len(kernel_name)):
			grub_kernel_name = kernel_name[i].split(root)[1]
		for i in range(len(initrd_name)):
			grub_initrd_name = initrd_name[i].split(root)[1]
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
		if self._install_profile.get_kernel_config_uri() != "":  #using CUSTOM kernel
			if foundboot:
				newgrubconf += "kernel " + grub_kernel_name[5:] + " root="+root_device+root_minor+"\n"
			else:
				newgrubconf += "kernel /boot"+ grub_kernel_name[5:] + " root="+root_device+root_minor+"\n"
		else:
			if foundboot:
				newgrubconf += "kernel " + grub_kernel_name[5:] + " root=/dev/ram0 init=/linuxrc ramdisk=8192 real_root="
				newgrubconf += root_device + root_minor + "\n"
				newgrubconf += "initrd " + grub_initrd_name[5:] + "\n"
			else:
				newgrubconf += "kernel /boot" + grub_kernel_name[5:] + " root=/dev/ram0 init=/linuxrc ramdisk=8192 real_root="
				newgrubconf += root_device + root_minor + "\n"
				newgrubconf += "initrd /boot" + grub_initrd_name[5:] + "\n"
		
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
		#print grubinstallstring
		exitstatus = GLIUtility.spawn(grubinstallstring)
		if exitstatus != 0:
			raise GLIException("GrubInstallError", 'fatal', '_install_grub', "Could not install grub!")
		self._logger.log("Bootloader: grub has been installed!")
		#now make the grub.conf file
		file_name = root + "/boot/grub/grub.conf"	
		try:
			shutil.move(file_name, file_name + ".OLDdefault")
		except:
			pass
		f = open(file_name, 'w')
		f.writelines(newgrubconf)
		f.close()
		self._logger.log("Grub installed and configured.")

	def _install_lilo(self):
		boot_device = ""
		boot_minor = ""
		root_device = ""
		root_minor = ""
		minornum = 0
		#Assign root to the root mount point to make lines more readable
		root = self._chroot_dir
		file_name3 = root + "/boot/grub/kernel_name"
		foundboot = False
		parts = self._install_profile.get_partition_tables()
		for device in parts:
			for partition in parts[device]:
				mountpoint = parts[device][partition]['mountpoint']
				if (mountpoint == "/boot"):
					foundboot = True
				if (( (mountpoint == "/") and (not foundboot) ) or (mountpoint == "/boot")):
					boot_minor = str(parts[device][partition]['minor'])
					boot_device = device
				if mountpoint == "/":
					root_minor = str(parts[device][partition]['minor'])
					root_device = device
		exitstatus0 = GLIUtility.spawn("ls "+root+"/boot/kernel-* > "+file_name3)
		exitstatus1 = GLIUtility.spawn("ls "+root+"/boot/initrd-* >> "+file_name3)
		if (exitstatus0 != 0) or (exitstatus1 != 0):
			raise GLIException("BootloaderError", 'fatal', '_install_lilo', "Error in one of THE TWO run commands")
		g = open(file_name3)
		kernel_name = g.readlines()
		g.close()
		if not kernel_name[0]:
			raise GLIException("BootloaderError", 'fatal', '_install_lilo',"Error: We have no kernel in /boot to put in the grub.conf file!")
		kernel_name = map(string.strip, kernel_name)
		kernel_name[0] = kernel_name[0].split(root)[1]
		kernel_name[1] = kernel_name[1].split(root)[1]
		#-------------------------------------------------------------
		#time to build the lilo.conf
		newliloconf = ""
		if self._install_profile.get_boot_loader_mbr():
			newliloconf += "boot="+boot_device+"   # Install LILO in the MBR \n"
		else:
			newliloconf += "boot="+boot_device+boot_minor+"   # Install LILO in the MBR \n"
		newliloconf += "prompt                    # Give the user the chance to select another section\n"
		newliloconf += "timeout=50                # Wait 5 (five) seconds before booting the default section\n"
		newliloconf += "default=gentoo            # When the timeout has passed, boot the \"gentoo\" section\n"
		newliloconf += "# Only if you use framebuffer. Otherwise remove the following line:\n"
		if not self._install_profile.get_kernel_bootsplash():
			newliloconf += "#"
		newliloconf += "vga=788                   # Framebuffer setting. Adjust to your own will\n"
		newliloconf += "image=/boot"+kernel_name[0][5:]+" \n"
		newliloconf += "  label=gentoo \n  read-only \n  root=/dev/ram0 \n"
		newliloconf += "  append=\"init=/linuxrc ramdisk=8192 real_root="+root_device+root_minor+"\" \n"
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
		#-------------------------------------------------------------
		#OK, now that the file is built.  Install lilo.
		exitstatus = GLIUtility.spawn("/sbin/lilo",chroot=self._chroot_dir)
		if exitstatus != 0:
			raise GLIException("LiloInstallError", 'fatal', '_install_lilo', "Running lilo failed!")
		self._logger.log("Lilo installed, configured, and run.")
		
	def _lilo_add_windows(self, newliloconf):
		parts = self._install_profile.get_partition_tables()
		for device in parts:
			for partition in parts[device]:
				if (parts[device][partition]['type'] == "vfat") or (parts[device][partition]['type'] == "ntfs"):
					newliloconf += "other="+device+str(parts[device][partition]['minor'])+"\n"
					newliloconf += "label=Windows_P"+str(parts[device][partition]['minor'])+"\n\n"
		return newliloconf
