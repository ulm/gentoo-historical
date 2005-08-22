# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.

import gtk
import GLIScreen
import GLIUtility

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
		tmplabel = gtk.Label("This will run 'emerge sync' to get a local copy of the portage tree")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=15)
		self.radio_syncs['webrsync'] = gtk.RadioButton(self.radio_syncs['sync'], "Webrsync")
		self.radio_syncs['webrsync'].set_name("webrsync")
		self.radio_syncs['webrsync'].connect("toggled", self.stage_selected, "webrsync")
		self.radio_syncs['webrsync'].set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.radio_syncs['webrsync'], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("This will download a portage snapshot from a Gentoo mirror and sync it locally. Use this option if you are behind a restrictive firewall that blocks outgoing rsync traffic")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=15)
		self.radio_syncs['snapshot'] = gtk.RadioButton(self.radio_syncs['sync'], "Snapshot")
		self.radio_syncs['snapshot'].set_name("snapshot")
		self.radio_syncs['snapshot'].connect("toggled", self.stage_selected, "snapshot")
		self.radio_syncs['snapshot'].set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.radio_syncs['snapshot'], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("Use this option to if you have a portage snapshot. You will need to enter the URI below")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=15)
		self.radio_syncs['none'] = gtk.RadioButton(self.radio_syncs['sync'], "None")
		self.radio_syncs['none'].set_name("none")
		self.radio_syncs['none'].connect("toggled", self.stage_selected, "none")
		self.radio_syncs['none'].set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.radio_syncs['none'], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("This option leaves /usr/portage untouched. Use this if you are NFS mounting the tree.")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=15)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(gtk.Label("Portage snapshot URI:"), expand=False, fill=False, padding=5)
		self.entry_portage_snapshot_uri = gtk.Entry()
		self.entry_portage_snapshot_uri.set_width_chars(50)
		self.entry_portage_snapshot_uri.set_sensitive(False)
		hbox.pack_start(self.entry_portage_snapshot_uri, expand=False, fill=False, padding=10)
		vert.pack_start(hbox, expand=False, fill=False, padding=30)

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
		if self.controller.install_profile.get_dynamic_stage3():
			self.entry_portage_snapshot_uri.set_text(GLIUtility.get_cd_snapshot_uri())
			self.radio_syncs["snapshot"].set_active(True)
			self.active_selection = "snapshot"
			for radio in self.radio_syncs:
				self.radio_syncs[radio].set_sensitive(False)
			self.entry_portage_snapshot_uri.set_sensitive(False)
		else:
			self.active_selection = self.controller.install_profile.get_portage_tree_sync_type() or "sync"
			self.radio_syncs[self.active_selection].set_active(True)
			self.entry_portage_snapshot_uri.set_text(self.controller.install_profile.get_portage_tree_snapshot_uri())
			if not self.entry_portage_snapshot_uri.get_text():
				self.entry_portage_snapshot_uri.set_text(GLIUtility.get_cd_snapshot_uri())
			for radio in self.radio_syncs:
				self.radio_syncs[radio].set_sensitive(True)
			self.entry_portage_snapshot_uri.set_sensitive(True)

	def deactivate(self):
		if self.active_selection == "snapshot":
			if not self.entry_portage_snapshot_uri.get_text():
				msgdlg = gtk.MessageDialog(parent=self.controller.window, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format="You did not enter a portage snapshot URI. Continue?")
				resp = msgdlg.run()
				msgdlg.destroy()
				if resp == gtk.RESPONSE_NO:
					return False
			elif not GLIUtility.validate_uri(self.entry_portage_snapshot_uri.get_text()):
				msgdlg = gtk.MessageDialog(parent=self.controller.window, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format="The portage snapshot URI you entered does not exist. Continue?")
				resp = msgdlg.run()
				msgdlg.destroy()
				if resp == gtk.RESPONSE_NO:
					return False
		self.controller.install_profile.set_portage_tree_sync_type(None, self.active_selection, None)
		try: self.controller.install_profile.set_portage_tree_snapshot_uri(None, self.entry_portage_snapshot_uri.get_text(), None)
		except: pass
		return True
