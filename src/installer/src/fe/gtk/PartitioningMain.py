import gtk
import GLIScreen
import Partitioning
import PartitioningUgly

class Panel(GLIScreen.GLIScreen):

	title = "Partitioning"
	active_page = -1

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(False, 0)
		vert.set_border_width(10)

		self.notebook = gtk.Notebook()
		self.notebook.append_page(Partitioning.Panel(self.controller, self))
		self.notebook.append_page(PartitioningUgly.Panel(self.controller))
		self.notebook.set_show_tabs(False)
		self.notebook.set_show_border(False)
		vert.pack_start(self.notebook, expand=True, fill=True, padding=0)

		choices_hbox = gtk.HBox(False, 0)
		self.radio_pretty = gtk.RadioButton(group=None, label="Pretty")
		self.radio_pretty.connect("toggled", self.switch_screen, 0)
		choices_hbox.pack_start(self.radio_pretty, expand=False, fill=False, padding=0)
		self.radio_ugly = gtk.RadioButton(group=self.radio_pretty, label="Ugly")
		self.radio_ugly.connect("toggled", self.switch_screen, 1)
		choices_hbox.pack_start(self.radio_ugly, expand=False, fill=False, padding=15)
		vert.pack_end(choices_hbox, expand=False, fill=False, padding=0)

		self.add_content(vert)

	def switch_screen(self, widget, data=None):
#		print "data=" + str(data) + ", active_page=" + str(self.active_page)
		if widget and not widget.get_active(): return
		if not self.active_page == data:
			self.active_page = data
			self.notebook.set_current_page(data)
			self.notebook.get_nth_page(data).activate()

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = True
		self.controller.SHOW_BUTTON_HELP    = True
		self.controller.SHOW_BUTTON_BACK    = True
		self.controller.SHOW_BUTTON_FORWARD = True
		self.controller.SHOW_BUTTON_FINISH  = False
#		self.notebook.hide_all()
		if self.active_page == -1:
			self.switch_screen(None, 0)
		else:
			self.switch_screen(None, self.active_page)
#		self.notebook.show_all()

	def deactivate(self):
		return self.notebook.get_nth_page(self.notebook.get_current_page()).deactivate()
