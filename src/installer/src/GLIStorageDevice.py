import commands, string, re, os, parted
#from decimal import Decimal

MEGABYTE = 1024 * 1024

archinfo = { 'sparc': { 'fixedparts': [ { 'minor': 3, 'type': "wholedisk" } ], 'disklabel': 'sun', 'extended': False },
             'hppa': { 'fixedparts': [ { 'minor': 1, 'type': "boot" } ], 'disklabel': 'msdos', 'extended': False },
             'x86': { 'fixedparts': [], 'disklabel': 'msdos', 'extended': True },
             'ppc': { 'fixedparts': [ { 'minor': 1, 'type': "metadata" } ], 'disklabel': 'mac', 'extended': False }
           }

##
# This class provides a partitioning abstraction for the frontends
class Device:
	"Class representing a partitionable device."
	
	_device = None
	_partitions = None
	_geometry = None
	_total_bytes = 0
	_total_sectors = 0
	_cylinder_bytes = 0
	_sectors_in_cylinder = 0
	_parted_dev = None
	_parted_disk = None
	_sector_bytes = 0
	_total_mb = 0
	_arch = None

	##
	# Initialization function for GLIStorageDevice class
	# @param device Device node (e.g. /dev/hda) of device being represented
	# @param arch="x86" Architecture that we're partition for (defaults to 'x86' for now)
	def __init__(self, device, arch="x86"):
		self._device = device
		self._partitions = {}
		self._geometry = {'cylinders': 0, 'heads': 0, 'sectors': 0, 'sectorsize': 512}
		self._total_bytes = 0
		self._cylinder_bytes = 0
		self._arch = arch
		self._parted_dev = parted.PedDevice.get(self._device)
		self._parted_disk = parted.PedDisk.new(self._parted_dev)
		self.set_disk_geometry_from_disk()

	##
	# Sets disk geometry info from disk. This function is used internally by __init__()
	def set_disk_geometry_from_disk(self):
		self._total_bytes = self._parted_dev.length * self._parted_dev.sector_size
		self._geometry['heads'], self._geometry['sectors'], self._geometry['cylinders'] = self._parted_dev.heads, self._parted_dev.sectors, self._parted_dev.cylinders
		self._sector_bytes = self._parted_dev.sector_size
		self._cylinder_bytes = self._geometry['heads'] * self._geometry['sectors'] * self._sector_bytes
		self._total_sectors = self._parted_dev.length
		self._sectors_in_cylinder = self._geometry['heads'] * self._geometry['sectors']
		self._total_mb = int(self._total_bytes / MEGABYTE)

	##
	# Sets partition info from disk.
	def set_partitions_from_disk(self):
		last_part = 0
		last_log_part = 4
		parted_part = self._parted_disk.next_partition()
		while parted_part:
			part_mb = int((parted_part.geom.end - parted_part.geom.start + 1) * self._sector_bytes / MEGABYTE)
			if parted_part.num >= 1:
				fs_type = ""
				if parted_part.fs_type != None: fs_type = parted_part.fs_type.name
				if parted_part.type == 2: fs_type = "extended"
				if archinfo[self._arch]['extended'] and parted_part.num > 4:
					last_log_part = parted_part.num
				else:
					last_part = parted_part.num
				self._partitions[int(parted_part.num)] = Partition(self, parted_part.num, part_mb, parted_part.geom.start, parted_part.geom.end, fs_type, format=False, existing=True)
			elif parted_part.type_name == "free":
				parent_part = self.get_partition_at(parted_part.geom.start, ignore_extended=0)
				if parent_part:
					self._partitions[last_log_part+0.9] = Partition(self, last_log_part+0.9, part_mb, parted_part.geom.start, parted_part.geom.end, "free", format=False, existing=False)
					last_log_part += 1
				else:
					self._partitions[last_part+0.1] = Partition(self, last_part+0.1, part_mb, parted_part.geom.start, parted_part.geom.end, "free", format=False, existing=False)
					last_part += 1
			parted_part = self._parted_disk.next_partition(parted_part)

	##
	# Imports partition info from the install profile partition structure (currently does nothing)
	# @param ips Parameter structure returned from install_profile.get_partition_tables()
	def set_partitions_from_install_profile_structure(self, ips):
		pass
