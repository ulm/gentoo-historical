import gtk
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = "Stage Selection"
	active_selection = 1
	radio_stages = [None, None, None, None]

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(False, 0)
		vert.set_border_width(10)

		content_str = """Here, you will select which stage you would like to start your install from.
Each option has a brief description beside it.
"""
		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=False, fill=False, padding=0)            
		self.radio_stages[1] = gtk.RadioButton(None, "Stage 1")
		self.radio_stages[1].set_name("1")
		self.radio_stages[1].connect("toggled", self.stage_selected, "1")
		self.radio_stages[1].set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.radio_stages[1], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("The entire system will be compiled from scratch with your CHOST and CFLAGS settings")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=15)
		self.radio_stages[2] = gtk.RadioButton(self.radio_stages[1], "Stage 2")
		self.radio_stages[2].set_name("2")
		self.radio_stages[2].connect("toggled", self.stage_selected, "2")
		self.radio_stages[2].set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.radio_stages[2], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("Most of the system will be compiled with your CHOST and CFLAGS settings. Don't use this option unless you have a good reason")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=15)

		self.radio_stages[3] = gtk.RadioButton(self.radio_stages[1], "Stage 3")
		self.radio_stages[3].set_name("3")
		self.radio_stages[3].connect("toggled", self.stage_selected, "3")
		self.radio_stages[3].set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.radio_stages[3], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("The base system will be installed using precompiled packages. You can recompile later with your custom settings if you choose. This is the fastest option")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=15)

		self.check_grp = gtk.CheckButton("GRP Install")
		self.check_grp.set_sensitive(False)
		self.check_grp.set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.check_grp, expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("Any extra packages installed (beyond the stage3) will be installed using binaries from the LiveCD that you are installing from")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=20)

		hbox = gtk.HBox(False, 0)
		hbox.pack_start(gtk.Label("Stage tarball URI:"), expand=False, fill=False, padding=5)
		self.entry_stage_tarball_uri = gtk.Entry()
		self.entry_stage_tarball_uri.set_width_chars(50)
		hbox.pack_start(self.entry_stage_tarball_uri, expand=False, fill=False, padding=10)
		vert.pack_start(hbox, expand=False, fill=False, padding=30)

		self.add_content(vert)

	def stage_selected(self, widget, data=None):
		self.active_selection = int(data)
		if int(data) == 3:
			self.check_grp.set_sensitive(True)
		else:
			self.check_grp.set_sensitive(False)

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = True
		self.controller.SHOW_BUTTON_HELP    = True
		self.controller.SHOW_BUTTON_BACK    = True
		self.controller.SHOW_BUTTON_FORWARD = True
		self.controller.SHOW_BUTTON_FINISH  = False
		self.active_selection = int(self.controller.install_profile.get_install_stage()) or 1
		self.radio_stages[self.active_selection].set_active(True)
		self.entry_stage_tarball_uri.set_text(self.controller.install_profile.get_stage_tarball_uri())
		self.check_grp.set_active(self.controller.install_profile.get_grp_install())

	def deactivate(self):
		self.controller.install_profile.set_install_stage(None, self.active_selection, None)
		if self.active_selection == 3:
			self.controller.install_profile.set_grp_install(None, self.check_grp.get_active(), None)
		else:
			self.controller.install_profile.set_grp_install(None, False, None)
		try: self.controller.install_profile.set_stage_tarball_uri(None, self.entry_stage_tarball_uri.get_text(), None)
		except: pass
		return True
