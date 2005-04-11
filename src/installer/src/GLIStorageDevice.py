import commands, string, re, os, parted
from decimal import Decimal

MEGABYTE = 1024 * 1024

archinfo = { 'sparc': { 'fixedparts': [ { 'minor': 3, 'type': "wholedisk" } ], 'disklabel': 'sun', 'extended': False },
             'hppa': { 'fixedparts': [ { 'minor': 1, 'type': "boot" } ], 'disklabel': 'msdos', 'extended': False },
             'x86': { 'fixedparts': [], 'disklabel': 'msdos', 'extended': True },
             'ppc': { 'fixedparts': [ { 'minor': 1, 'type': "metadata" } ], 'disklabel': 'mac', 'extended': False }
           }

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

	def set_disk_geometry_from_disk(self):
		self._total_bytes = self._parted_dev.length * self._parted_dev.sector_size
		self._geometry['heads'], self._geometry['sectors'], self._geometry['cylinders'] = self._parted_dev.heads, self._parted_dev.sectors, self._parted_dev.cylinders
		self._sector_bytes = self._parted_dev.sector_size
		self._cylinder_bytes = self._geometry['heads'] * self._geometry['sectors'] * self._sector_bytes
		self._total_sectors = self._parted_dev.length
		self._sectors_in_cylinder = self._geometry['heads'] * self._geometry['sectors']
		self._total_mb = int(self._total_bytes / MEGABYTE)

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
				self._partitions[int(parted_part.num)] = Partition(self, parted_part.num, part_mb, parted_part.geom.start, parted_part.geom.end, fs_type, format=False, existing=True)
			elif parted_part.type_name == "free":
				parent_part = self.get_partition_at(parted_part.geom.start, ignore_extended=0)
				if parent_part:
					self._partitions[Decimal(str(float(last_log_part+0.9)))] = Partition(self, Decimal(str(float(last_log_part+0.9))), part_mb, parted_part.geom.start, parted_part.geom.end, "free", format=False, existing=False)
					last_log_part += 1
				else:
					self._partitions[Decimal(str(float(last_log_part+0.1)))] = Partition(self, Decimal(str(float(last_log_part+0.1))), part_mb, parted_part.geom.start, parted_part.geom.end, "free", format=False, existing=False)
					last_part += 1
			parted_part = self._parted_disk.next_partition(parted_part)

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

	def get_device(self):
		return self._device

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
					if part_log < Decimal("4.9"): continue
					tmppart_log = self._partitions[part_log]
					if tmppart_log.get_type() == "free":
						if last_log_minor < last_log_free:
							self._partitions[last_log_free].set_mb(self._partitions[last_log_free].get_mb()+tmppart_log.get_mb())
							del self._partitions[part_log]
						else:
							if not last_log_free:
								last_log_free = Decimal(str(last_log_minor + 0.9))
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
						last_free = Decimal(str(last_minor + 0.1))
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

	def add_partition(self, free_minor, mb, start, end, type, mountpoint='', mountopts=''):
		free_minor = Decimal(str(free_minor))
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
				free_minor = Decimal(str(new_minor + 0.9))
			else:
				free_minor = Decimal(str(new_minor + 0.1))
			self._partitions[free_minor] = Partition(self, free_minor, old_free_mb-mb, 0, 0, "free")
#			print "add_partition(): new part doesn't use all freespace. new free part is: minor=" + str(free_minor)
		else:
			del self._partitions[free_minor]
		self._partitions[new_minor] = Partition(self, new_minor, mb, start, end, type, mountpoint=mountpoint, mountopts=mountopts)
		if type == "extended":
			self._partitions[Decimal("4.9")] = Partition(self, Decimal("4.9"), mb, 0, 0, "free")
		self.tidy_partitions()

	def remove_partition(self, minor):
		tmppart = self._partitions[int(minor)]
		free_minor = 0
		if tmppart.is_logical():
			free_minor = Decimal(str(float(minor)-0.1))
		else:
			free_minor = Decimal(str(float(minor)-0.9))
		self._partitions[free_minor] = Partition(self, free_minor, tmppart.get_mb(), 0, 0, "free", format=False, existing=False)
		del self._partitions[int(minor)]
		self.tidy_partitions()

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

	def get_partition_at(self, sector, ignore_extended=1):
		parts = self._partitions.keys()
		parts.sort()
		for part in parts:
			tmppart = self._partitions[part]
			if ignore_extended and tmppart.is_extended(): continue
			if (sector >= tmppart.get_start()) and (sector <= tmppart.get_end()):
				return part
		return 0

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

	def get_ordered_partition_list(self):
                parts = self._partitions.keys()
                parts.sort()
                partlist = []
		tmppart = None
		tmppart_log = None
		for part in parts:
			if archinfo[self._arch]['extended'] and part > Decimal("4.1"): break
			tmppart = self._partitions[part]
			partlist.append(part)
			if tmppart.is_extended():
				for part_log in parts:
					if part_log < Decimal("4.9"): continue
					tmppart_log = self._partitions[part_log]
					partlist.append(part_log)
		return partlist

	def get_install_profile_structure(self):
		devdic = {}
		for part in self._partitions:
			tmppart = self._partitions[part]
			devdic[part] = { 'mb': tmppart.get_mb(), 'minor': float(part), 'origminor': tmppart.get_orig_minor(), 'start': tmppart.get_start(), 'end': tmppart.get_end(), 'type': tmppart.get_type(), 'mountpoint': tmppart.get_mountpoint(), 'mountopts': tmppart.get_mountopts(), 'format': tmppart.get_format() }
		return devdic

	def get_extended_partition(self):
		for part in self._partitions:
			tmppart = self._partitions[part]
			if tmppart.is_extended():
				return part
		return 0

	def get_num_sectors(self):
		return int(self._total_sectors)

	def get_cylinder_size(self):
		return int(self._cylinder_bytes)

	def get_sector_size(self):
		return int(self._sector_bytes)

	def get_num_cylinders(self):
		return int(self._geometry['cylinders'])

	def get_drive_bytes(self):
		return int(self._total_bytes)

	def get_total_mb(self):
		return self._total_mb

	def get_partitions(self):
		return self._partitions

