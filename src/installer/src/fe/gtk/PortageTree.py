import gtk
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = "Portage Tree"
	active_selection = 1
	radio_syncs = {}

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(gtk.FALSE, 0)
		vert.set_border_width(10)

		content_str = """Here, you will select how you would like to obtain a portage tree. Each option has
a brief description beside it.
"""
		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		self.radio_syncs['sync'] = gtk.RadioButton(None, "Normal")
		self.radio_syncs['sync'].set_name("sync")
		self.radio_syncs['sync'].connect("toggled", self.stage_selected, "sync")
		self.radio_syncs['sync'].set_size_request(100, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.radio_syncs['sync'], expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("This will run 'emerge sync' to get a local copy of the portage tree"), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		self.radio_syncs['webrsync'] = gtk.RadioButton(self.radio_syncs['sync'], "Webrsync")
		self.radio_syncs['webrsync'].set_name("webrsync")
		self.radio_syncs['webrsync'].connect("toggled", self.stage_selected, "webrsync")
		self.radio_syncs['webrsync'].set_size_request(100, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.radio_syncs['webrsync'], expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("This will download a portage snapshot from a Gentoo mirror and sync it locally. Use\nthis option if you are behind a nazi-ish firewall that blocks outgoing rsync traffic"), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		self.radio_syncs['custom'] = gtk.RadioButton(self.radio_syncs['sync'], "None")
		self.radio_syncs['custom'].set_name("custom")
		self.radio_syncs['custom'].connect("toggled", self.stage_selected, "custom")
		self.radio_syncs['custom'].set_size_request(100, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.radio_syncs['custom'], expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("Use this option to bypass syncing the tree. If you want to NFS mount the portage tree,\nuse this option"), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(gtk.Label("Portage snapshot URI:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		self.entry_portage_snapshot_uri = gtk.Entry()
		self.entry_portage_snapshot_uri.set_width_chars(50)
		hbox.pack_start(self.entry_portage_snapshot_uri, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=40)

		self.add_content(vert)

	def stage_selected(self, widget, data=None):
		self.active_selection = data

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
		self.active_selection = self.controller.install_profile.get_portage_tree_sync_type() or "sync"
		self.radio_syncs[self.active_selection].set_active(gtk.TRUE)
		self.entry_portage_snapshot_uri.set_text(self.controller.install_profile.get_portage_tree_snapshot_uri())

	def deactivate(self):
		self.controller.install_profile.set_portage_tree_sync_type(None, self.active_selection, None)
		try: self.controller.install_profile.set_portage_tree_snapshot_uri(None, self.entry_portage_snapshot_uri.get_text(), None)
		except: pass
		return True