#		for part in ips:
#			tmppart = ips[part]
#			existing = False
#			parted_part = self._parted_disk.get_partition(part)
#			if parted_part != None:
#				start = parted_part.geom.start / self._sectors_in_cylinder
#				end = parted_part.geom.end / self._sectors_in_cylinder
#				fs_type = ""
#				if parted_part.fs_type != None: fs_type = parted_part.fs_type.name
#				if parted_part.type == 2: fs_type = "extended"
#				if int(tmppart['start']) == int(start) and int(tmppart['end']) == int(end) and tmppart['type'] == fs_type and tmppart['format'] == False:
#					existing = True
#			self._partitions[int(part)] = Partition(self, part, '', tmppart['start'], tmppart['end'], 0, tmppart['type'], mountopts=tmppart['mountopts'], mountpoint=tmppart['mountpoint'], format=tmppart['format'], existing=(not tmppart['format']))

	##
	# Returns name of device (e.g. /dev/hda) being represented
	def get_device(self):
		return self._device

	##
	# Combines free space and closes gaps in minor numbers. This is used internally
	def tidy_partitions(self):
		last_minor = 0
		last_log_minor = 4
		last_free = 0
		last_log_free = 0
		parts = self._partitions.keys()
		parts.sort()
		for part in parts:
			if archinfo[self._arch]['extended'] and part > 4: break
			tmppart = self._partitions[part]
			if tmppart.get_type() == "extended":
				for part_log in parts:
					if part_log < 4.9: continue
					tmppart_log = self._partitions[part_log]
					if tmppart_log.get_type() == "free":
						if last_log_minor < last_log_free:
							self._partitions[last_log_free].set_mb(self._partitions[last_log_free].get_mb()+tmppart_log.get_mb())
							del self._partitions[part_log]
						else:
							if not last_log_free:
								last_log_free = last_log_minor + 0.9
							tmppart_log.set_minor(last_log_free)
							self._partitions[last_log_free] = tmppart_log
							if part_log != last_log_free: del self._partitions[part_log]
							continue
						last_log_free = part_log
					else:
						if part_log > (last_log_minor + 1):
							tmppart_log.set_minor(last_log_minor + 1)
							last_log_minor = last_log_minor + 1
							self._partitions[last_log_minor] = tmppart_log
							del self._partitions[part_log]
							continue
						last_log_minor = part_log
			if tmppart.get_type() == "free":
				if last_minor < last_free:
					self._partitions[last_free].set_mb(self._partitions[last_free].get_mb()+tmppart.get_mb())
					del self._partitions[part]
				else:
					if not last_free:
						last_free = last_minor + 0.1
					tmppart.set_minor(last_free)
					self._partitions[last_free] = tmppart
					if part != last_free: del self._partitions[part]
					continue
				last_free = part
			else:
				if part > (last_minor + 1):
					tmppart.set_minor(last_minor + 1)
					last_minor = last_minor + 1
					self._partitions[last_minor] = tmppart
					del self._partitions[part]
					continue
				last_minor = part

	##
	# Adds a new partition to the partition info
	# @param free_minor minor of unallocated space partition is being created in
	# @param mb size of partition in MB
	# @param start Start sector (only used for existing partitions)
	# @param end End sector (only used for existing partitions)
	# @param type Partition type (ext2, ext3, fat32, linux-swap, free, extended, etc.)
	# @param mountpoint='' Partition mountpoint
	# @param mountopts='' Partition mount options
	def add_partition(self, free_minor, mb, start, end, type, mountpoint='', mountopts=''):
		free_minor = free_minor
		new_minor = int(free_minor) + 1
#		print "add_partition(): free_minor=" + str(free_minor) + ", new_minor=" + str(new_minor)
		if self._partitions.has_key(new_minor):
			parts = self._partitions.keys()
			parts.sort()
			parts.reverse()
			hole_at = 0
			for i in range(1, parts[0]+1):
				if i <= new_minor: continue
				if not self._partitions.has_key(i):
					hole_at = i
					break
			stopscooting = 0
			for i in parts:
				if stopscooting: break
				if i >= hole_at and hole_at: continue
				if i >= new_minor:
					self._partitions[i].set_minor(i+1)
					self._partitions[i+1] = self._partitions[i]
					if i == new_minor: stopscooting = 1
		if mb != self._partitions[free_minor].get_mb():
			old_free_mb = self._partitions[free_minor].get_mb()
			del self._partitions[free_minor]
			if archinfo[self._arch]['extended'] and new_minor >= 5:
				free_minor = new_minor + 0.9
			else:
				free_minor = new_minor + 0.1
			self._partitions[free_minor] = Partition(self, free_minor, old_free_mb-mb, 0, 0, "free")
