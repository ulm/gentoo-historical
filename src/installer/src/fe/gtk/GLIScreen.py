import gtk
import os.path

class GLIScreen(gtk.VBox):

	full_path = ""

	def __init__(self, controller):
		self.controller = controller
		self.full_path = os.path.abspath(os.path.dirname(__file__))

		gtk.VBox.__init__(self, gtk.FALSE, 0)
		right_title_label = gtk.Label()
		right_title_label.set_markup('<span><b>'+self.title+'</b></span>')
		right_title_label.set_use_markup(gtk.TRUE)
		self.pack_start(right_title_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

	def add_content(self, content):
		self.pack_end(content, gtk.TRUE, gtk.TRUE, 0)

	def activate(self):
		pass
