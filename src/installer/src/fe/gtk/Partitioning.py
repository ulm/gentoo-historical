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
This is the neutered partition screen.

On this screen, you will be presented with a list of detected partitionable devices. Selecting
a device will show you the current partitions on it (if any) and allow you to add, remove, and
resize partitions.
"""
 	
		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0) # This was removed for screen space
		self.add_content(vert)

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