#			print "add_partition(): new part doesn't use all freespace. new free part is: minor=" + str(free_minor)
		else:
			del self._partitions[free_minor]
		self._partitions[new_minor] = Partition(self, new_minor, mb, start, end, type, mountpoint=mountpoint, mountopts=mountopts)
		if type == "extended":
			self._partitions[4.9] = Partition(self, 4.9, mb, 0, 0, "free")
		self.tidy_partitions()

	##
	# Removes partition from partition info
	# @param minor Minor of partition to remove
	def remove_partition(self, minor):
		tmppart = self._partitions[int(minor)]
		free_minor = 0
		if tmppart.is_logical():
			free_minor = minor-0.1
		else:
			free_minor = minor-0.9
		self._partitions[free_minor] = Partition(self, free_minor, tmppart.get_mb(), 0, 0, "free", format=False, existing=False)
		del self._partitions[int(minor)]
		self.tidy_partitions()

	##
	# Returns free space (no longer used)
	# @param start Start sector for search
	def get_free_space(self, start):
		GAP_SIZE = 100
		parts = self._partitions.keys()
		parts.sort()
		lastend_pri = 0
		lastend_log = 0
		free_start = -1
		free_end = -1
		if start > self._total_sectors: return (-1, -1)
		for part in parts:
			if part > 4: break
			tmppart = self._partitions[part]
			if (tmppart.get_start() > (lastend_pri + GAP_SIZE)) and (lastend_pri >= start):
				free_start = lastend_pri
				free_end = tmppart.get_start() - 1
				break
			if tmppart.is_extended() and start < tmppart.get_end():
				lastend_log = tmppart.get_start()
				for part_log in parts:
					if part_log < 5: continue
					tmppart_log = self._partitions[part_log]
					if (tmppart_log.get_start() > (lastend_log + GAP_SIZE)) and (lastend_log >= start):
						free_start = lastend_log
						free_end = tmppart_log.get_start() - 1
						break
					lastend_log = tmppart_log.get_end() + 1
				if free_start == -1 and lastend_log < tmppart.get_end():
					free_start = lastend_log
					free_end = tmppart.get_end()
					break
			lastend_pri = tmppart.get_end() + 1
		if free_start == -1 and lastend_pri < self._total_sectors:
			free_start = lastend_pri
			free_end = self._total_sectors
		return (free_start, free_end)

	##
	# Gets partition containing a certain sector (no longer used)
	# @param sector Sector to look at
	# @param ignore_extended=1 Ignore extended partitions
	def get_partition_at(self, sector, ignore_extended=1):
		parts = self._partitions.keys()
		parts.sort()
		for part in parts:
			tmppart = self._partitions[part]
			if ignore_extended and tmppart.is_extended(): continue
			if (sector >= tmppart.get_start()) and (sector <= tmppart.get_end()):
				return part
		return 0

	##
	# Returns free minor (no longer used)
	# @param start Parameter description
	# @param end Parameter description
	def get_free_minor_at(self, start, end):
                parts = self._partitions.keys()
                parts.sort()
		minor = 1
		lastpart = 0
                for part in parts:
                        if part > 4: break
                        tmppart = self._partitions[part]
			if end < tmppart.get_start():
				minor = part
				if (minor - 1) > lastpart: minor = lastpart + 1
				break
                        if tmppart.is_extended() and start < tmppart.get_end():
				minor = 5
				lastpart = 4
                                for part_log in parts:
                                        if part_log < 5: continue
                                        tmppart_log = self._partitions[part_log]
					if end < tmppart_log.get_start():
						minor = part_log
						if (minor - 1) > lastpart: minor = lastpart + 1
						break
					minor = part_log + 1
					lastpart = part_log
				break
			minor = part + 1
			lastpart = part
                return minor

	##
	# Returns an ordered list (disk order) of partition minors
	def get_ordered_partition_list(self):
                parts = self._partitions.keys()
                parts.sort()
                partlist = []
		tmppart = None
		for part in parts:
			if archinfo[self._arch]['extended'] and part > 4.1: break
			tmppart = self._partitions[part]
			partlist.append(part)
			if tmppart.is_extended():
				for part_log in parts:
					if part_log < 4.9: continue
					tmppart_log = self._partitions[part_log]
					partlist.append(part_log)
		return partlist

	##
	# Returns partition info in a format suitable for passing to install_profile.set_partition_tables()
	def get_install_profile_structure(self):
		devdic = {}
		for part in self._partitions:
			tmppart = self._partitions[part]
			devdic[part] = { 'mb': tmppart.get_mb(), 'minor': float(part), 'origminor': tmppart.get_orig_minor(), 'start': tmppart.get_start(), 'end': tmppart.get_end(), 'type': tmppart.get_type(), 'mountpoint': tmppart.get_mountpoint(), 'mountopts': tmppart.get_mountopts(), 'format': tmppart.get_format() }
		return devdic

	##
	# Returns the minor of the extended partition, if any
	def get_extended_partition(self):
		for part in self._partitions:
			tmppart = self._partitions[part]
			if tmppart.is_extended():
				return part
		return 0

	##
	# Returns the number of sectors on the device
	def get_num_sectors(self):
		return int(self._total_sectors)

	##
	# Returns the size of a cylinder in bytes
	def get_cylinder_size(self):
		return int(self._cylinder_bytes)

	##
	# Returns the size of a sector in bytes
	def get_sector_size(self):
		return int(self._sector_bytes)

	##
	# Returns the number of cylinders
	def get_num_cylinders(self):
		return int(self._geometry['cylinders'])

	##
	# Returns the total number of bytes on the device
	def get_drive_bytes(self):
		return int(self._total_bytes)

	##
	# Returns the total number of MB on the device
	def get_total_mb(self):
		return self._total_mb

	##
	# Returns partition info dictionary
	def get_partitions(self):
		return self._partitions

	##
	# Prints disk geometry to STDOUT (no longer used)
	def print_geometry(self):
		print self._total_bytes, self._geometry

	##
	# Utility function for raising an exception
	# @param message Error message
	def _error(self, message):
		"Raises an exception"
		raise "DeviceObjectError", message
		
	##
	# Utility function for running a command and returning it's output as a list
	# @param cmd Command to run
	def _run(self, cmd):
		"Runs a command and returns the output"
		
		# Run command
		output_string = commands.getoutput(cmd)
			
		# What we will return
		output_list = []
		
		# As long as there is a new line in the output_string
		while output_string.find("\n") != -1:
		
			# Find the \n in the string
			index = output_string.find("\n") + 1
			
			# Add the line to the output and remove it from 
			# the output_string
			output_list.append(output_string[:index])
			output_string = output_string[index:]
			
		# return output
		return output_list

