import commands, string, re, os, parted

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
	_fdiskcall = "fdisk -l "
	
	def __init__(self, device):
		self._device = device
		self._partitions = {}
		self._geometry = {'cylinders': 0, 'heads': 0, 'sectors': 0, 'sectorsize': 512}
		self._total_bytes = 0
		self._cylinder_bytes = 0
		self._parted_dev = parted.PedDevice.get(self._device)
		self._parted_disk = parted.PedDisk.new(self._parted_dev)
		self.set_disk_geometry_from_disk()

	def set_disk_geometry_from_disk(self):
		self._total_bytes = self._parted_dev.length * self._parted_dev.sector_size
		if string.strip(commands.getoutput("echo " + self._device + " | grep '/hd'")) == self._device: # IDE
			proc_dir = "/proc/ide/" + commands.getoutput("echo " + self._device + " | cut -d '/' -f 3")
			proc_dir = string.strip(proc_dir)
			heads = commands.getoutput("cat " + proc_dir + "/geometry | grep logical | cut -d '/' -f 2")
			sectors = commands.getoutput("cat " + proc_dir + "/geometry | grep logical | cut -d '/' -f 3")
			total_sectors = commands.getoutput("cat " + proc_dir + "/capacity")
			cylinders = int(total_sectors) / (int(heads) * int(sectors))
			self._geometry['heads'], self._geometry['sectors'], self._geometry['cylinders'] = int(heads), int(sectors), int(cylinders)
		else: #SCSI
			self._geometry['heads'], self._geometry['sectors'], self._geometry['cylinders'] = self._parted_dev.heads, self._parted_dev.sectors, self._parted_dev.cylinders
		self._cylinder_bytes = self._geometry['heads'] * self._geometry['sectors'] * self._parted_dev.sector_size
		self._total_sectors = self._geometry['cylinders'] * self._geometry['heads'] * self._geometry['sectors']
		self._sectors_in_cylinder = self._geometry['heads'] * self._geometry['sectors']

	def set_partitions_from_disk(self):
		parted_part = self._parted_disk.next_partition()
		while parted_part != None:
			if parted_part.num < 1:
				parted_part = self._parted_disk.next_partition(parted_part)
				continue
			fs_type = ""
			if parted_part.fs_type != None: fs_type = parted_part.fs_type.name
			if parted_part.type == 2: fs_type = "extended"
			self._partitions[int(parted_part.num)] = Partition(self, parted_part.num, '', (parted_part.geom.start / self._sectors_in_cylinder), (parted_part.geom.end / self._sectors_in_cylinder), (parted_part.geom.end - parted_part.geom.start), fs_type, format=False, existing=True)
			parted_part = self._parted_disk.next_partition(parted_part)

	def set_partitions_from_install_profile_structure(self, ips):
		for part in ips:
			tmppart = ips[part]
			existing = False
			parted_part = self._parted_disk.get_partition(part)
			if parted_part != None:
				start = parted_part.geom.start / self._sectors_in_cylinder
				end = parted_part.geom.end / self._sectors_in_cylinder
				fs_type = ""
				if parted_part.fs_type != None: fs_type = parted_part.fs_type.name
				if parted_part.type == 2: fs_type = "extended"
				if int(tmppart['start']) == int(start) and int(tmppart['end']) == int(end) and tmppart['type'] == fs_type and tmppart['format'] == False:
					existing = True
			self._partitions[int(part)] = Partition(self, part, '', tmppart['start'], tmppart['end'], 0, tmppart['type'], mountopts=tmppart['mountopts'], mountpoint=tmppart['mountpoint'], format=tmppart['format'], existing=(not tmppart['format']))

	def get_device(self):
		return self._device

	def clear_partitions(self):
		self._partitions = {}

	def add_partition(self, minor, start, end, type):
		free_start, free_end = self.get_free_space(start)
		minor = int(minor)
		if not free_end:
			return False
		if self._partitions.has_key(minor):
			parts = self._partitions.keys()
			parts.sort()
			parts.reverse()
			hole_at = 0
			for i in range(1, parts[0]+1):
				if i <= minor: continue
				if not self._partitions.has_key(int(i)):
					hole_at = i
					break
			stopscooting = 0
			for i in parts:
				if stopscooting: break
				if (i >= hole_at) and (hole_at): continue
				if i >= minor:
					self._partitions[i].set_minor(i+1)
					self._partitions[i+1] = self._partitions[i]
					if i == minor: stopscooting = 1
		self._partitions[minor] = Partition(self, minor, '', start, end, 0, type)

	def remove_partition(self, minor):
		del self._partitions[int(minor)]

	def get_free_space(self, start):
		parts = self._partitions.keys()
		parts.sort()
		lastend_pri = 0
		lastend_log = 0
		free_start = -1
		free_end = -1
		if start > self.get_num_cylinders(): return (-1, -1)
		for part in parts:
			if part > 4: break
			tmppart = self._partitions[part]
			if (tmppart.get_start() > lastend_pri) and (lastend_pri >= start):
				free_start = lastend_pri
				free_end = tmppart.get_start() - 1
				break
			if tmppart.is_extended() and start < tmppart.get_end():
				lastend_log = tmppart.get_start()
				for part_log in parts:
					if part_log < 5: continue
					tmppart_log = self._partitions[part_log]
					if (tmppart_log.get_start() > lastend_log) and (lastend_log >= start):
						free_start = lastend_log
						free_end = tmppart_log.get_start() - 1
						break
					lastend_log = tmppart_log.get_end() + 1
				if free_start == -1 and lastend_log < tmppart.get_end():
					free_start = lastend_log
					free_end = tmppart.get_end()
					break
			lastend_pri = tmppart.get_end() + 1
		if free_start == -1 and lastend_pri < self.get_num_cylinders():
			free_start = lastend_pri
			free_end = self.get_num_cylinders()
		return (free_start, free_end)

	def get_partition_at(self, cylinder, ignore_extended=1):
		parts = self._partitions.keys()
		parts.sort()
		for part in parts:
			tmppart = self._partitions[part]
			if ignore_extended and tmppart.is_extended(): continue
			if (cylinder >= tmppart.get_start()) and (cylinder <= tmppart.get_end()):
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
                free_start, free_end = self.get_free_space(0)
                tmppart = None
		tmppart_log = None
                for part in parts:
			if part > 4: break
			tmppart = self._partitions[part]
			if free_end < tmppart.get_start() and not free_start == -1:
				partlist.append("Free Space (" + str(free_start) + "-" + str(free_end) + ")")
				free_start, free_end = self.get_free_space(free_end)
			newitem = self._device + str(part) + ": " + str(tmppart.get_start()) + "-" + str(tmppart.get_end())
			if tmppart.is_extended(): newitem = newitem + " extended"
			partlist.append(newitem)
			if tmppart.is_extended():
				for part_log in parts:
					if part_log < 5: continue
					tmppart_log = self._partitions[part_log]
					if free_end < tmppart_log.get_start() and free_end <= tmppart.get_end() and not free_start == -1:
						partlist.append("Free Space (" + str(free_start) + "-" + str(free_end) + ")")
						free_start, free_end = self.get_free_space(free_end)
					newitem = self._device + str(part_log) + ": " + str(tmppart_log.get_start()) + "-" + str(tmppart_log.get_end()) + " logical"
					partlist.append(newitem)
				if ((tmppart_log == None) or (free_start > tmppart_log.get_end())) and free_start < tmppart.get_end():
					partlist.append("Free Space (" + str(free_start) + "-" + str(free_end) + ") logical")
					free_start, free_end = self.get_free_space(free_end)
		if (tmppart == None) or (free_start > tmppart.get_end()):
			partlist.append("Free Space (" + str(free_start) + "-" + str(free_end) + ")")
		return partlist

	def get_install_profile_structure(self):
		devdic = {}
		for part in self._partitions:
			tmppart = self._partitions[part]
			devdic[part] = { 'mb': 0, 'start': tmppart.get_start(), 'end': tmppart.get_end(), 'type': tmppart.get_type(), 'mountpoint': tmppart.get_mountpoint(), 'mountopts': tmppart.get_mountopts(), 'format': tmppart.get_format() }
		return devdic

	def get_num_sectors(self):
		return int(self._total_sectors)

	def get_cylinder_size(self):
		return int(self._cylinder_bytes)

	def get_num_cylinders(self):
		return int(self._geometry['cylinders'])

	def get_drive_bytes(self):
		return int(self._total_bytes)

	def get_partitions(self):
		return self._partitions

	def print_partitions(self):
		for part in self._partitions.keys():
			print self._partitions[part].return_info()

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
	_minor = None
	_bootflag = None
	_start = None
	_end = None
	_blocks = None
	_type = None
	_mountpoint = None
	_mountopts = None
	_format = None
	_resizeable = None
	_min_cylinders_for_resize = 0
	
	def __init__(self, device, minor, bootflag, start, end, blocks, type, mountpoint='', mountopts='', format=True, existing=False):
		self._device = device
		self._minor = int(minor)
		self._bootflag = bootflag
		self._start = int(start)
		self._end = int(end)
		self._blocks = int(blocks)
		self._type = type
		self._mountpoint = mountpoint
		self._mountopts = mountopts
		self._format = format
		if blocks == 0:
			self._blocks = ((self._end - self._start) * self._device.get_cylinder_size()) / 512
		if existing:
			parted_part = device._parted_disk.get_partition(minor)
			if type == "ntfs":
				min_bytes = int(commands.getoutput("ntfsresize --info " + device._device + str(minor) + " | grep -e '^You might resize' | sed -e 's/You might resize at //' -e 's/ bytes or .\+//'"))
				self._min_cylinders_for_resize = int(min_bytes / self._device._cylinder_bytes) + 1
				self._resizeable == True
			elif type == "ext2" or type == "ext3":
				commands.getstatus("mkdir /mnt/freespace; mount " + device._device + str(minor) + " /mnt/freespace")
				min_bytes = int(commands.getoutput("df -B kB " + device._device + str(minor) + " | tail -n 1 | sed -e 's:^" + device._device + str(minor) + "\s\+[0-9]\+kB\s\+::' -e 's:kB\s.\+::'")) * 1000
				commands.getstatus("umount /mnt/freespace; rm -rf /mnt/freespace")
				min_bytes = min_bytes + (100 * 1024 * 1024) # Add 100M just to be safe
				self._min_cylinders_for_resize = int(min_bytes / self._device._cylinder_bytes) + 1
				self._resizeable == True
			elif type == "fat16" or type == "fat32":
				parted_part = self._device._parted_disk.get_partition(self._minor)
				parted_fs = parted_part.geom.file_system_open()
				resize_constraint = parted_fs.get_resize_constraint()
				min_size = float(resize_constraint.min_size / self._device._sectors_in_cylinder)
				if int(min_size) != min_size: min_size = int(min_size) + 1
				self._min_cylinders_for_resize = min_size
				self._resizeable = True
			elif type == "":
				self._min_cylinders_for_resize = 1
				self._resizeable = True
		else:
			self._resizeable = True

	def is_extended(self):
		if self._type == "extended":
			return True
		else:
			return False

	def is_logical(self):
		part = self._device.get_partition_at(self._start, ignore_extended=0)
		if part and self._device._partitions[part].is_extended() and not part == self._minor:
			return True
		return False

	def get_logicals(self):
		logicals = []
		start = self._start
		while not start > self._end:
			part = self._device.get_partition_at(start)
			if not part: break
			logicals.append(part)
			start = self._device._partitions[part].get_end() + 1
		logicals.sort()
		return logicals

	def get_extended_parent(self):
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

	def set_type(self, type):
		self._type = type

	def get_type(self):
		return self._type

	def get_device(self):
		return self._device

	def set_minor(self, minor):
		self._minor = int(minor)

	def get_minor(self):
		return int(self._minor)

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

	def get_min_cylinders_for_resize(self):
#		min_size = self._start + 1
#		if not self._format:
#			parted_part = self._device._parted_disk.get_partition(self._minor)
#			parted_fs = parted_part.geom.file_system_open()
#			resize_constraint = parted_fs.get_resize_constraint()
#			min_size = float(resize_constraint.min_size / self._device._sectors_in_cylinder)
#			if int(min_size) != min_size: min_size = int(min_size) + 1
#		min_size = min_size + self._start
#################################################
		if self.is_extended():
			min_size = self._start
			for part in self._device._partitions:
				if part < 5: continue
				min_size = part.get_end()
		else:
			return self._min_cylinders_for_resize

	def get_max_cylinders_for_resize(self):
		free_start, free_end = self._device.get_free_space(self._end)
		if free_end == -1: return self._end
		if free_start - 1 == self._end:
			if self.is_logical():
				if free_end <= self._device._partitions[self.get_extended_parent()]._end:
					return free_end
				else:
					return self._end
			else:
				return free_end

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
