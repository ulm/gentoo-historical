"""
This is the partition tools layer that will eventually be a part of a 
non GLI partitioning python module.  However, we'll use it here temporarily 
until that module is complete.
"""

import commands

# Define the following (for checking later)
PyPartedDevice, PartedDevice, FdiskDevice = None, None, None

# Only load the PyPartedDevice class if pyparted is available
try:
	# Get the pyparted module
	import parted
	class PyPartedDevice:
		"""Class defining an object representing a Device(Disk).  
		Uses pyparted (libparted python bindings) as an interface."""

		# Where to log errors if any
		_logger = None

		# device string
		_device = None

		# Method for exceptions
		_exception_handler = None
		
		_FLAGS_BY_FLAG = { "boot" : 1, "root" : 2, "swap" : 3, 
				"hidden": 4, "raid": 5, "lvm": 6, "lba": 7 }
		_FLAGS_BY_NUM = { 1: "boot", 2: "root",  3: "swap", 
				4: "hidden", 5: "raid", 6: "lvm", 7: "lba" }

		def __init__(self, device, logger=None):

			# Set the logfile
			self._logger = logger

			# Get the device string
			self._device = device

			# Define the method to be used upon an error
			self._exception_handler = self._exceptions

		def _exceptions(self, ped_exception):
			"Handles pyparted exceptions"

			# Only log if a logger is defined
			if self._logger:
				# Log the error
				self._logger.log(ped_exception.type_string + \
						": " + ped_exception.message)

			# If there is no logger, then just print the info
			else:
				print ped_exception.type_string + ": " + \
							ped_exception.message

			# Don't actually handle the exception		
			return parted.EXCEPTION_UNHANDLED
			
		def _start_pyparted(self):
			"Initializes pyparted, returning a device object"

			# Register the event handler
			parted.exception_set_handler(self._exception_handler)
			
			# Get device object
			device = parted.PedDevice.get(self._device)
			
			# Make sure device is not busy
			if device.is_busy():
				raise "PyPartedDeviceError", "Device is busy! \
							 Cannot continue!"
				
			# Return the device object
			return device
			
		def get_partition_minors(self):
			"Returns a tuple of the minors of all the partitions on the drive"
			
			# Get the disk object
			disk = parted.PedDisk.new(self._start_pyparted())
			
			# Set the list of partitions to null
			partitions = []
			
			# Scan the partitions on the disk
			last_part_num = disk.get_last_partition_num()
			for i in range(1,last_part_num + 1):
				try:
					partition = disk.get_partition(i)
					if partition.type in [ 
							parted.PARTITION_PRIMARY, 
							parted.PARTITION_LOGICAL,
							parted.PARTITION_EXTENDED ]:
						partitions.append(i)
				except:
					pass
					
			return tuple(partitions)
			
		def get_device_sector_size(self):
			"Returns the size of sectors on the device in bytes"
			
			return self._start_pyparted().sector_size
			
		def get_partition_naming_support(self):
			"Returns whether or not the current partition label supports naming (bool)"
			
			# Get the disk object
			disk = parted.PedDisk.new(self._start_pyparted())			
			
			# Return True if the partition labels supports 
			# partition naming, false if not
			if disk.type.check_feature(parted.DISK_TYPE_PARTITION_NAME):
				return True
			else:
				return False
				
		def get_device_size(self):
			"Returns the size of a disk in sectors"
			
			return self._start_pyparted().length
			
		def get_device_model(self):
			"Returns the model of the device (an embeded string in the device)"
			
			return self._start_pyparted().model
			
		def get_partition_label_type(self):
			"Returns a string representing the partition label type"
			
			# Get the disk object
			return parted.PedDisk.new(self._start_pyparted()).type.name
			
		def get_partition_info(self, minor):
			"""
			Returns partition table info from partition 'minor'.  
			Returns None if partition doesn't exist.
			If the output is NOT None, the partition exists.
			Output is in the format ( <start>, <end>, <filesystem>, <flags (tuple)>, <part_min_resize> )
			If no flags are set, 'flags' will be an empty tuple.
			If the partition cannot be resized, part_min_resize will be None.
			"""
			
			# Get the disk object
			disk = parted.PedDisk.new(self._start_pyparted())

			try:
				partition = disk.get_partition(minor)

				# If this is a real partition (not a parted virtual partition)
				if not partition.type in [ 
							parted.PARTITION_PRIMARY, 
							parted.PARTITION_LOGICAL,
							parted.PARTITION_EXTENDED ]:
					return None
				
				# Get start, end and filesystem type
				part_start = partition.geom.start
				part_end = partition.geom.end
				
				# If we are dealing with an extended partition
				if partition.type == parted.PARTITION_EXTENDED:
					part_fs = "extended"
				else:
					part_fs = partition.fs_type.name

				# Get which flags are active on the partition
				part_flags = []
				for i in self._FLAGS_BY_NUM.keys():
					if partition.get_flag(i):
						part_flags.append(self._FLAGS_BY_NUM[i])
				
				# We aren't going to allow resizing extended partitions
				if partition.type == parted.PARTITION_EXTENDED:
					part_min_resize = None
					
				# If the partition is not extended, 
				# lets get the minimum resize size
				else:
					# Try to get the size, if we can't, 
					# then we can't resize the partition
					try:
						fs = partition.geom.file_system_open()
						part_min_resize = \
							fs.get_resize_constraint().min_size
					except:
						part_min_resize = None
			except:
				return None
			
			return ( part_start, part_end, part_fs, 
					tuple(part_flags), part_min_resize )
			
		def grow_partition(self, minor, new_end=None):
			"""Grows partition to specified new end point.
			If new_end is not specified, it will maximize the partition."""
			
			# Get the disk object
			disk = parted.PedDisk.new(self._start_pyparted())

			try:
				minor = int(minor)
			except:
				raise "PyPartedDeviceError", "Minor must be an integer!"
		
			try:
				partition = disk.get_partition(minor)
			except:
				raise "PyPartedDeviceError", "Minor does not exist!"
				
			# Get the next minor up (if it exists)
			next_part_minor = None
			for i in self.get_partition_minors():
				if i > minor:
					if next_part_minor == None:
						next_part_minor = i
					elif i < next_part_minor:
						next_part_minor = i
			
			# If a minor exists after the current minor...
			if next_part_minor:
				next_partition = disk.get_partition(next_part_minor)
				max_end = next_partition.geom.end - 1
			else:
				max_end = self.get_device_size() - 1	

			# If we are going to maximize the partition
			if not new_end:
				new_end = max_end
			
			# Make sure we are growing
			elif new_end < partition.geom.end:
				raise "PyPartedDevice", "You wanted to grow the \
				partition, but the specified new_end is smaller \
				than the current end!"
			
			# If the new end is bigger than the maximum possible end
			elif new_end > max_end:
			
				# Find out if the difference is negligable
				if abs(max_end - new_end) > ( 8192 * \
						self.get_device_sector_size()):
					raise "PyPartedDevice", "Specified size is too large!"
				else:
					new_end = max_end
						
			# Resize the partition
			partition.geom.set_end(new_end)
			if not disk.commit():
				raise "PyPartedDevice", "Resizing partition failed!"
			
		def shrink_partition(self, minor, new_end=None):
			"""
			Shrinks partition to the specified new endpoint.  
			If new_end is not specified, it will shrink down to the 
			size of the filesystem.
			WARNING: For unsupported filesystem types (ie. ntfs), 
			new_end MUST be specified!
			"""
			
			# Get the disk object
			disk = parted.PedDisk.new(self._start_pyparted())

			try:
				minor = int(minor)
			except:
				raise "PyPartedDeviceError", "Minor must be an integer!"
		
			try:
				partition = disk.get_partition(minor)
			except:
				raise "PyPartedDeviceError", "Minor does not exist!"
				
			# If we are going to minimize the partition
			if not new_end:
			
				try:
					fs = partition.geom.file_system_open()
				except:
					raise "PyPartedDeviceError", "pyparted \
					does not support the filesystem on minor "\
					 + str(minor)
					
				new_end = fs.geom.end
			
			# Make sure we are shrinking
			elif new_end > partition.geom.end:
				raise "PyPartedDevice", "You wanted to shrink \
				the partition, but the specified new_end is \
				bigger than the current end!"
			
			# Resize the partition
			partition.geom.set_end(new_end)
			if not disk.commit():
				raise "PyPartedDevice", "Resizing partition failed!"


		def grow_filesystem(self, minor):
			"Expands filesystem on 'minor' to the size of the partition."
		
			# Get the disk object
			disk = parted.PedDisk.new(self._start_pyparted())

			try:
				minor = int(minor)
			except:
				raise "PyPartedDeviceError", "Minor must be an integer!"
		
			try:
				partition = disk.get_partition(minor)
			except:
				raise "PyPartedDeviceError", "Minor does not exist!"
				
			try:
				fs = partition.geom.file_system_open()
				new_geom = fs.geom.duplicate()
			except:
				raise "PyPartedDeviceError", "pyparted does not \
				support the filesystem on minor " + str(minor)
				
			# Get the new size, and resize
			new_geom.set_end(partition.geom.end - 1)
			if not fs.resize(new_geom):
				raise "PyPartedDeviceError", "pyparted failed \
				while resizing the filesystem on partition minor"\
				+ str(minor)
		
		def shrink_filesystem(self, minor, new_end=None):
			"""
			Shrinks filesystem on 'minor' to specifiec new end.  
			If no new_end is specified, 
			it shrinks the fs to the minimum possible size.
			"""		
		
			# Get the disk object
			disk = parted.PedDisk.new(self._start_pyparted())

			try:
				minor = int(minor)
			except:
				raise "PyPartedDeviceError", "Minor must be an integer!"
		
			try:
				partition = disk.get_partition(minor)
			except:
				raise "PyPartedDeviceError", "Minor does not exist!"
				
			try:
				fs = partition.geom.file_system_open()
				new_geom = fs.geom.duplicate()
			except:
				raise "PyPartedDeviceError", "pyparted does not\
				 support the filesystem on minor " + str(minor)
				
			min_end = (fs.geom.start + \
					fs.get_resize_constraint().min_size)
				
			# If we are going to minimize the filesystem
			if not new_end:
				new_geom.set_end(min_end)
			elif new_end > fs.geom.end:
				raise "PyPartedDevice", "You wanted to shrink \
				the filesystem, but the specified new_end is \
				bigger than the current end!"
				
			# If the specified new_end is smaller than the minimum resize
			elif new_end < min_end:

				# Find out if the difference is negligable
				if abs(min_end - new_end) > ( 8192 * \
						self.get_device_sector_size()):
					raise "PyPartedDevice", "Specified size is too small!"
				else:
					new_geom.set_end(min_end)
					
			# If new_end passes all our sanity checks
			else:
				new_geom.set_end(new_end)
				
			# Resize
			if not fs.resize(new_geom):
				raise "PyPartedDeviceError", "pyparted failed \
				while resizing the filesystem on partition minor"\
				+ str(minor)

		def remove_partition(self, minor):
		
			# Get the disk object
			disk = parted.PedDisk.new(self._start_pyparted())

			try:
				minor = int(minor)
			except:
				raise "PyPartedDeviceError", "Minor must be an integer!"
				
			try:
				partition = disk.get_partition(minor)
			except:
				raise "PyPartedDeviceError", "Minor does not exist!"
				
			if not disk.delete_partition(partition):
				raise "PyPartedDeviceError", "Failure while removing the partition!"
				
		def add_partition(self, start, end, part_type, fs_type):
			"""
			Adds a partition to the partition table.  
			Partition type is one of: primary, extended, logical.  
			Filesystem type is in: ext2, ext3, fat16, fat32, linux-swap,
			hfs, hfs+, jfs, ntfs, reiserfs, hp-ufs, sun-ufs, xfs.
			NOTE: This does NOT create filesystems, however, it 
			DOES set the partition ID appropriately.
			"""
			
			