##
# This class represents a partition within a GLIStorageDevice object
class Partition:
	"Class representing a single partition within a Device object"

	_device = None
	_minor = 0
	_orig_minor = 0
	_start = 0
	_end = 0
	_type = None
	_mountpoint = None
	_mountopts = None
	_format = None
	_resizeable = None
	_min_mb_for_resize = 0
	_mb = 0
	
	##
	# Initialization function for the Partition class
	# @param device Parent GLIStorageDevice object
	# @param minor Minor of partition
	# @param mb Parameter Size of partition in MB
	# @param start Parameter Start sector of partition
	# @param end Parameter Start sector of partition
	# @param type Parameter Type of partition (ext2, ext3, fat32, linux-swap, free, extended, etc.)
	# @param mountpoint='' Mountpoint of partition
	# @param mountopts='' Mount options of partition
	# @param format=True Format partition
	# @param existing=False This partition exists on disk
	def __init__(self, device, minor, mb, start, end, type, mountpoint='', mountopts='', format=True, existing=False):
		self._device = device
		self._minor = float(minor)
		if existing: self._orig_minor = int(minor)
		self._start = int(start)
		self._end = int(end)
		self._type = type or "unknown"
		self._mountpoint = mountpoint
		self._mountopts = mountopts
		self._format = format
		self._mb = mb
		if existing:
			self._orig_minor = self._minor
			parted_part = device._parted_disk.get_partition(minor)
			label_type = device._parted_disk.type.name
			if label_type == "loop":
				dev_node = device._device
			else:
				dev_node = device._device + str(minor)
			if type == "ntfs":
				min_bytes = int(commands.getoutput("ntfsresize -f --info " + dev_node + " | grep -e '^You might resize' | sed -e 's/You might resize at //' -e 's/ bytes or .\+//'"))
				self._min_mb_for_resize = int(min_bytes / MEGABYTE) + 1
				self._resizeable = True
			elif type == "ext2" or type == "ext3":
				block_size = int(string.strip(commands.getoutput("dumpe2fs -h " + dev_node + r" 2>&1 | grep -e '^Block size:' | sed -e 's/^Block size:\s\+//'")))
				free_blocks = int(string.strip(commands.getoutput("dumpe2fs -h " + dev_node + r" 2>&1 | grep -e '^Free blocks:' | sed -e 's/^Free blocks:\s\+//'")))
				free_bytes = int(block_size * free_blocks)
				# can't hurt to pad (the +50) it a bit since this is really just a guess
				self._min_mb_for_resize = self._mb - int(free_bytes / MEGABYTE) + 50
				self._resizeable = True
			else:
				parted_part = self._device._parted_disk.get_partition(int(self._minor))
				try:
					parted_fs = parted_part.geom.file_system_open()
				except:
					self._resizeable = False
					return
				resize_constraint = parted_fs.get_resize_constraint()
				min_bytes = resize_constraint.min_size * self._device._sector_bytes
				self._min_mb_for_resize = int(min_bytes / MEGABYTE) + 1
				self._resizeable = True

	##
	# Returns whether or not the partition is extended
	def is_extended(self):
		if self._type == "extended":
			return True
		else:
			return False

	##
	# Returns whether or not the partition is logical
	def is_logical(self):
		if self._type == "free":
			if int(self._minor) + 0.9 == self._minor:
				return True
			else:
				return False
		elif archinfo[self._device._arch]['extended'] and self._minor > 4:
			return True
		else:
			return False

	##
	# Returns a list of logical partitions if this is an extended partition
	def get_logicals(self):
		if not self.is_extended():
			return None
		logicals = []
		start = self._start
		parts = self._device._partitions.keys()
		parts.sort()
		for part in parts:
			if part < 5: continue
			logicals.append(part)
		logicals.sort()
		return logicals

	##
	# Returns the extened parent partition if this is a logical partition (no longer used)
	def get_extended_parent(self):
		if not self.is_logical():
			return None
		else:
			return self._device.get_partition_at(self._start, ignore_extended=0)

	##
	# Sets the start sector for the partition
	# @param start Start sector
	def set_start(self, start):
		self._start = int(start)

	##
	# Returns the start sector for the partition
	def get_start(self):
		return int(self._start)

	##
	# Sets the end sector of the partition
	# @param end End sector
	def set_end(self, end):
		self._end = int(end)

	##
	# Returns end sector for the partition
	def get_end(self):
		return int(self._end)

	##
	# Returns size of partition in MB
	def get_mb(self):
		return int(self._mb)

	##
	# Sets size of partition in MB
	# @param mb Parameter description
	def set_mb(self, mb):
		self._mb = int(mb)

	##
	# Sets type of partition
	# @param type Parameter description
	def set_type(self, type):
		self._type = type

	##
	# Returns type of partition
	def get_type(self):
		return self._type

	##
	# Returns parent GLIStorageDevice object
	def get_device(self):
		return self._device

	##
	# Sets minor of partition
	# @param minor New minor
	def set_minor(self, minor):
		self._minor = float(minor)

	##
	# Returns minor of partition
	def get_minor(self):
		return float(self._minor)

	##
	# Sets the original minor of the partition
	# @param orig_minor Parameter description
	def set_orig_minor(self, orig_minor):
		self._orig_minor = int(orig_minor)

	##
	# Returns the original minor of the partition
	def get_orig_minor(self):
		return self._orig_minor

	##
	# Sets the mountpoint for the partition
	# @param mountpoint Mountpoint
	def set_mountpoint(self, mountpoint):
		self._mountpoint = mountpoint

	##
	# Returns the mountpoint for the partition
	def get_mountpoint(self):
		return self._mountpoint

	##
	# Sets the mount options for the partition
	# @param mountopts Mount options
	def set_mountopts(self, mountopts):
		self._mountopts = mountopts

	##
	# Returns the mount options for the partition
	def get_mountopts(self):
		return self._mountopts

	##
	# Set whether to format the partition
	# @param format Format this partition (True/False)
	def set_format(self, format):
		self._format = format

	##
	# Returns whether to format the partition
	def get_format(self):
		return self._format

	##
	# Returns whether the partition is resizeable
	def is_resizeable(self):
		return self._resizeable

	##
	# Returns minimum MB for resize
	def get_min_mb_for_resize(self):
