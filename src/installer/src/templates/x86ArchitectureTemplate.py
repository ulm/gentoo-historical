"""
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
Gentoo Linux Installer

$Id: x86ArchitectureTemplate.py,v 1.110 2006/03/06 21:37:06 agaffney Exp $
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

		self.notify_frontend("progress", (0, "Examining partitioning data"))
		total_steps = float(len(parts_new) * 3)
		cur_progress = 0
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

			self._logger.log("partitioning: Processing " + device + "...")

			# Create pyparted objects for this device
			parted_dev = parted.PedDevice.get(device)
			try:
				parted_disk = parted.PedDisk.new(parted_dev)
			except:
				parted_disk = parted_dev.disk_new_fresh(parted.disk_type_get((tmp_parts_new[device].get_disklabel() or GLIStorageDevice.archinfo[self._architecture_name]['disklabel'])))
#			new_part_list = parts_new[device].keys()
#			new_part_list.sort()
			new_part_list = tmp_parts_new[device].get_ordered_partition_list()
			device_sectors = parted_dev.length

			# Iterate through new partitions and check for 'origminor' and 'format' == False
			for part in new_part_list:
				tmppart_new = parts_new[device][part]
				if not tmppart_new['origminor'] or tmppart_new['format']: continue
				tmppart_old = parts_old[device][tmppart_new['origminor']]
				parted_part = parted_disk.get_partition(tmppart_new['origminor'])
				# This partition in parts_new corresponds with an existing partitions, so we save the start/end sector and flags
				for flag in range(0, 10):
					# The 10 is completely arbitrary. If flags seem to be missed, this number should be increased
					if not parted_part: break
					if parted_part.is_flag_available(flag) and parted_part.get_flag(flag):
						if not "flags" in tmppart_new: tmppart_new['flags'] = []
						tmppart_new['flags'].append(flag)
				if tmppart_new['resized']:
					self._logger.log("  Partition " + str(part) + " has origminor " + str(tmppart_new['origminor']) + " and it being resized...saving start sector " + str(parted_part.geom.start))
					tmppart_new['start'] = parted_part.geom.start
					tmppart_new['end'] = 0
				else:
					self._logger.log("  Partition " + str(part) + " has origminor " + str(tmppart_new['origminor']) + "...saving start sector " + str(parted_part.geom.start) + " and end sector " + str(parted_part.geom.end))
					tmppart_new['start'] = parted_part.geom.start
					tmppart_new['end'] = parted_part.geom.end

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
			self.notify_frontend("progress", (cur_progress / total_steps, "Deleting partitioning that aren't being resized for " + device))
			cur_progress += 1
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
							if tmppart['origminor'] == part_log and not tmppart['resized']:
								self._logger.log("  Deleting old minor " + str(part_log) + " to be recreated later")
								try:
									parted_disk.delete_partition(parted_disk.get_partition(part_log))
								except:
									self._logger.log("    Could not delete partition...ignoring")
								break
							# This partition is resized with the data preserved in the new layout
							if tmppart['origminor'] == part_log and tmppart['resized']:
								self._logger.log("  Ignoring old minor " + str(part_log) + " to resize later")
								logical_to_resize = 1
								break
					if not logical_to_resize:
						self._logger.log("  Deleting extended partition with minor " + str(part))
						parted_disk.delete_partition(parted_disk.get_partition(part))
					continue
				for new_part in parts_new[device]:
					tmppart = parts_new[device][new_part]
					if tmppart['origminor'] == part and not tmppart['resized']:
						self._logger.log("  Deleting old minor " + str(part) + " to be recreated later")
						try:
							parted_disk.delete_partition(parted_disk.get_partition(part))
						except:
							self._logger.log("    Could not delete partition...ignoring")
						break
					if tmppart['origminor'] == part and tmppart['resized']:
						self._logger.log("  Ignoring old minor " + str(part) + " to resize later")
						break
			parted_disk.commit()

			# Second pass to resize old partitions that need to be resized
			self._logger.log("Partitioning: Second pass...")
			self.notify_frontend("progress", (cur_progress / total_steps, "Resizing remaining partitions for " + device))
			cur_progress += 1
			for part in parts_old[device]:
				oldpart = parts_old[device][part]
				for new_part in parts_new[device]:
					tmppart = parts_new[device][new_part]
					if tmppart['origminor'] == part and tmppart['resized'] and tmppart['start'] and not tmppart['end']:
						self._logger.log("  Resizing old minor " + str(part) + " from " + str(oldpart['start']) + "-" + str(oldpart['end'])+  " to " + str(tmppart['start']) + "-" + str(tmppart['end']))
						type = tmppart['type']
						minor = part
						start = tmppart['start']
						# Replace 512 with code to retrieve bytes per sector for device
						end = start + (long(tmppart['mb']) * MEGABYTE / 512)
						tmppart['end'] = end
						for i in new_part_list:
							if i <= new_part: continue
							if parts_new[device][i]['start'] and end >= parts_new[device][i]['start']:
								end = parts_new[device][i]['start'] - 1
							elif end >= device_sectors:
								end = device_sectors - 1
							break
						if type == "ext2" or type == "ext3":
							total_sectors = end - start + 1
							ret = GLIUtility.spawn("resize2fs " + device + str(minor) + " " + str(total_sectors) + "s", logfile=self._compile_logfile, append_log=True)
							if not GLIUtility.exitsuccess(ret): # Resize error
								raise GLIException("PartitionResizeError", 'fatal', 'partition', "could not resize " + device + str(minor))
						elif type == "ntfs":
							total_sectors = end - start + 1
							total_bytes = long(total_sectors) * 512
							ret = GLIUtility.spawn("ntfsresize --size " + str(total_bytes) + " " + device + str(minor), logfile=self._compile_logfile, append_log=True)
							if not GLIUtility.exitsuccess(ret): # Resize error
								raise GLIException("PartitionResizeError", 'fatal', 'partition', "could not resize " + device + str(minor))
						elif type == "linux-swap" or type == "fat32" or type == "fat16":
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
			self.notify_frontend("progress", (cur_progress / total_steps, "Recreating partition table for " + device))
			cur_progress += 1
			start = 0
			end = 0
			extended_start = 0
			extended_end = 0
			self._logger.log("  Drive has " + str(device_sectors) + " sectors")
#			for part in parts_new[device]:
			for part in new_part_list:
				newpart = parts_new[device][part]
				self._logger.log("  Partition " + str(part) + " has " + str(newpart['mb']) + "MB")
				if newpart['start']:
					self._logger.log("    Old start sector " + str(newpart['start']) + " retrieved")
					if start != newpart['start']:
						self._logger.log("    Retrieved start sector is not the same as the calculated next start sector")
					start = newpart['start']
				else:
					self._logger.log("    Start sector calculated to be " + str(start))
				if (newpart['minor'] < 5 or not GLIStorageDevice.archinfo['x86']['extended']) and start < extended_end:
					self._logger.log("    Start sector for primary is less than the end sector for previous extended")
					start = extended_end + 1
				if newpart['end']:
					self._logger.log("    Old end sector " + str(newpart['end']) + " retrieved")
					end = newpart['end']
					part_sectors = end - start + 1
				else:
					part_sectors = long(newpart['mb']) * MEGABYTE / 512
					end = start + part_sectors
					self._logger.log("    End sector calculated to be " + str(end))
				# Make sure end doesn't overlap next partition's existing start sector
				for i in new_part_list:
					if i <= part: continue
					if parts_new[device][i]['start'] and end >= parts_new[device][i]['start']:
						if not newpart['type'] == "extended" or i <= 4:
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
							parted_disk.get_partition(part).set_flag(flag, True)
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
					elif newpart['type'] == 'fat16':
						cmdname = 'mkfs.vfat -F 16'
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
#					while not GLIUtility.is_file(devnode):
#						self._logger.log("Waiting for device node "+devnode+" to exist...")
#						time.sleep(1)
					# one bit of extra sleep is needed, as there is a blip still
#					time.sleep(1)

					tries = 0
					while tries <= 10:
						# now the actual command
						cmd = "%s %s %s" % (cmdname,newpart['mkfsopts'],devnode)
						self._logger.log("  Formatting partition %s as %s with: %s" % (str(part),newpart['type'],cmd))
						# If logging is not done, then you get errors:
						# PartitionFormatError :FATAL: partition: could't create ext2 filesystem on /dev/hda1
						#if GLIUtility.spawn(cmd):
						#if GLIUtility.spawn(cmd,append_log=True,logfile='/var/log/install-mkfs.log'):
						ret = GLIUtility.spawn(cmd, logfile=self._compile_logfile, append_log=True)
						if not GLIUtility.exitsuccess(ret):
							tries += 1
							self._logger.log("Try %d failed formatting partition %s...waiting 5 seconds" % (tries, devnode))
							time.sleep(5)
						else:
							break
					if tries == 3:
						raise GLIException("PartitionFormatError", 'fatal', 'partition', errormsg)
				start = end + 1
			self.notify_frontend("progress", (cur_progress / total_steps, "Done with partitioning for " + device))
#			cur_progress += 1

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
			tmp_partitions = parts[device].get_install_profile_structure()
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
			tmp_partitions = parts[device].get_install_profile_structure()
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
			tmp_partitions = parts[device].get_install_profile_structure()
			for partition in tmp_partitions:
				if (tmp_partitions[partition]['type'] == "vfat") or (tmp_partitions[partition]['type'] == "ntfs"):
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
