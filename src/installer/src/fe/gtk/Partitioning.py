import gtk
import GLIScreen
import GLIStorageDevice
import re
import PartitionButton

class Panel(GLIScreen.GLIScreen):

	title = "Partitioning"
	part_buttons = []
	drives = []
	devices = {}
	active_device = ""
	active_device_bytes_in_cylinder = 0
	active_device_cylinders = 0
	active_part_min_size = 0
	active_part_max_size = 0
	active_part_cur_size = 0
	active_part_minor = 0
	colors = { 'ext2': '#0af2fe', 'ext3': '#0af2fe', 'unalloc': '#a2a2a2', 'unknown': '#ed03e0', 'free': '#ffffff', 'ntfs': '#f20600', 'fat': '#3d07f9', 'reiserfs': '#e9f704', 'linux-swap': '#12ff09' }

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)

		vert = gtk.VBox(gtk.FALSE, 10)
		vert.set_border_width(10)

		content_str = """
On this screen, you will be presented with a list of detected partitionable devices. Selecting
a device will show you the current partitions on it (if any) and allow you to add, remove, and
resize partitions.
"""
 	
		content_label = gtk.Label(content_str)
#		vert.pack_start(content_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0) # This was removed for screen space
		container = gtk.HBox(gtk.FALSE, 10)
		detected_dev_label = gtk.Label("Devices:")
		container.pack_start(detected_dev_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		self.detected_dev_combo = gtk.combo_box_new_text()
		self.detected_dev_combo.connect("changed", self.drive_changed)
		container.pack_start(self.detected_dev_combo, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)

		self.drives = GLIStorageDevice.detect_devices()
		self.drives.sort()
		for drive in self.drives:
			self.devices[drive] = GLIStorageDevice.Device(drive)
			self.devices[drive].set_partitions_from_disk()
			self.detected_dev_combo.append_text(drive)
		self.active_device = self.drives[0]

		vert.pack_start(container, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

		# This builds the container for the "whole disk" display at the top
		part_table_frame = gtk.Frame()
		part_table_frame.set_shadow_type(gtk.SHADOW_IN)
		self.part_table = gtk.Table(1, 1, gtk.FALSE)
		part_table_frame.add(self.part_table)
		vert.pack_start(part_table_frame, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)

		# This builds the partition info box
		self.part_info_box = gtk.HBox(gtk.FALSE, 0)
		part_info_table = gtk.Table(6, 2, gtk.TRUE)
		part_info_table.set_col_spacings(10)
		self.info_partition = gtk.Label("/dev/hda1")
		self.info_type = gtk.Label("Primary")
		self.info_filesystem = gtk.Label("ext3")
		self.info_start = gtk.Label("0")
		self.info_end = gtk.Label("560")
		self.info_size = gtk.Label("280M")
		part_info_table.attach(gtk.Label("Partition:"), 0, 1, 0, 1)
		part_info_table.attach(self.info_partition, 1, 2, 0, 1)
		part_info_table.attach(gtk.Label("Type:"), 0, 1, 1, 2)
		part_info_table.attach(self.info_type, 1, 2, 1, 2)
		part_info_table.attach(gtk.Label("Filesystem:"), 0, 1, 2, 3)
		part_info_table.attach(self.info_filesystem, 1, 2, 2, 3)
		part_info_table.attach(gtk.Label("Start cylinder:"), 0, 1, 3, 4)
		part_info_table.attach(self.info_start, 1, 2, 3, 4)
		part_info_table.attach(gtk.Label("End cylinder:"), 0, 1, 4, 5)
		part_info_table.attach(self.info_end, 1, 2, 4, 5)
		part_info_table.attach(gtk.Label("Size:"), 0, 1, 5, 6)
		part_info_table.attach(self.info_size, 1, 2, 5, 6)
		self.part_info_box.pack_start(part_info_table, expand=gtk.FALSE, fill=gtk.FALSE)
		vert.pack_start(self.part_info_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)

		# This builds the resize slider and the Entry widgets below it
		self.resize_box = gtk.VBox(gtk.FALSE, 0)
		self.resize_hpaned = gtk.HPaned()
		self.resize_hpaned.connect("size-allocate", self.part_resized)
		self.resize_part_space_frame = gtk.Frame()
		self.resize_part_space_frame.set_shadow_type(gtk.SHADOW_IN)
		self.resize_part_space = PartitionButton.Partition(color1=self.colors['linux-swap'], color2=self.colors['free'], division=0, label="")
		self.resize_part_space.set_sensitive(gtk.FALSE)
		self.resize_part_space_frame.add(self.resize_part_space)
		self.resize_hpaned.pack1(self.resize_part_space_frame, resize=gtk.TRUE, shrink=gtk.FALSE)
		self.resize_unalloc_space_frame = gtk.Frame()
		self.resize_unalloc_space_frame.set_shadow_type(gtk.SHADOW_IN)
		self.resize_unalloc_space = PartitionButton.Partition(color1=self.colors['unalloc'], color2=self.colors['unalloc'], label="")
		self.resize_unalloc_space.set_sensitive(gtk.FALSE)
		self.resize_unalloc_space_frame.add(self.resize_unalloc_space)
		self.resize_hpaned.add2(self.resize_unalloc_space_frame)
		self.resize_hpaned.set_position(0)
		self.resize_box.pack_start(self.resize_hpaned, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		resize_text_box = gtk.HBox(gtk.FALSE, 0)
		resize_text_box.pack_start(gtk.Label("Partition size:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=6)
		self.resize_info_part_size = gtk.Entry(max=11)
		self.resize_info_part_size.set_width_chars(8)
		self.resize_info_part_size.connect("insert-text", self.validate_keypress)
		self.resize_info_part_size.connect("focus-out-event", self.update_slider_and_entries, "part_size")
		resize_text_box.pack_start(self.resize_info_part_size, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		resize_text_box.pack_start(gtk.Label("MB"), expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		resize_text_box.pack_start(gtk.Label("Partition freespace:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=6)
		self.resize_info_part_free = gtk.Entry(max=11)
		self.resize_info_part_free.set_width_chars(8)
		self.resize_info_part_free.connect("insert-text", self.validate_keypress)
		self.resize_info_part_free.connect("focus-out-event", self.update_slider_and_entries, "part_free")
		resize_text_box.pack_start(self.resize_info_part_free, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		resize_text_box.pack_start(gtk.Label("MB"), expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		resize_text_box.pack_start(gtk.Label("Unallocated size:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=6)
		self.resize_info_unalloc_size = gtk.Entry(max=11)
		self.resize_info_unalloc_size.set_width_chars(8)
		self.resize_info_unalloc_size.connect("insert-text", self.validate_keypress)
		self.resize_info_unalloc_size.connect("focus-out-event", self.update_slider_and_entries, "unalloc-size")
		resize_text_box.pack_start(self.resize_info_unalloc_size, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		resize_text_box.pack_start(gtk.Label("MB"), expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		self.resize_box.pack_start(resize_text_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		vert.pack_start(self.resize_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)

		# This builds the row of buttons
		self.part_button_box = gtk.HBox(gtk.TRUE, 0)
		part_button_delete = gtk.Button("Remove")
		part_button_delete.connect("clicked", self.part_button_delete_clicked)
		self.part_button_box.pack_start(part_button_delete, expand=gtk.FALSE, fill=gtk.FALSE)
		part_button_updatesize = gtk.Button("Update size")
		part_button_updatesize.connect("clicked", self.part_button_updatesize_clicked)
		self.part_button_box.pack_start(part_button_updatesize, expand=gtk.FALSE, fill=gtk.FALSE)
		part_button_resetsize = gtk.Button("Reset size")
		part_button_resetsize.connect("clicked", self.part_button_resetsize_clicked)
		self.part_button_box.pack_start(part_button_resetsize, expand=gtk.FALSE, fill=gtk.FALSE)
		vert.pack_start(self.part_button_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)

		# This builds the color key at the bottom
		color_codes_box = gtk.HBox(gtk.FALSE, 0)
		linuxswap_color = gtk.Image()
		linuxswap_color.set_from_file(self.full_path + "/linuxswap_color_square.jpg")
		color_codes_box.pack_start(linuxswap_color, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		color_codes_box.pack_start(gtk.Label("Linux swap"), padding=3)
		ext2_color = gtk.Image()
		ext2_color.set_from_file(self.full_path + "/ext2_color_square.jpg")
		color_codes_box.pack_start(ext2_color, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		color_codes_box.pack_start(gtk.Label("Ext2/3"), padding=3)
		reiserfs_color = gtk.Image()
		reiserfs_color.set_from_file(self.full_path + "/reiserfs_color_square.jpg")
		color_codes_box.pack_start(reiserfs_color, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		color_codes_box.pack_start(gtk.Label("Reiser"), padding=3)
		fat_color = gtk.Image()
		fat_color.set_from_file(self.full_path + "/fat_color_square.jpg")
		color_codes_box.pack_start(fat_color, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		color_codes_box.pack_start(gtk.Label("FAT"), padding=3)
		ntfs_color = gtk.Image()
		ntfs_color.set_from_file(self.full_path + "/ntfs_color_square.jpg")
		color_codes_box.pack_start(ntfs_color, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		color_codes_box.pack_start(gtk.Label("NTFS"), padding=3)
		unknown_color = gtk.Image()
		unknown_color.set_from_file(self.full_path + "/unknown_color_square.jpg")
		color_codes_box.pack_start(unknown_color, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		color_codes_box.pack_start(gtk.Label("Unknown/Other"), padding=3)
		freespace_color = gtk.Image()
		freespace_color.set_from_file(self.full_path + "/freespace_color_square.jpg")
		color_codes_box.pack_start(freespace_color, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		color_codes_box.pack_start(gtk.Label("Free space"), padding=3)
		unalloc_color = gtk.Image()
		unalloc_color.set_from_file(self.full_path + "/unalloc_color_square.jpg")
		color_codes_box.pack_start(unalloc_color, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		color_codes_box.pack_start(gtk.Label("Unallocated"), padding=3)
		vert.pack_end(color_codes_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=2)

		self.add_content(vert)
		self.detected_dev_combo.set_active(0)

	def drive_changed(self, combobox, data=None):
		self.active_device = self.drives[self.detected_dev_combo.get_active()]
		self.draw_part_box()
		self.active_device_cylinders = self.devices[self.active_device].get_num_cylinders()
		self.active_device_bytes_in_cylinder = self.devices[self.active_device].get_cylinder_size()
		self.info_partition.set_text("")
		self.info_type.set_text("")
		self.info_filesystem.set_text("")
		self.info_start.set_text("")
		self.info_end.set_text("")
		self.info_size.set_text("")
		self.part_info_box.hide_all()
		self.resize_box.hide_all()
		self.part_button_box.hide_all()

	def part_selected(self, button, dev=None, minor=None):
		normal_resize_types = ['ext2', 'ext3', 'fat32', 'ntfs', 'fat16', 'reiserfs']
		minor = int(minor)
		tmppart = self.devices[dev].get_partitions()[minor]
		self.info_partition.set_text(dev + str(minor))
		if int(minor) < 5:
			if tmppart.get_type() == "extended":
				self.info_type.set_text("Extended")
			else:
				self.info_type.set_text("Primary")
		else:
			self.info_type.set_text("Logical")
		type = tmppart.get_type()
		if type == "extended":
			self.info_filesystem.set_text("N/A")
		else:
			self.info_filesystem.set_text(type)
		start = tmppart.get_start()
		end = tmppart.get_end()
		self.info_start.set_text(str(start))
		self.info_end.set_text(str(end))
		part_size = int(round(float(self.devices[dev].get_cylinder_size()) * (end - start + 1) / 1024 / 1024))
		self.info_size.set_text(str(part_size) + " MB")
		min_size = tmppart.get_min_cylinders_for_resize()
		max_size = tmppart.get_max_cylinders_for_resize()
		hpaned_width = self.resize_hpaned.get_allocation().width
		hpaned_pos = hpaned_width
		if max_size > end:
			hpaned_pos = int(float(float(end) / float(max_size)) * hpaned_width) - 5
		self.resize_hpaned.set_position(hpaned_pos)
		self.resize_info_part_size.set_text(str(part_size))
		self.resize_info_part_free.set_text("0")
		self.resize_info_unalloc_size.set_text("0")
		self.active_part_min_size = min_size
		self.active_part_max_size = max_size - start + 1
		self.active_part_cur_size = end - start + 1
		self.active_part_minor = tmppart.get_minor()
		if hpaned_pos == hpaned_width: hpaned_pos = hpaned_pos - 5
		if type in normal_resize_types:
			self.resize_part_space.set_division(int(hpaned_pos * (float(self.active_part_min_size) / float(self.active_part_cur_size))) - 12)
			self.resize_part_space.set_colors(self.colors[type], self.colors['free'])
		elif type == "linux-swap":
			self.resize_part_space.set_division(0)
			self.resize_part_space.set_colors(self.colors['linux-swap'], self.colors['linux-swap'])
		else:
			self.rsize_part_space.set_division(hpaned_pos)
			self.resize_part_space.set_colors(self.colors['unknown'], self.colors['unknown'])
		self.part_info_box.show_all()
		self.resize_box.show_all()
		self.part_button_box.show_all()

	def part_resized(self, widget, allocation):
		newwidth = allocation.width
		hpaned_width = self.resize_hpaned.get_allocation().width - 5
		hpaned_pos = self.resize_hpaned.get_position()
#		print "hpaned_width is " + str(hpaned_width) + ", hpaned_pos is " + str(hpaned_pos)
		part_space = float(hpaned_width - (hpaned_width - hpaned_pos)) / hpaned_width
		free_space = float(hpaned_width - hpaned_pos) / hpaned_width
		part_size_cyl = round(self.active_part_max_size * part_space)
		part_size_mib = int(round(part_size_cyl * self.active_device_bytes_in_cylinder / 1024 / 1024))
#		print "part_size_cyl is " + str(part_size_cyl) + ", part_size_mib is " + str(part_size_mib)
		self.resize_info_part_size.set_text(str(part_size_mib))
		part_free_cyl = part_size_cyl - self.active_part_min_size
		part_free_mib = int(round(part_free_cyl * self.active_device_bytes_in_cylinder / 1024 / 1024))
#		print "part_free_cyl is " + str(part_free_cyl) + ", part_free_mib is " + str(part_free_mib)
		self.resize_info_part_free.set_text(str(part_free_mib))
		part_unalloc_cyl = self.active_part_max_size - part_size_cyl
		part_unalloc_mib = int(round(part_unalloc_cyl * self.active_device_bytes_in_cylinder / 1024 / 1024))
#		print "part_unalloc_cyl is " + str(part_unalloc_cyl) + ", part_unalloc_mib is " + str(part_unalloc_mib)
		self.resize_info_unalloc_size.set_text(str(part_unalloc_mib))

	def validate_keypress(self, editable, new_text, new_text_length, position):
		if new_text == ".": return
		try:
			float(new_text)
		except:
			editable.stop_emission("insert-text")

	def update_slider_and_entries(self, widget, event, which_one):
		print "Entry " + which_one + " has been updated"

	def part_button_delete_clicked(self, button, data=None):
		pass

	def part_button_updatesize_clicked(self, button, data=None):
		hpaned_width = self.resize_hpaned.get_allocation().width - 5
		hpaned_pos = self.resize_hpaned.get_position()
		part_space = float(hpaned_width - (hpaned_width - hpaned_pos)) / hpaned_width
		part_size_cyl = round(self.active_part_max_size * part_space)
		tmppart = self.devices[self.active_device].get_partitions()[self.active_part_minor]
		tmppart.resize(int(tmppart.get_start()), int(tmppart.get_start() + part_size_cyl - 1))
		self.draw_part_box()

	def part_button_resetsize_clicked(self, button, data=None):
		pass

	def draw_part_box(self):
		partlist = self.devices[self.active_device].get_ordered_partition_list()
		tmpparts = self.devices[self.active_device].get_partitions()
		cylinders = self.devices[self.active_device].get_num_cylinders()
		for button in self.part_buttons:
			self.part_table.remove(self.part_buttons[button])
		self.part_table.resize(1, 100)
		self.part_buttons = {}
		last_percent = 0
		for part in partlist:
			if re.compile("^Free Space").match(part) != None:
				new_start, new_end = re.compile("^Free Space \((\d+)\s*-\s*(\d+)\)").match(part).groups()
				partsize = int(new_end) - int(new_start) + 1
				percent = (float(partsize) / float(cylinders)) * 100
				if percent > 0 and percent < 1: percent = 1
				percent = int(percent)
				self.part_buttons['free_' + new_start + '_' + new_end] = PartitionButton.Partition(color1=self.colors['unalloc'], color2=self.colors['unalloc'], label="", division=0)
				self.part_table.attach(self.part_buttons['free_' + new_start + '_' + new_end], last_percent, (last_percent + percent), 0, 1)
				last_percent = last_percent + percent
			elif re.compile("^(/dev/[a-zA-Z]+)(\d+):").search(part) != None:
				tmpdevice, tmpminor = re.compile("^(/dev/[a-zA-Z]+)(\d+):").search(part).groups()
				if tmpparts[int(tmpminor)].is_logical(): continue
				partsize = tmpparts[int(tmpminor)].get_end() - tmpparts[int(tmpminor)].get_start() + 1
				percent = (float(partsize) / float(cylinders)) * 100
				if percent > 0 and percent < 1: percent = 1
				percent = int(percent)
				if tmpparts[int(tmpminor)].is_extended():
					self.part_buttons[int(tmpminor)] = gtk.Button()
				else:
					self.part_buttons[int(tmpminor)] = PartitionButton.Partition(color1=self.colors[tmpparts[int(tmpminor)].get_type()], color2=self.colors[tmpparts[int(tmpminor)].get_type()], label="", division=0)
				self.part_buttons[int(tmpminor)].connect("clicked", self.part_selected, tmpdevice, tmpminor)
				self.part_table.attach(self.part_buttons[int(tmpminor)], last_percent, (last_percent + percent), 0, 1)
				last_percent = last_percent + percent
		self.part_table.show_all()

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
		self.drive_changed(None)