#	def print_partitions(self):
#		for part in self._partitions.keys():
#			print self._partitions[part].return_info()

	def print_geometry(self):
		print self._total_bytes, self._geometry

	def _error(self, message):
		"Raises an exception"
		raise "DeviceObjectError", message
		
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
	_min_sectors_for_resize = 0
	_mb = 0
	
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
				self._min_cylinders_for_resize = int(min_bytes / self._device._cylinder_bytes) + 1
				self._resizeable == True
			elif type == "ext2" or type == "ext3":
				block_size = string.strip(commands.getoutput("dumpe2fs -h " + dev_node + r" 2>&1 | grep -e '^Block size:' | sed -e 's/^Block size:\s\+//'"))
				free_blocks = string.strip(commands.getoutput("dumpe2fs -h " + dev_node + r" 2>&1 | grep -e '^Free blocks:' | sed -e 's/^Free blocks:\s\+//'"))
				free_sec = int(int(block_size) * int(free_blocks) / self._device._sector_bytes)
				free_sec = free_sec - 2000 # just to be safe
				self._min_sectors_for_resize = (self._end - self._start + 1) - free_sec
				self._resizeable == True
			else:
				parted_part = self._device._parted_disk.get_partition(int(self._minor))
				try:
					parted_fs = parted_part.geom.file_system_open()
				except:
					self._resizeable = False
					return
				resize_constraint = parted_fs.get_resize_constraint()
				min_size = resize_constraint.min_size
				if int(min_size) != min_size: min_size = int(min_size) + 1
				self._min_sectors_for_resize = min_size
				self._resizeable = True

	def is_extended(self):
		if self._type == "extended":
			return True
		else:
			return False

	def is_logical(self):
		if self._type == "free":
			if int(self._minor) + Decimal("0.9") == Decimal(str(self._minor)):
				return True
			else:
				return False
		elif archinfo[self._device._arch]['extended'] and self._minor > 4:
			return True
		else:
			return False

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

	def get_extended_parent(self):
		if not self.is_logical():
			return None
		else:
			return self._device.get_partition_at(self._start, ignore_extended=0)

	def set_start(self, start):
		self._start = int(start)
		self._blocks = ((self._end - self._start) * self._device.get_cylinder_size()) / 512

	def get_start(self):
		return int(self._start)

	def set_end(self, end):
		self._end = int(end)
		self._blocks = ((self._end - self._start) * self._device.get_cylinder_size()) / 512

	def get_end(self):
		return int(self._end)

	def get_mb(self):
		return int(self._mb)

	def set_mb(self, mb):
		self._mb = int(mb)

	def set_type(self, type):
		self._type = type

	def get_type(self):
		return self._type

	def get_device(self):
		return self._device

	def set_minor(self, minor):
		self._minor = float(minor)

	def get_minor(self):
		return float(self._minor)

	def set_orig_minor(self, orig_minor):
		self._orig_minor = int(orig_minor)

	def get_orig_minor(self):
		return self._orig_minor

	def set_mountpoint(self, mountpoint):
		self._mountpoint = mountpoint

	def get_mountpoint(self):
		return self._mountpoint

	def set_mountopts(self, mountopts):
		self._mountopts = mountopts

	def get_mountopts(self):
		return self._mountopts

	def set_format(self, format):
		self._format = format

	def get_format(self):
		return self._format

	def get_blocks(self):
		return int(self._blocks)

	def get_min_sectors_for_resize(self):
		if self.is_extended():
			min_size = self._start
			for part in self._device._partitions:
				if part < 5: continue
				if part.get_end > min_size: min_size = part.get_end()
			return min_size
		else:
			return self._min_sectors_for_resize

	def get_max_sectors_for_resize(self):
		free_start, free_end = self._device.get_free_space(self._end)
		if free_end == -1: return self._end
		if free_start - 1 == self._end:
			if self.is_logical():
				if free_end <= self._device._partitions[self.get_extended_parent()]._end:
					return free_end - self._start
				else:
					return self._end - self._start
			else:
				return free_end - self._start

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

	def _error(self, message):
		"Raises an exception"
		raise "PartitionObjectError", message
		

def detect_devices():
	"Returns a list of partitionable devices on the system"
	
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
