import gtk
import GLIScreen
import GLIStorageDevice
import re
import PartitionButton
import PartProperties

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

	def __init__(self, controller, parent):
		GLIScreen.GLIScreen.__init__(self, controller, show_title=False)
		self._parent = parent

		vert = gtk.VBox(False, 0)
		vert.set_border_width(10)

		content_str = """On this screen, you will be presented with a list of detected partitionable devices. Selecting
a device will show you the current partitions on it (if any) and allow you to add, remove, and
resize partitions.
"""
 
		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=False, fill=False, padding=0) # This was removed for screen space
		container = gtk.HBox(False, 0)
		detected_dev_label = gtk.Label("Devices:")
		container.pack_start(detected_dev_label, expand=False, fill=False, padding=10)
		self.detected_dev_combo = gtk.combo_box_new_text()
		self.detected_dev_combo.connect("changed", self.drive_changed)
		container.pack_start(self.detected_dev_combo, expand=False, fill=False, padding=0)

		vert.pack_start(container, expand=False, fill=False, padding=10)

		# This builds the container for the "whole disk" display at the top
		part_table_frame = gtk.Frame()
		part_table_frame.set_shadow_type(gtk.SHADOW_IN)
		self.part_table = gtk.Table(1, 1, False)
		self.part_table.set_size_request(-1, 40)
		part_table_frame.add(self.part_table)
		vert.pack_start(part_table_frame, expand=False, fill=False, padding=5)

		# This builds the partition info box
		self.part_info_box = gtk.HBox(False, 0)
		part_info_table = gtk.Table(6, 2, False)
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
		self.part_info_box.pack_start(part_info_table, expand=False, fill=False)
		vert.pack_start(self.part_info_box, expand=False, fill=False, padding=10)

		# This builds the row of buttons
		self.part_button_box = gtk.HBox(False, 0)
		self.part_button_delete = gtk.Button(" Delete ")
		self.part_button_delete.connect("clicked", self.part_button_delete_clicked)
		self.part_button_box.pack_start(self.part_button_delete, expand=False, fill=False, padding=0)
		self.part_button_properties = gtk.Button(" Properties ")
		self.part_button_properties.connect("clicked", self.part_button_properties_clicked)
		self.part_button_box.pack_start(self.part_button_properties, expand=False, fill=False, padding=10)
		part_button_dump_info = gtk.Button(" Dump to console (debug) ")
		part_button_dump_info.connect("clicked", self.dump_part_info_to_console)
		self.part_button_box.pack_start(part_button_dump_info, expand=False, fill=False, padding=0)
		vert.pack_start(self.part_button_box, expand=False, fill=False, padding=10)

		# This builds the color key at the bottom
		color_codes = [ { 'label': "Swap", 'color': '#12ff99' },
                                { 'label': "Ext2/3", 'color': '#0af2fe' },
                                { 'label': "ReiserFS", 'color': '#e9f704' },
                                { 'label': "FAT", 'color': '#3d07f9' },
                                { 'label': "NTFS", 'color': '#f20600' },
                                { 'label': "Other", 'color': '#ed03e0' },
                                { 'label': "Free space", 'color': '#ffffff' },
                                { 'label': "Unallocated", 'color': '#a2a2a2' }
                              ]
		color_codes_box = gtk.HBox(False, 0)
		vert.pack_end(color_codes_box, expand=False, fill=False, padding=2)
		for color in color_codes:
			temp_xpm = [ "12 12 2 1",
                                     "B c #000000",
                                     "C c " + color['color'],
                                     "BBBBBBBBBBBB",
                                     "BCCCCCCCCCCB",
                                     "BCCCCCCCCCCB",
                                     "BCCCCCCCCCCB",
                                     "BCCCCCCCCCCB",
                                     "BCCCCCCCCCCB",
                                     "BCCCCCCCCCCB",
                                     "BCCCCCCCCCCB",
                                     "BCCCCCCCCCCB",
                                     "BCCCCCCCCCCB",
                                     "BCCCCCCCCCCB",
                                     "BBBBBBBBBBBB"
                                   ]
			pixmap, mask = gtk.gdk.pixmap_create_from_xpm_d(self.controller.window.window, None, temp_xpm)
			tmp_image = gtk.Image()
			tmp_image.set_from_pixmap(pixmap, mask)
			color_codes_box.pack_start(tmp_image, expand=False, fill=False, padding=3)
			color_codes_box.pack_start(gtk.Label(color['label']), expand=False, fill=False, padding=3)

		self.add_content(vert)
#		self.detected_dev_combo.set_active(0)

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
#		self.resize_box.hide_all()
		self.part_button_box.hide_all()
#		self.part_mount_info_box.hide_all()

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
		self.part_button_delete.set_sensitive(True)
		self.part_info_box.show_all()
		self.part_button_box.show_all()

	def unalloc_selected(self, button, dev=None, extended=False, start=0, end=0):
		props = PartProperties.PartProperties(self, self.active_device, -1, start, end, 0, 0, "", self.active_device_bytes_in_sector)
		props.run()

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

	def part_button_properties_clicked(self, widget, data=None):
		tmppart = self.devices[self.active_device].get_partitions()[self.active_part_minor]
		props = PartProperties.PartProperties(self, self.active_device, self.active_part_minor, tmppart.get_start(), tmppart.get_end(), tmppart.get_min_sectors_for_resize(), tmppart.get_max_sectors_for_resize(), tmppart.get_type(), self.active_device_bytes_in_sector)
		props.run()

	def activate(self):
#		self.controller.SHOW_BUTTON_EXIT    = True
#		self.controller.SHOW_BUTTON_HELP    = True
#		self.controller.SHOW_BUTTON_BACK    = True
#		self.controller.SHOW_BUTTON_FORWARD = True
#		self.controller.SHOW_BUTTON_FINISH  = False

		if not len(self.drives):
			part_load_error = 0
			tmp_drives = GLIStorageDevice.detect_devices()
			tmp_drives.sort()
			for drive in tmp_drives:
				try:
					self.devices[drive] = GLIStorageDevice.Device(drive)
					self.devices[drive].set_partitions_from_disk()
					self.detected_dev_combo.append_text(drive)
					self.drives.append(drive)
				except:
					if self.devices.has_key(drive): del self.devices[drive]
					part_load_error = 1
			if part_load_error:
				if len(self.drives):
					msgdlg = gtk.MessageDialog(parent=self.controller.window, type=gtk.MESSAGE_WARN, buttons=gtk.BUTTONS_OK, message_format="One or more drives' partition tables could not be read")
					msgdlg.run()
					msgdlg.destroy()
				else:
	msgdlg = gtk.MessageDialog(parent=self.controller.window, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK, message_format="The installer could not read the partition table on any detected drives. You will be forced to use the ugly mode.")
					msgdlg.run()
					msgdlg.destroy()
#					self._parent.switch_screen(None, 1) # Switch to ugly screen
					self._parent.radio_ugly.set_active(True)
					self._parent.radio_pretty.set_sensitive(False)
					self._parent.radio_ugly.set_sensitive(False)
					return
					
		if len(self.drives):
			self.active_device = self.drives[0]
			self.detected_dev_combo.set_active(0)
			self.drive_changed(None)

	def deactivate(self):
		parts_tmp = {}
		for part in self.devices.keys():
			parts_tmp[part] = self.devices[part].get_install_profile_structure()
		self.controller.install_profile.set_partition_tables(parts_tmp)

		return True
