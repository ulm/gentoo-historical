import gtk
import GLIScreen
import Partitioning
import PartitioningUgly

class Panel(GLIScreen.GLIScreen):

	title = "Partitioning"
	active_page = 0

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(gtk.FALSE, 0)
		vert.set_border_width(10)

		self.notebook = gtk.Notebook()
		self.notebook.append_page(Partitioning.Panel(self.controller))
		self.notebook.append_page(PartitioningUgly.Panel(self.controller))
		self.notebook.set_show_tabs(gtk.FALSE)
		self.notebook.set_show_border(gtk.FALSE)
		vert.pack_start(self.notebook, expand=gtk.TRUE, fill=gtk.TRUE, padding=0)

		choices_hbox = gtk.HBox(gtk.FALSE, 0)
		self.radio_pretty = gtk.RadioButton(group=None, label="Pretty")
		self.radio_pretty.connect("toggled", self.switch_screen, 0)
		choices_hbox.pack_start(self.radio_pretty, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		self.radio_ugly = gtk.RadioButton(group=self.radio_pretty, label="Ugly")
		self.radio_ugly.connect("toggled", self.switch_screen, 1)
		choices_hbox.pack_start(self.radio_ugly, expand=gtk.FALSE, fill=gtk.FALSE, padding=15)
		vert.pack_end(choices_hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)

		self.add_content(vert)

	def switch_screen(self, widget, data=None):
		self.notebook.set_current_page(data)
		self.notebook.get_nth_page(data).activate()
		self.active_page = data

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
		self.switch_screen(self.notebook, self.active_page)
