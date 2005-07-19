"""
Gentoo Linux Installer

$Id: x86ArchitectureTemplate.py,v 1.54 2005/07/19 08:30:08 robbat2 Exp $
Copyright 2004 Gentoo Technologies Inc.


This fills in x86 specific functions.
"""

import GLIUtility, string, time
from GLIArchitectureTemplate import ArchitectureTemplate
from GLIException import *
import parted
import GLIStorageDevice
		
MEGABYTE = 1024 * 1024

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
			exitstatus = self._emerge(bootloader_pkg)
			if exitstatus != 0:
				raise GLIException("BootLoaderEmergeError", 'fatal', 'install_bootloader', "Could not emerge bootloader!")
			else:
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
		
	def _sectors_to_megabytes(self, sectors, sector_bytes=512):
		return float((float(sectors) * sector_bytes)/ float(MEGABYTE))

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
		parts_old = {}
		tmp_parts_new = self._install_profile.get_partition_tables()
		parts_new = {}
		for device in tmp_parts_new:
			parts_new[device] = tmp_parts_new[device].get_install_profile_structure()
		detected_devices = GLIStorageDevice.detect_devices()
		for device in detected_devices:
			tmpdevice = GLIStorageDevice.Device(device)
			tmpdevice.set_partitions_from_disk()
			parts_old[device] = tmpdevice.get_install_profile_structure()

		for device in parts_new.keys():
			# Skip this device in parts_new if device isn't detected on current system
			if not device in detected_devices:
				self._logger.log("There is no physical device " + device + " detected to match the entry in the install profile...skipping")
				continue

			# Check to see if the old and new partition table structures are the same
			table_changed = 0
			for part in parts_new[device]:
				if not part in parts_old[device]:
					table_changed = 1
					break
				oldpart = parts_old[device][part]
				newpart = parts_new[device][part]
				if oldpart['type'] == newpart['type'] and oldpart['start'] == newpart['start'] and oldpart['end'] == newpart['end'] and newpart['format'] == False:
					continue
				else:
					table_changed = 1
					break
			# Skip this device if they are they same
			if not table_changed:
				self._logger.log("Partition table for " + device + " is unchanged...skipping")
				continue

			# Create pyparted objects for this device
			parted_dev = parted.PedDevice.get(device)
			try:
				parted_disk = parted.PedDisk.new(parted_dev)
			except:
				parted_disk = parted_dev.disk_new_fresh(parted.disk_type_get((tmp_parts_new[device].get_disklabel() or GLIStorageDevice.archinfo[self._architecture_name]['disklabel'])))
			new_part_list = parts_new[device].keys()
			new_part_list.sort()
			device_sectors = parted_dev.length

			# Iterate through new partitions and check for 'origminor' and 'format' == False
			for part in parts_new[device].keys():
				tmppart_new = parts_new[device][part]
				if not tmppart_new['origminor'] or tmppart_new['format']: continue
				tmppart_old = parts_old[device][tmppart_new['origminor']]
				# This partition in parts_new corresponds with an existing partitions, so we save the start/end sector and flags
				for flag in range(0, 10):
					# The 10 is completely arbitrary. If flags seem to be missed, this number should be increased
					parted_part = parted_disk.get_partition(part)
					if not parted_part: break
					if parted_part.is_flag_available(flag) and parted_part.get_flag(flag):
						if not "flags" in tmppart_new: tmppart_new['flags'] = []
						tmppart_new['flags'].append(flag)
				if tmppart_old['mb'] == tmppart_new['mb']:
					tmppart_new['start'] = tmppart_old['start']
					tmppart_new['end'] = tmppart_old['end']
				else:
					tmppart_new['start'] = tmppart_old['start']
					tmppart_new['end'] = 0