except:
	raise "ToolDefineError", "Unable to load pyparted interface and fdisk/parted not implimented yet"


#class PartedDevice:
#	"""Class defining an object representing a Device(Disk).  
#	Uses parted as an interface."""
#	pass


#class FdiskDevice:
#	"""Class defining an object representing a Device(Disk).  
#	Uses fdisk as an interface."""
#	pass
	
	
	

class NTFSFilesystem:
	"Class defining an object representing a NTFS Filesystem"
	
	_device = None
	_minor = None
	_logger = None
	_sector_size = 512
	
	def __init__(self, device, minor, sector_size=512, logger=None):
		self._device = device
		self._minor = minor
		self._logger = logger
		self._sector_size = sector_size
		
	def _error(self, message):
		"Raises an exception"
		raise "NTFSFilesystemError", message
		
	def _run(self, cmd):
		"Runs a command and returns the output"
		
		# Run command
		status, output_string = commands.getstatusoutput(cmd)
		if status:
			self._error("Error running command '" + cmd + "'!")
			
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
			
		# If a logger is defined, the log to the logger
		if self._logger:
			self._logger.log(output_list)
		# Otherwise, just print output
		else:
			for line in output_list:
				if len(line) > 0 and line[-1] == "\n":
					line = line[:-1]
				print line
			
		# return output
		return output_list
		
	def _run_ntfsresize(self, size=None, dry_run=True):
		"""Runs ntfsresize.  If size is not set, it will just get info.  
		If size is set, it will resize."""
		
		# If size is not defined, then just get info
		if not size:
			cmd = "ntfsresize -P -f -i " + self._device + \
								str(self._minor)
			
		# If the size is defined as "max" then maximize filesystem
		elif size == "max":
			if dry_run:
				cmd = "ntfsresize -P -n " + self._device + \
								str(self._minor)
			else:
				cmd = "ntfsresize -P " + self._device + \
								str(self._minor)
		
		# Otherwise, size to the size specified
		else:
			if dry_run:
				cmd = "ntfsresize -P -n -s " + str(size) + " " + \
						self._device + str(self._minor)
			else:
				cmd = "ntfsresize -P -s " + str(size) + " " + \
						self._device + str(self._minor)
		
		return self._run(cmd)

	
	def get_min_resize(self):
		"Returns the minimum size of the partition in sectors"
		
		output = self._run_ntfsresize()

		# Default to None
		min_resize = None
		
		# Get the min_resize size
		for line in output:
			if line[:19] == "You might resize at":
				min_resize = long(line.split()[4]) / self._sector_size
				
		return min_resize
		
	def resize(self, size):
		"Resizes minor to the specified size in sectors"
		
		# Make sure size is correct
		if type(size) != int and type(size) != long and size != "max":
			self._error("size must be an integer/log or 'max'!")
			
		# Convert size to bytes from sectors
		if type(size) == int or type(size) == long:
			size = size * self._sector_size
			
		# Run the command
		output = self._run_ntfsresize(size)
		
	def format(self):
		"Creates a NTFS filesystem on the minor specified"

		# Make the command string
		cmd = "mkntfs " + self._device + str(self._minor)
		
		# Run it
		output = self._run(cmd)

