import gtk

class PartProperties(gtk.Window):

	def __init__(self, controller, device, minor, start, end, min_size, max_size, fstype):
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

		self.controller = controller
		self.connect("delete_event", self.delete_event)
		self.connect("destroy", self.destroy_event)
		self.set_default_size(400,300)
#		self.set_geometry_hints(None, min_width=800, min_height=600, max_width=800, max_height=600)
		self.set_title("Properties for " + device + str(minor))

		self.globalbox = gtk.VBox(gtk.FALSE, 0)
		self.globalbox.set_border_width(10)

		self.globalbox.pack_start(gtk.Label("Partition properties dialog"), expand=gtk.FALSE, fill=gtk.FALSE, padding=0)

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
