import gtk
import GLIScreen
import GLIStorageDevice
import re
import PartitionButton

class Panel(GLIScreen.GLIScreen):

	title = "Partitioning"
	part_buttons = {}
	drives = []
	devices = {}
	active_device = ""
	active_device_bytes_in_cylinder = 0
	active_device_bytes_in_sector = 0
	active_device_cylinders = 0
	active_part_min_size = 0
	active_part_max_size = 0
	active_part_cur_size = 0
	active_part_start_cyl = 0
	active_part_minor = 0
	colors = { 'ext2': '#0af2fe', 'ext3': '#0af2fe', 'unalloc': '#a2a2a2', 'unknown': '#ed03e0', 'free': '#ffffff', 'ntfs': '#f20600', 'fat': '#3d07f9', 'fat32': '#3d07f9', 'reiserfs': '#e9f704', 'linux-swap': '#12ff09' }
	supported_filesystems = ['ext2', 'ext3', 'reiserfs', 'linux-swap', 'fat32', 'ntfs']

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)

		vert = gtk.VBox(gtk.FALSE, 0)
		vert.set_border_width(10)

		content_str = """On this screen, you will be presented with a list of detected partitionable devices. Selecting
a device will show you the current partitions on it (if any) and allow you to add, remove, and
resize partitions.
"""
 
		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0) # This was removed for screen space
		container = gtk.HBox(gtk.FALSE, 0)
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
		part_info_table = gtk.Table(6, 2, gtk.FALSE)
		part_info_table.set_col_spacings(10)
		info_partition_label = gtk.Label("Partition:")
		info_partition_label.set_alignment(0.0, 0.5)
		self.info_partition = gtk.Label()
		self.info_partition.set_alignment(0.0, 0.5)
		info_type_label = gtk.Label("Type:")
		info_type_label.set_alignment(0.0, 0.5)
		self.info_type = gtk.Label()
		self.info_type.set_alignment(0.0, 0.5)
		info_filesystem_label = gtk.Label("Filesystem:")
		info_filesystem_label.set_alignment(0.0, 0.5)
		self.info_filesystem = gtk.Label()
		self.info_filesystem.set_alignment(0.0, 0.5)
		info_start_label = gtk.Label("Start sector:")
		info_start_label.set_alignment(0.0, 0.5)
		self.info_start = gtk.Label()
		self.info_start.set_alignment(0.0, 0.5)
		info_end_label = gtk.Label("End sector:")
		info_end_label.set_alignment(0.0, 0.5)
		self.info_end = gtk.Label()
		self.info_end.set_alignment(0.0, 0.5)
		info_size_label = gtk.Label("Size:")
		info_size_label.set_alignment(0.0, 0.5)
		self.info_size = gtk.Label()
		self.info_size.set_alignment(0.0, 0.5)
		part_info_table.attach(info_partition_label, 0, 1, 0, 1)
		part_info_table.attach(self.info_partition, 1, 2, 0, 1)
		part_info_table.attach(info_type_label, 0, 1, 1, 2)
		part_info_table.attach(self.info_type, 1, 2, 1, 2)
		part_info_table.attach(info_filesystem_label, 0, 1, 2, 3)
		part_info_table.attach(self.info_filesystem, 1, 2, 2, 3)
		part_info_table.attach(info_start_label, 0, 1, 3, 4)
		part_info_table.attach(self.info_start, 1, 2, 3, 4)
		part_info_table.attach(info_end_label, 0, 1, 4, 5)
		part_info_table.attach(self.info_end, 1, 2, 4, 5)
		part_info_table.attach(info_size_label, 0, 1, 5, 6)
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
		self.resize_hpaned.pack1(self.resize_part_space_frame, resize=gtk.TRUE, shrink=gtk.TRUE)
		self.resize_unalloc_space_frame = gtk.Frame()
		self.resize_unalloc_space_frame.set_shadow_type(gtk.SHADOW_IN)
		self.resize_unalloc_space = PartitionButton.Partition(color1=self.colors['unalloc'], color2=self.colors['unalloc'], label="")
		self.resize_unalloc_space.set_sensitive(gtk.FALSE)
		self.resize_unalloc_space_frame.add(self.resize_unalloc_space)
		self.resize_hpaned.add2(self.resize_unalloc_space_frame)
		self.resize_hpaned.set_position(0)
		self.resize_box.pack_start(self.resize_hpaned, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		resize_text_box = gtk.HBox(gtk.FALSE, 0)
		resize_text_box.pack_start(gtk.Label("Type:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=6)
		self.resize_info_part_type = gtk.combo_box_new_text()
		self.resize_info_part_type.append_text("Primary")
		self.resize_info_part_type.append_text("Logical")
		self.resize_info_part_type.set_active(0)
		resize_text_box.pack_start(self.resize_info_part_type, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		resize_text_box.pack_start(gtk.Label("Filesystem:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=6)
		self.resize_info_part_filesystem = gtk.combo_box_new_text()
		for fs in self.supported_filesystems:
			self.resize_info_part_filesystem.append_text(fs)
		self.resize_info_part_filesystem.set_active(0)
		self.resize_info_part_filesystem.connect("changed", self.filesystem_changed)
		resize_text_box.pack_start(self.resize_info_part_filesystem, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		resize_text_box.pack_start(gtk.Label("New size:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=6)
		self.resize_info_part_size = gtk.Entry(max=9)
		self.resize_info_part_size.set_width_chars(7)
		self.resize_info_part_size.connect("insert-text", self.validate_keypress)
		self.resize_info_part_size.connect("focus-out-event", self.update_slider_and_entries, "part_size")
		resize_text_box.pack_start(self.resize_info_part_size, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		resize_text_box.pack_start(gtk.Label("MB"), expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		resize_text_box.pack_start(gtk.Label("Unalloc. size:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=6)
		self.resize_info_unalloc_size = gtk.Entry(max=9)
		self.resize_info_unalloc_size.set_width_chars(7)
		self.resize_info_unalloc_size.connect("insert-text", self.validate_keypress)
		self.resize_info_unalloc_size.connect("focus-out-event", self.update_slider_and_entries, "unalloc-size")
		resize_text_box.pack_start(self.resize_info_unalloc_size, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		resize_text_box.pack_start(gtk.Label("MB"), expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		self.resize_box.pack_start(resize_text_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		vert.pack_start(self.resize_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)

		# This builds the row of buttons
		self.part_button_box = gtk.HBox(gtk.FALSE, 0)
		self.part_button_create = gtk.Button(" Create ")
		self.part_button_create.connect("clicked", self.part_button_create_clicked)
		self.part_button_box.pack_start(self.part_button_create, expand=gtk.FALSE, fill=gtk.FALSE)
		self.part_button_delete = gtk.Button(" Remove Partition ")
		self.part_button_delete.connect("clicked", self.part_button_delete_clicked)
		self.part_button_box.pack_start(self.part_button_delete, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		part_button_dump_info = gtk.Button(" Dump to console ")
		part_button_dump_info.connect("clicked", self.dump_part_info_to_console)
		self.part_button_box.pack_start(part_button_dump_info, expand=gtk.FALSE, fill=gtk.FALSE)
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
		self.active_device_bytes_in_sector = self.devices[self.active_device].get_sector_size()
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
		part_size = int(round(float(self.devices[dev].get_sector_size()) * (end - start + 1) / 1024 / 1024))
		self.info_size.set_text(str(part_size) + " MB")
		self.active_part_minor = tmppart.get_minor()
		self.resize_box.hide_all()
		self.part_button_delete.set_sensitive(gtk.TRUE)
		self.part_button_create.set_sensitive(gtk.FALSE)
		self.part_info_box.show_all()
		self.part_button_box.show_all()

	def unalloc_selected(self, button, dev=None, extended=False, start=0, end=0):
		self.info_partition.set_text(dev + " (unallocated space)")
		if self.devices[self.active_device].get_partition_at(start, ignore_extended=0) != 0:
			self.info_type.set_text("Logical")
		else:
			self.info_type.set_text("Primary")
		self.info_filesystem.set_text("Unallocated space")
		self.info_start.set_text(str(start))
		self.info_end.set_text(str(end))
		part_size = int(round(float(self.devices[dev].get_sector_size()) * (end - start + 1) / 1024 / 1024))
		self.info_size.set_text(str(part_size) + " MB")

		min_size = 0
		max_size = end - start
		hpaned_width = self.resize_hpaned.get_allocation().width
		hpaned_pos = hpaned_width
		if max_size > end:
			hpaned_pos = int(float(float(end) / float(max_size)) * hpaned_width) - 5
		self.resize_hpaned.set_position(hpaned_pos)
		self.resize_info_part_size.set_text(str(part_size))
		self.resize_info_unalloc_size.set_text("0")
		self.active_part_min_size = min_size
		self.active_part_max_size = max_size
		self.active_part_cur_size = max_size
		self.active_part_start_cyl = start
		self.resize_part_space.set_division(0)
		self.resize_part_space.set_colors(self.colors['ext3'], self.colors['ext3'])
		self.part_info_box.show_all()
		self.resize_box.show_all()
		self.part_button_delete.set_sensitive(gtk.FALSE)
		self.part_button_create.set_sensitive(gtk.TRUE)
		if self.devices[self.active_device].get_extended_partition():
			if self.devices[self.active_device].get_partition_at(start, ignore_extended=0) != 0:
				self.resize_info_part_type.set_active(1)
			else:
				self.resize_info_part_type.set_active(0)
			self.resize_info_part_type.set_sensitive(gtk.FALSE)
		else:
			self.resize_info_part_type.set_active(0)
			self.resize_info_part_type.set_sensitive(gtk.TRUE)
		self.resize_info_part_filesystem.set_active(0)
		self.part_button_box.show_all()

	def part_resized(self, widget, allocation):
		newwidth = allocation.width
		hpaned_width = self.resize_hpaned.get_allocation().width - 5
		hpaned_pos = self.resize_hpaned.get_position()
		part_space = float(hpaned_width - (hpaned_width - hpaned_pos)) / hpaned_width
		part_size_cyl = round(self.active_part_max_size * part_space)
		part_size_mib = int(round(part_size_cyl * self.active_device_bytes_in_sector / 1024 / 1024))
		self.resize_info_part_size.set_text(str(part_size_mib))
		part_unalloc_cyl = self.active_part_max_size - part_size_cyl
		part_unalloc_mib = int(round(part_unalloc_cyl * self.active_device_bytes_in_sector / 1024 / 1024))
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
		msgdlg = gtk.MessageDialog(parent=self.controller.window, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format="Are you sure you want to delete " + self.active_device + str(self.active_part_minor))
		resp = msgdlg.run()
		msgdlg.destroy()
		if resp == gtk.RESPONSE_YES:
			self.devices[self.active_device].remove_partition(self.active_part_minor)
			if self.active_part_minor > 4:
				ext_part = self.devices[self.active_device].get_extended_partition()
				if len(self.devices[self.active_device].get_partitions()[ext_part].get_logicals()) == 0:
					self.devices[self.active_device].remove_partition(ext_part)
			self.drive_changed(None)

	def part_button_create_clicked(self, button, data=None):
		hpaned_width = self.resize_hpaned.get_allocation().width - 5
		hpaned_pos = self.resize_hpaned.get_position()
		part_space = float(hpaned_width - (hpaned_width - hpaned_pos)) / hpaned_width
		part_size_cyl = round(self.active_part_max_size * part_space)
		start = self.active_part_start_cyl
		end = int(start + part_size_cyl)
		if self.resize_info_part_type.get_active() == 1 and self.devices[self.active_device].get_extended_partition() == 0: # Logical and no extended partition
			free_start, free_end = self.devices[self.active_device].get_free_space(start)
			self.devices[self.active_device].add_partition(self.devices[self.active_device].get_free_minor_at(start, end), free_start, free_end, "extended")
		minor = self.devices[self.active_device].get_free_minor_at(start, end)
		type = self.supported_filesystems[self.resize_info_part_filesystem.get_active()]
		self.devices[self.active_device].add_partition(minor, start, end, type)
		self.draw_part_box()
		self.part_selected(None, self.active_device, minor)

	def part_button_resetsize_clicked(self, button, data=None):
		pass

	def draw_part_box(self):
		partlist = self.devices[self.active_device].get_ordered_partition_list()
		tmpparts = self.devices[self.active_device].get_partitions()
		cylinders = self.devices[self.active_device].get_num_cylinders()
		sectors = self.devices[self.active_device].get_num_sectors()
		for button in self.part_buttons.keys():
			self.part_table.remove(self.part_buttons[button])
		self.part_table.resize(1, 100)
		self.part_buttons = {}
		last_percent = 0
		last_log_percent = 0
		extended_part = 0
		extended_table = None
		for part in partlist:
			if re.compile("^Free Space").match(part) != None:
				new_start, new_end = re.compile("^Free Space \((\d+)\s*-\s*(\d+)\)").match(part).groups()
				partsize = int(new_end) - int(new_start) + 1
				percent = (float(partsize) / float(sectors)) * 100
				if percent > 0 and percent < 1: percent = 1
				percent = int(percent)
				if self.devices[self.active_device].get_partition_at(int(new_start), ignore_extended=0):
					tmpbutton = PartitionButton.Partition(color1=self.colors['unalloc'], color2=self.colors['unalloc'], label="", division=0)
					tmpbutton.connect("clicked", self.unalloc_selected, self.active_device, False, int(new_start), int(new_end))
					extended_table.attach(tmpbutton, last_log_percent, (last_log_percent + percent), 0, 1)
					last_log_percent = last_log_percent + percent
				else:
					self.part_buttons['free_' + new_start + '_' + new_end] = PartitionButton.Partition(color1=self.colors['unalloc'], color2=self.colors['unalloc'], label="", division=0)
					if self.devices[self.active_device].get_partitions().has_key(1) and self.devices[self.active_device].get_partitions().has_key(2) and self.devices[self.active_device].get_partitions().has_key(3) and self.devices[self.active_device].get_partitions().has_key(4):
						self.part_buttons['free_' + new_start + '_' + new_end].connect("clicked", self.show_no_more_primary_message)
					else:
						self.part_buttons['free_' + new_start + '_' + new_end].connect("clicked", self.unalloc_selected, self.active_device, False, int(new_start), int(new_end))
					self.part_table.attach(self.part_buttons['free_' + new_start + '_' + new_end], last_percent, (last_percent + percent), 0, 1)
					last_percent = last_percent + percent
			elif re.compile("^(/dev/[a-zA-Z]+)(\d+):").search(part) != None:
				tmpdevice, tmpminor = re.compile("^(/dev/[a-zA-Z]+)(\d+):").search(part).groups()
				partsize = tmpparts[int(tmpminor)].get_end() - tmpparts[int(tmpminor)].get_start() + 1
				percent = (float(partsize) / float(sectors)) * 100
				if percent > 0 and percent < 1: percent = 1
				percent = int(percent)
				if tmpparts[int(tmpminor)].is_extended():
					extended_table = gtk.Table(1, percent)
					extended_table.set_border_width(3)
					extended_part = int(tmpminor)
					self.part_buttons[int(tmpminor)] = extended_table
					self.part_table.attach(self.part_buttons[int(tmpminor)], last_percent, (last_percent + percent), 0, 1)
					last_percent = last_percent + percent
				elif tmpparts[int(tmpminor)].is_logical():
					tmpbutton = PartitionButton.Partition(color1=self.colors[tmpparts[int(tmpminor)].get_type()], color2=self.colors[tmpparts[int(tmpminor)].get_type()], label="", division=0)
					if percent >= 15:
						tmpbutton.set_label(tmpdevice + tmpminor)
					extended_table.attach(tmpbutton, last_log_percent, (last_log_percent + percent), 0, 1)
					last_log_percent = last_log_percent + percent
					tmpbutton.connect("clicked", self.part_selected, tmpdevice, tmpminor)
				else:
					self.part_buttons[int(tmpminor)] = PartitionButton.Partition(color1=self.colors[tmpparts[int(tmpminor)].get_type()], color2=self.colors[tmpparts[int(tmpminor)].get_type()], label="", division=0)
					if percent >= 15:
						self.part_buttons[int(tmpminor)].set_label(tmpdevice + tmpminor)
					self.part_buttons[int(tmpminor)].connect("clicked", self.part_selected, tmpdevice, tmpminor)
					self.part_table.attach(self.part_buttons[int(tmpminor)], last_percent, (last_percent + percent), 0, 1)
					last_percent = last_percent + percent
		self.part_table.show_all()

	def show_no_more_primary_message(self, button, data=None):
		msgdlg = gtk.MessageDialog(parent=self.controller.window, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK, message_format="You cannot create more than 4 primary partitions. If you need more partitions, delete one or more and create logical partitions.")
		msgdlg.run()
		msgdlg.destroy()

	def dump_part_info_to_console(self, button, data=None):
		import pprint
		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(self.devices[self.active_device].get_install_profile_structure())

	def filesystem_changed(self, widget, data=None):
		fs = self.supported_filesystems[self.resize_info_part_filesystem.get_active()]
		self.resize_part_space.set_colors(self.colors[fs], self.colors[fs])
		self.resize_part_space.get_child().expose_event(None, None)

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
		self.drive_changed(None)

	def deactivate(self):
		parts_tmp = {}
		for part in self.devices.keys():
			parts_tmp[part] = self.devices[part].get_install_profile_structure()
		self.controller.install_profile.set_partition_tables(parts_tmp)

		return True
