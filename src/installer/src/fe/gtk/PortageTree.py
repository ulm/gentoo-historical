import gtk
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = "Portage Tree"
	active_selection = None
	radio_syncs = {}

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(False, 0)
		vert.set_border_width(10)

		content_str = """Here, you will select how you would like to obtain a portage tree. Each option has
a brief description beside it.
"""
		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=False, fill=False, padding=0)
		self.radio_syncs['sync'] = gtk.RadioButton(None, "Normal")
		self.radio_syncs['sync'].set_name("sync")
		self.radio_syncs['sync'].connect("toggled", self.stage_selected, "sync")
		self.radio_syncs['sync'].set_size_request(100, -1)
#		self.radio_syncs['sync'].set_sensitive(False) # temporary
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.radio_syncs['sync'], expand=False, fill=False, padding=5)
		hbox.pack_start(gtk.Label("This will run 'emerge sync' to get a local copy of the portage tree (temporarily disabled)"), expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=20)
		self.radio_syncs['webrsync'] = gtk.RadioButton(self.radio_syncs['sync'], "Webrsync")
		self.radio_syncs['webrsync'].set_name("webrsync")
		self.radio_syncs['webrsync'].connect("toggled", self.stage_selected, "webrsync")
		self.radio_syncs['webrsync'].set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.radio_syncs['webrsync'], expand=False, fill=False, padding=5)
		hbox.pack_start(gtk.Label("This will download a portage snapshot from a Gentoo mirror and sync it locally. Use\nthis option if you are behind a nazi-ish firewall that blocks outgoing rsync traffic"), expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=20)
		self.radio_syncs['snapshot'] = gtk.RadioButton(self.radio_syncs['sync'], "Snapshot")
		self.radio_syncs['snapshot'].set_name("snapshot")
		self.radio_syncs['snapshot'].connect("toggled", self.stage_selected, "snapshot")
		self.radio_syncs['snapshot'].set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.radio_syncs['snapshot'], expand=False, fill=False, padding=5)
		hbox.pack_start(gtk.Label("Use this option to if you have a portage snapshot."), expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=20)
		self.radio_syncs['none'] = gtk.RadioButton(self.radio_syncs['sync'], "None")
		self.radio_syncs['none'].set_name("none")
		self.radio_syncs['none'].connect("toggled", self.stage_selected, "none")
		self.radio_syncs['none'].set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.radio_syncs['none'], expand=False, fill=False, padding=5)
		hbox.pack_start(gtk.Label("This option leaves /usr/portage untouched. Use this if\nyou are NFS mounting the tree."), expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=20)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(gtk.Label("Portage snapshot URI:"), expand=False, fill=False, padding=5)
		self.entry_portage_snapshot_uri = gtk.Entry()
		self.entry_portage_snapshot_uri.set_width_chars(50)
		self.entry_portage_snapshot_uri.set_sensitive(False)
		hbox.pack_start(self.entry_portage_snapshot_uri, expand=False, fill=False, padding=10)
		vert.pack_start(hbox, expand=False, fill=False, padding=40)

		self.add_content(vert)

	def stage_selected(self, widget, data=None):
		self.active_selection = data
		if data == "snapshot":
			self.entry_portage_snapshot_uri.set_sensitive(True)
		else:
			self.entry_portage_snapshot_uri.set_sensitive(False)

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = True
		self.controller.SHOW_BUTTON_HELP    = True
		self.controller.SHOW_BUTTON_BACK    = True
		self.controller.SHOW_BUTTON_FORWARD = True
		self.controller.SHOW_BUTTON_FINISH  = False
		self.active_selection = self.controller.install_profile.get_portage_tree_sync_type() or "sync"
#		if self.active_selection == "sync": self.active_selection = "webrsync" # temporary
		self.radio_syncs[self.active_selection].set_active(True)
		self.entry_portage_snapshot_uri.set_text(self.controller.install_profile.get_portage_tree_snapshot_uri())

	def deactivate(self):
		self.controller.install_profile.set_portage_tree_sync_type(None, self.active_selection, None)
		try: self.controller.install_profile.set_portage_tree_snapshot_uri(None, self.entry_portage_snapshot_uri.get_text(), None)
		except: pass
		return True
