import gtk
import PartitionButton

class PartProperties(gtk.Window):

	def __init__(self, controller, device, minor, start, end, min_size, max_size, fstype):
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

		self.controller = controller
		self.connect("delete_event", self.delete_event)
		self.connect("destroy", self.destroy_event)
		self.set_default_size(600,400)
#		self.set_geometry_hints(None, min_width=800, min_height=600, max_width=800, max_height=600)
		self.set_title("Properties for " + device + str(minor))

		self.globalbox = gtk.VBox(gtk.FALSE, 0)
		self.globalbox.set_border_width(10)

		self.globalbox.pack_start(gtk.Label("Partition properties dialog"), expand=gtk.FALSE, fill=gtk.FALSE, padding=0)



		self.resize_box = gtk.VBox(gtk.FALSE, 0)
		self.resize_hpaned = gtk.HPaned()
#		self.resize_hpaned.connect("size-allocate", self.part_resized)
		self.resize_part_space_frame = gtk.Frame()
		self.resize_part_space_frame.set_shadow_type(gtk.SHADOW_IN)
		self.resize_part_space = PartitionButton.Partition(color1=self.controller.colors['linux-swap'], color2=self.controller.colors['free'], division=0, label="")
		self.resize_part_space.set_sensitive(gtk.FALSE)
		self.resize_part_space_frame.add(self.resize_part_space)
		self.resize_hpaned.pack1(self.resize_part_space_frame, resize=gtk.TRUE, shrink=gtk.TRUE)
		self.resize_unalloc_space_frame = gtk.Frame()
		self.resize_unalloc_space_frame.set_shadow_type(gtk.SHADOW_IN)
		self.resize_unalloc_space = PartitionButton.Partition(color1=self.controller.colors['unalloc'], color2=self.controller.colors['unalloc'], label="")
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
		for fs in self.controller.supported_filesystems:
			self.resize_info_part_filesystem.append_text(fs)
		self.resize_info_part_filesystem.set_active(0)
#		self.resize_info_part_filesystem.connect("changed", self.filesystem_changed)
		resize_text_box.pack_start(self.resize_info_part_filesystem, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		resize_text_box.pack_start(gtk.Label("New size:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=6)
		self.resize_info_part_size = gtk.Entry(max=9)
		self.resize_info_part_size.set_width_chars(7)
#		self.resize_info_part_size.connect("insert-text", self.validate_keypress)
#		self.resize_info_part_size.connect("focus-out-event", self.update_slider_and_entries, "part_size")
		resize_text_box.pack_start(self.resize_info_part_size, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		resize_text_box.pack_start(gtk.Label("MB"), expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		resize_text_box.pack_start(gtk.Label("Unalloc. size:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=6)
		self.resize_info_unalloc_size = gtk.Entry(max=9)
		self.resize_info_unalloc_size.set_width_chars(7)
#		self.resize_info_unalloc_size.connect("insert-text", self.validate_keypress)
#		self.resize_info_unalloc_size.connect("focus-out-event", self.update_slider_and_entries, "unalloc-size")
		resize_text_box.pack_start(self.resize_info_unalloc_size, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		resize_text_box.pack_start(gtk.Label("MB"), expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		self.resize_box.pack_start(resize_text_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)
		self.globalbox.pack_start(self.resize_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=3)



		bottom_box = gtk.HBox(gtk.TRUE, 0)
		ok_button = gtk.Button(" OK ")
		ok_button.set_size_request(60, -1)
		ok_button.connect("clicked", self.ok_clicked)
		bottom_box.pack_start(ok_button, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		cancel_button = gtk.Button(" Cancel ")
		cancel_button.set_size_request(60, -1)
		cancel_button.connect("clicked", self.cancel_clicked)
		bottom_box.pack_start(cancel_button, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		self.globalbox.pack_end(bottom_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)

		self.add(self.globalbox)
		self.set_modal(gtk.TRUE)
		self.set_transient_for(self.controller.controller.window)
		self.make_visible()

	def make_visible(self):
		self.show_all()
		self.present()

	def make_invisible(self):
		self.hide_all()

	def ok_clicked(self, button):
		print "OK"
		self.destroy()

	def cancel_clicked(self, button):
		print "Cancel"
		self.destroy()

	def delete_event(self, widget, event, data=None):
		return gtk.FALSE

	def destroy_event(self, widget, data=None):
		return gtk.TRUE