#			if parts_new[dev][parts_new[dev].keys()[0]]['mb']:
#				# Change MB/%/* into sectors
#				total_sectors = parted_dev.length
#				sector_size = parted_dev.sector_size
#				total_mb = float(total_sectors * sector_size) / MEGABYTE
#				start_sector = 0
#				mb_left = total_mb
#				for part in parts_new[dev]:
#					tmppart = parts_new[dev][part]
#					if tmppart['type'] == "extended": continue
#					if tmppart['mb'][-1] == "%":
#						tmppart['mb'] = float(tmppart['mb'][:-1]) / 100 * total_mb
#					mb_left = mb_left - float(tmppart['mb'])
#				partlist = parts_new.keys()
#				partlist.sort()
#				for part in partlist:
#					if part > 4: continue
#					tmppart = parts_new[dev][part]
#					if tmppart['type'] == "extended":
#						for part_log in partlist:
#							if part < 5: continue
#							tmppart_log = parts_new[dev][part_log]
#							if not tmppart['start']:
#								tmppart['start'] = start_sector
#							if tmppart_log['mb'] == "*":
#								tmppart_log['mb'] = mb_left
#							part_bytes = long(tmppart_log['mb'] * MEGABYTE)
#							part_sectors = round(part_bytes / sector_size)
#							tmppart_log['start'] = start_sector
#							tmppart_log['end'] = start_sector + part_sectors - 1
#							tmppart['end'] = tmppart_log['end']
#							start_sector = start_sector + part_sectors
#						continue
#					if tmppart['mb'] == "*":
#						tmppart['mb'] = mb_left
#					part_bytes = long(tmppart['mb'] * MEGABYTE)
#					part_sectors = round(part_bytes / sector_size)
#					tmppart['start'] = start_sector
#					tmppart['end'] = start_sector + part_sectors - 1
#					start_sector = start_sector + part_sectors
#			else:

			# First pass to delete old partitions that aren't resized
			self._logger.log("partitioning: Processing " + device + "...")
			for part in parts_old[device]:
				oldpart = parts_old[device][part]
				# Replace 'x86' with call function to get arch from CC
				if (GLIStorageDevice.archinfo['x86']['extended'] and part > 4) or oldpart['type'] == "free": continue
				delete = 0
				if oldpart['type'] == "extended":
					logical_to_resize = 0
					for part_log in parts_old[device]:
						if part_log < 5 or parts_old[device][part_log]['type'] == "free": continue
						delete_log = 0
						for new_part in parts_new[device]:
							if new_part < 5: continue
							tmppart = parts_new[device][new_part]
							# This partition is unchanged in the new layout
							if tmppart['origminor'] == part_log and tmppart['start'] and tmppart['end']:
								self._logger.log("  Deleting old minor " + str(part_log) + " to be recreated later")
								delete_log = 1
								break
							# This partition is resized with the data preserved in the new layout
							if tmppart['origminor'] == part_log and tmppart['start'] and not tmppart['end']:
								self._logger.log("  Ignoring old minor " + str(part_log) + " to resize later")
								logical_to_resize = 1
								break
						if delete_log:
							self._logger.log("  No match found...deleting partition " + str(part_log))
							parted_disk.delete_partition(parted_disk.get_partition(part_log))
					if not logical_to_resize:
						self._logger.log("  Deleting extended partition with minor " + str(part))
						parted_disk.delete_partition(parted_disk.get_partition(part))
					continue
				for new_part in parts_new[device]:
					tmppart = parts_new[device][new_part]
					if tmppart['origminor'] == part and tmppart['start'] and tmppart['end']:
						self._logger.log("  Deleting old minor " + str(part) + " to be recreated later")
						delete = 1
						break
					if tmppart['origminor'] == part and tmppart['start'] and not tmppart['end']:
						self._logger.log("  Ignoring old minor " + str(part) + " to resize later")
						break
				if delete:
					self._logger.log("  No match found...deleting partition " + str(part))
					parted_disk.delete_partition(parted_disk.get_partition(part))
			parted_disk.commit()

			# Second pass to resize old partitions that need to be resized
			self._logger.log("Partitioning: Second pass...")
			for part in parts_old[device]:
				oldpart = parts_old[device][part]
				for new_part in parts_new[device]:
					tmppart = parts_new[device][new_part]
					if tmppart['origminor'] == part and tmppart['start'] and not tmppart['end']:
						self._logger.log("  Resizing old minor " + str(part) + " from " + str(oldpart['start']) + "-" + str(oldpart['end'])+  " to " + str(tmppart['start']) + "-" + str(tmppart['end']))
						type = tmppart['type']
						minor = part
						start = tmppart['start']
						# Replace 512 with code to retrieve bytes per sector for device
						end = start + (long(tmppart['mb']) * MEGABYTE / 512)
						for i in new_part_list:
							if i <= new_part: continue
							if parts_new[device][i]['start'] and end >= parts_new[device][i]['start']:
								end = parts_new[device][i]['start'] - 1
							elif end >= device_sectors:
								end = device_sectors - 1
							break
						if type == "ext2" or type == "ext3":
							total_sectors = end - start + 1
							ret = GLIUtility.spawn("resize2fs " + device + str(minor) + " " + str(total_sectors) + "s")
							if ret: # Resize error
								raise GLIException("PartitionResizeError", 'fatal', 'partition', "could not resize " + device + str(minor))
						elif type == "ntfs":
							total_sectors = end - start + 1
							total_bytes = long(total_sectors) * 512
							ret = GLIUtility.spawn("ntfsresize --size " + str(total_bytes) + " " + device + str(minor))
							if ret: # Resize error
								raise GLIException("PartitionResizeError", 'fatal', 'partition', "could not resize " + device + str(minor))
						elif type == "linux-swap" or type == "fat32":
							parted_fs = parted_disk.get_partition(part).geom.file_system_open()
							resize_constraint = parted_fs.get_resize_constraint()
							if end < (start + resize_constraint.min_size) or start != resize_constraint.start_range.start:
								raise GLIException("PartitionError", 'fatal', 'partition', "New size specified for " + device + str(minor) + " is not within allowed boundaries")
							new_geom = resize_constraint.start_range.duplicate()
							new_geom.set_start(start)
							new_geom.set_end(end)
							try:
								parted_fs.resize(new_geom)
							except:
								raise GLIException("PartitionResizeError", 'fatal', 'partition', "could not resize " + device + str(minor))
						self._logger.log("  Deleting old minor " + str(part) + " to be recreated in 3rd pass")
						parted_disk.delete_partition(parted_disk.get_partition(part))
						break
			parted_disk.delete_all()
			parted_disk.commit()

			# Third pass to create new partition table
			self._logger.log("Partitioning: Third pass....creating partitions")
			start = 0
			end = 0
			extended_start = 0
			extended_end = 0
			self._logger.log("  Drive has " + str(device_sectors) + " sectors")
