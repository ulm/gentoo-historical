import gtk
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = "Stage Selection"
	active_selection = 1
	radio_stages = [None, None, None, None]

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(gtk.FALSE, 0)
		vert.set_border_width(10)

		content_str = """Here, you will select which stage you would like to start your install from.
Each option has a brief description beside it.
"""
		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)            
		self.radio_stages[1] = gtk.RadioButton(None, "Stage 1")
		self.radio_stages[1].set_name("1")
		self.radio_stages[1].connect("toggled", self.stage_selected, "1")
		self.radio_stages[1].set_size_request(100, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.radio_stages[1], expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("The entire system will be compiled from scratch with your CHOST and CFLAGS settings"), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		self.radio_stages[2] = gtk.RadioButton(self.radio_stages[1], "Stage 2")
		self.radio_stages[2].set_name("2")
		self.radio_stages[2].connect("toggled", self.stage_selected, "2")
		self.radio_stages[2].set_size_request(100, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.radio_stages[2], expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("Most of the system will be compiled with your CHOST and CFLAGS settings. Don't use\nthis option unless you have a good reason"), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		self.radio_stages[3] = gtk.RadioButton(self.radio_stages[1], "Stage 3")
		self.radio_stages[3].set_name("3")
		self.radio_stages[3].connect("toggled", self.stage_selected, "3")
		self.radio_stages[3].set_size_request(100, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.radio_stages[3], expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("The base system will be installed using precompiled packages. You can recompile later\nwith your custom settings if you choose. This is the fastest option"), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(gtk.Label("Stage tarball URI:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		self.entry_stage_tarball_uri = gtk.Entry()
		self.entry_stage_tarball_uri.set_width_chars(50)
		hbox.pack_start(self.entry_stage_tarball_uri, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=40)

		self.add_content(vert)

	def stage_selected(self, widget, data=None):
		self.active_selection = int(data)

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
		self.active_selection = int(self.controller.install_profile.get_install_stage()) or 1
		self.radio_stages[self.active_selection].set_active(gtk.TRUE)
		self.entry_stage_tarball_uri.set_text(self.controller.install_profile.get_stage_tarball_uri())

	def deactivate(self):
		self.controller.install_profile.set_install_stage(None, self.active_selection, None)
		try: self.controller.install_profile.set_stage_tarball_uri(None, self.entry_stage_tarball_uri.get_text(), None)
		except: pass
		return True