#		if self.is_extended():
#			min_size = self._start
#			for part in self._device._partitions:
#				if part < 5: continue
#				if part.get_end > min_size: min_size = part.get_end()
#			return min_size
#		else:
		if self._resizeable:
			return self._min_mb_for_resize
		else:
			return -1

	##
	# Returns maximum MB for resize
	def get_max_mb_for_resize(self):
		free_minor = 0
		if self.is_logical():
			free_minor = self._minor + 0.9
		else:
			free_minor = self._minor + 0.1
		if free_minor in self._device._partitions:
			return self._mb + self._device._partitions[free_minor]._mb
		else:
			return self._mb

	##
	# Resizes the partition (ignore)
	# @param start New start sector
	# @param end New end sector
	def resize(self, start, end):
		part_at_start = self._device.get_partition_at(int(start))
		part_at_end = self._device.get_partition_at(int(end))
		logicals = None
		if self.is_logical():
			parent = self.get_extended_parent()
			parentstart = int(self._device._partitions[parent].get_start())
			parentend = int(self._device._partitions[parent].get_end())
			if (start < parentstart) or (end > parentend): return 0
		if self.is_extended():
			logicals = self.get_logicals()
			if len(logicals):
				logicals_start = self._device._partitions[logicals[0]].get_start()
				logicals_end = self._device._partitions[logicals[len(logicals)-1]].get_end()
				if (start > logicals_start) or (end < logicals_end): return 0
			if part_at_start in logicals: part_at_start = 0
			if part_at_end in logicals: part_at_end = 0
		if ((not part_at_start == 0) and (part_at_start != self._minor)) or ((not part_at_end == 0) and (part_at_end != self._minor)):
			return 0
		self.set_start(start)
		self.set_end(end)
		return 1

	##
	# Utility function to raise an exception
	# @param message Error message
	def _error(self, message):
		raise "PartitionObjectError", message