class Ext2Filesystem:
	"Class defining an object representing an Ext2/3 Filesystem"
	
	def __init__(self, device, minor, sector_size=512, logger=None):
		self._device = device
		self._minor = minor
		self._logger = logger
		self._sector_size = sector_size	

	def _error(self, message):
		"Raises an exception"
		raise "Ext2FilesystemError", message
		
	def _run(self, cmd):
		"Runs a command and returns the output"
		
		# Run command
		status, output_string = commands.getstatusoutput(cmd)
		if status:
			self._error("Error running command '" + cmd + "'!")
			
		# What we will return
		output_list = []
		
		# As long as there is a new line in the output_string
		while output_string.find("\n") != -1:
		
			# Find the \n in the string
			index = output_string.find("\n") + 1
			
			# Add the line to the output and remove it 
			# from the output_string
			output_list.append(output_string[:index])
			output_string = output_string[index:]
			
		# If a logger is defined, the log to the logger
		if self._logger:
			self._logger.log(output_list)
		# Otherwise, just print output
		else:
			for line in output_list:
				if len(line) > 0 and line[-1] == "\n":
					line = line[:-1]
				print line
			
		# return output
		return output_list
		
	def get_min_resize(self):
		"Returns the minimum size of the partition in sectors"
		
		# We don't know the actual resize size
		return long(10)
				
	def resize(self, size):
		"Resizes minor to the specified size in sectors"
		
		# Make sure size is correct
		if type(size) != int and type(size) != long and size != "max":
			self._error("size must be an integer/log or 'max'!")
			
		# If the size is defined as "max" then maximize filesystem
		if size == "max":
			cmd = "resize2fs " + self._device + str(self._minor)
		
		# Otherwise, size to the size specified
		else:
			cmd = "resize2fs " + self._device + str(self._minor) + \
							" " + str(size) + "s"
		
		output = self._run(cmd)

	def format(self, journel=True):
		"Creates a Ext2/3 filesystem on the minor specified"

		# Make the command string
		if journel:
			cmd = "mke2fs -j" + self._device + str(self._minor)
		else:
			cmd = "mke2fs " + self._device + str(self._minor)
		
		# Run it
		output = self._run(cmd)