#			for part in parts_new[device]:
			for part in new_part_list:
				newpart = parts_new[device][part]
				self._logger.log("  Partition " + str(part) + " has " + str(newpart['mb']) + "MB")
				part_sectors = long(newpart['mb']) * MEGABYTE / 512
				end = start + part_sectors
				for i in new_part_list:
					if i <= part: continue
					if parts_new[device][i]['start'] and end >= parts_new[device][i]['start']:
						end = parts_new[device][i]['start'] - 1
					break
				# cap to end of device
				if end >= device_sectors:
					end = device_sectors - 1
				# now the actual creation
				if newpart['type'] == "free":
					# Nothing to be done for this type
					pass
				elif newpart['type'] == "extended":
					self._logger.log("  Adding extended partition " + str(part) + " from " + str(start) + " to " + str(end))
					self._add_partition(parted_disk, start, end, "extended", "")
					extended_start = start
					extended_end = end
				elif part < 5 or not GLIStorageDevice.archinfo['x86']['extended']:
					self._logger.log("  Adding primary partition " + str(part) + " from " + str(start) + " to " + str(end))
					self._add_partition(parted_disk, start, end, "primary", newpart['type'])
				elif GLIStorageDevice.archinfo['x86']['extended'] and part > 4:
					if start >= extended_end:
						start = extended_start + 1
						end = start + part_sectors
					if part == new_part_list[-1] and end > extended_end:
						end = extended_end
					self._logger.log("  Adding logical partition " + str(part) + " from " + str(start) + " to " + str(end))
					self._add_partition(parted_disk, start, end, "logical", newpart['type'])
				if "flags" in newpart:
					for flag in newpart['flags']:
						if parted_disk.get_partition(part).is_flag_available(flag):
							parted_disk.get_partition(part).set_flag(flag)
				# write to disk
				parted_disk.commit()

				# force rescan of partition table
				# Should not be needed with current stuff
				#ret = GLIUtility.spawn("partprobe "+device, logfile=self._compile_logfile, append_log=True)
				
				# now format the partition
				# extended and 'free' partitions should never be formatted
				if newpart['format'] and newpart['type'] not in ('extended', 'free'):
					devnode = device + str(int(part))
					errormsg = "could't create %s filesystem on %s" % (newpart['type'],devnode)
					# if you need a special command and
					# some base options, place it here.
					if newpart['type'] == 'linux-swap':
						cmdname = 'mkswap'
					elif newpart['type'] == 'fat32':
						cmdname = 'mkfs.vfat -F 32'
					elif newpart['type'] == 'ntfs':
						cmdname = 'mkntfs'
					# All of these types need a -f as they
					# ask for confirmation of format
					elif newpart['type'] in ('xfs','jfs','reiserfs'):
						cmdname = 'mkfs.%s -f' % (newpart['type'])
					# add common partition stuff here
					elif newpart['type'] in ('ext2','ext3'):
						cmdname = 'mkfs.%s' % (newpart['type'])
					else: # this should catch everything else
						raise GLIException("PartitionFormatError", 'fatal', 'partition',"Unknown partition type "+newpart['type'])

					# force a stat of the device so that it
					# is created on demand. (At least if I
					# recall how udev works... - robbat2).
					# sleep a bit first
					time.sleep(1)
					# now sleep until it exists
					while not GLIUtility.is_file(devnode):
						self._logger.log("Waiting for device node "+devnode+" to exist...")
						time.sleep(1)
					# one bit of extra sleep is needed, as there is a blip still
					time.sleep(1)

					# now the actual command
					cmd = "%s %s %s" % (cmdname,newpart['mkfsopts'],devnode)
					self._logger.log("  Formatting partition %s as %s with: %s" % (str(part),newpart['type'],cmd))
					# If logging is not done, then you get errors:
					# PartitionFormatError :FATAL: partition: could't create ext2 filesystem on /dev/hda1
					#if GLIUtility.spawn(cmd):
					#if GLIUtility.spawn(cmd,append_log=True,logfile='/var/log/install-mkfs.log'):
					ret = GLIUtility.spawn(cmd, logfile=self._compile_logfile, append_log=True)
					if not GLIUtility.exitsuccess(ret):
						raise GLIException("PartitionFormatError", 'fatal', 'partition', errormsg)
				start = end + 1

	def _configure_grub(self):
		build_mode = self._install_profile.get_kernel_build_method()
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
			tmp_partitions = parts[device].get_install_profile_structure()
			for partition in tmp_partitions:
				mountpoint = tmp_partitions[partition]['mountpoint']
				if (mountpoint == "/boot"):
					foundboot = True
				if (( (mountpoint == "/") and (not foundboot) ) or (mountpoint == "/boot")):
					boot_minor = str(int(tmp_partitions[partition]['minor']))
					grub_boot_minor = str(int(tmp_partitions[partition]['minor']) - 1)
					boot_device = device
				if mountpoint == "/":
					root_minor = str(int(tmp_partitions[partition]['minor']))
					grub_root_minor = str(int(tmp_partitions[partition]['minor']) - 1)
					root_device = device
		if GLIUtility.is_file(root+file_name2):
			exitstatus = GLIUtility.spawn("rm "+root+file_name2)		
		exitstatus1 = GLIUtility.spawn("echo quit | "+ root+"/sbin/grub --device-map="+file_name2)
		exitstatus2 = GLIUtility.spawn("ls "+root+"/boot/kernel-* > "+file_name3)
		if build_mode == "genkernel":
			exitstatus3 = GLIUtility.spawn("ls "+root+"/boot/initramfs-* > "+file_name4)
		else:
			exitstatus3 = GLIUtility.spawn("touch "+file_name4)
		if (exitstatus1 != 0) or (exitstatus2 != 0) or (exitstatus3 != 0):
			raise GLIException("BootloaderError", 'fatal', '_configure_grub', "Error in one of THE THREE run commands")
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
			raise GLIException("BootloaderError", 'fatal', '_configure_grub',"Couldn't find the drive num in the list from the device.map")

		g = open(file_name3)
		h = open(file_name4)
		initrd_name = h.readlines()
		kernel_name = g.readlines()
		g.close()
		h.close()
		if not kernel_name[0]:
			raise GLIException("BootloaderError", 'fatal', '_configure_grub',"Error: We have no kernel in /boot to put in the grub.conf file!")
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
		if self._install_profile.get_bootloader_kernel_args(): bootloader_kernel_args = self._install_profile.get_bootloader_kernel_args()
		else: bootloader_kernel_args = ""
		if foundboot:  #we have a /boot
			newgrubconf += "splashimage=(" + grub_boot_drive + "," + grub_boot_minor + ")/grub/splash.xpm.gz\n"
		else: #we have / and /boot needs to be included
			newgrubconf += "splashimage=(" + grub_boot_drive + "," + grub_boot_minor + ")/boot/grub/splash.xpm.gz\n"
			
		newgrubconf += "title=Gentoo Linux\n"
		newgrubconf += "root (" + grub_boot_drive + "," + grub_boot_minor + ")\n"
		if build_mode != "genkernel":  #using CUSTOM kernel
			if foundboot:
				newgrubconf += "kernel " + grub_kernel_name[5:] + " root="+root_device+root_minor+"\n"
			else:
				newgrubconf += "kernel /boot"+ grub_kernel_name[5:] + " root="+root_device+root_minor+"\n"
		else: #using genkernel so it has an initrd.
			if foundboot:
				newgrubconf += "kernel " + grub_kernel_name[5:] + " root=/dev/ram0 init=/linuxrc ramdisk=8192 real_root="
				newgrubconf += root_device + root_minor + " " + bootloader_kernel_args + "\n"
				newgrubconf += "initrd " + grub_initrd_name[5:] + "\n"
			else:
				newgrubconf += "kernel /boot" + grub_kernel_name[5:] + " root=/dev/ram0 init=/linuxrc ramdisk=8192 real_root="
				newgrubconf += root_device + root_minor + " " + bootloader_kernel_args + "\n"
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
			raise GLIException("GrubInstallError", 'fatal', '_configure_grub', "Could not install grub!")
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

	def _configure_lilo(self):
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
			tmp_partitions = parts[device]
			for partition in tmp_partitions:
				mountpoint = tmp_partitions[partition]['mountpoint']
				if (mountpoint == "/boot"):
					foundboot = True
				if (( (mountpoint == "/") and (not foundboot) ) or (mountpoint == "/boot")):
					boot_minor = str(int(tmp_partitions[partition]['minor']))
					boot_device = device
				if mountpoint == "/":
					root_minor = str(int(tmp_partitions[partition]['minor']))
					root_device = device
		exitstatus0 = GLIUtility.spawn("ls "+root+"/boot/kernel-* > "+file_name3)
		exitstatus1 = GLIUtility.spawn("ls "+root+"/boot/initrd-* >> "+file_name3)
		if (exitstatus0 != 0) or (exitstatus1 != 0):
			raise GLIException("BootloaderError", 'fatal', '_configure_lilo', "Error in one of THE TWO run commands")
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
		newliloconf += "  append=\"init=/linuxrc ramdisk=8192 real_root="+root_device+root_minor + " " + bootloader_kernel_args + "\" \n"
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
			raise GLIException("LiloInstallError", 'fatal', '_configure_lilo', "Running lilo failed!")
		self._logger.log("Lilo installed, configured, and run.")
		
	def _lilo_add_windows(self, newliloconf):
		parts = self._install_profile.get_partition_tables()
		for device in parts:
			tmp_partitions = parts[device]
			for partition in tmp_partitions:
				if (tmp_partitions[partition]['type'] == "vfat") or (tmp_partitions[partition]['type'] == "ntfs"):
					newliloconf += "other="+device+str(int(tmp_partitions[partition]['minor']))+"\n"
					newliloconf += "label=Windows_P"+str(int(tmp_partitions[partition]['minor']))+"\n\n"
		return newliloconf