##
# Returns a list of detected partitionable devices
def detect_devices():
	devices = []
	
	# Make sure sysfs exists
	if not os.path.exists("/sys/bus"):
		raise Exception, "no sysfs found (you MUST use a kernel >2.6)"
	# Make sure /proc/partitions exists
	if not os.path.exists("/proc/partitions"):
		raise Exception, "/proc/partitions does not exist!"
	
	# Load /proc/partitions into the variable 'partitions'
	partitions = []
	for line in open("/proc/partitions"):
		if len(line.split()) < 4 or not line.split()[0].isdigit() or \
						not line.split()[1].isdigit():
			continue
		
		# Get the major, minor and device name
		major = line.split()[0]
		minor = line.split()[1]
		device = "/dev/" + line.split()[3]
		
		if not major.isdigit() or not minor.isdigit():
			continue
			
		major = int(major)
		minor = int(minor)

		# If there is no /dev/'device_name', then scan
		# all the devices in /dev to try and find a
		# devices with the same major and minor		
		if not os.path.exists(device):
			device = None
			for path, dirs, files in os.walk("/dev"):
				for file in files:
					full_file = os.path.join(path, file)
					if not os.path.exists(full_file):
						continue
					statres = os.stat(full_file)
					fmaj = os.major(statres.st_rdev)
					fmin = os.minor(statres.st_rdev)
					if fmaj == major and fmin == minor:
						device = full_file
						break
			if not device:
				continue
			
		partitions.append(( major, minor, device ))
	
	# Scan sysfs for the devices of type 'x'
	# 'x' being a member of the list below:
	for dev_type in [ "ide", "scsi" ]:	# Other device types? usb? fw?
		if os.path.exists("/sys/bus/" + dev_type):
			sysfs_devices = os.listdir("/sys/bus/"+dev_type+"/devices")
			
			# For each device in the devices on that bus
			for sysfs_device in sysfs_devices:
				dev_file = "/sys/bus/" + dev_type + "/devices/"\
						+ sysfs_device + "/block/dev"
						
				# If the file is not a block device, loop
				if not os.path.exists(dev_file):
					continue
					
				# Get the major and minor info
				try:
					major, minor = open(dev_file).read().split(":")
					major = int(major)
					minor = int(minor)
				except:
					raise Exception, "invalid major minor in "\
								+ dev_file
			
				# Find a device listed in /proc/partitions
				# that has the same minor and major as our
				# current block device.
				for record in partitions:
					if major == record[0] and minor == record[1]:
						devices.append(record[2])
	
	# We have assembled the list of devices, so return it
	return devices
