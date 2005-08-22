# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.

import gtk
import GLIScreen
import GLIUtility

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
		vert.pack_start(hbox, expand=False, fill=False, padding=10)
		self.radio_stages[2] = gtk.RadioButton(self.radio_stages[1], "Stage 2")
		self.radio_stages[2].set_name("2")
		self.radio_stages[2].connect("toggled", self.stage_selected, "2")
		self.radio_stages[2].set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.radio_stages[2], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("Most of the system will be compiled with your CHOST and CFLAGS settings. Don't use this option unless you have a good reason")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=10)

		self.radio_stages[3] = gtk.RadioButton(self.radio_stages[1], "Stage 3")
		self.radio_stages[3].set_name("3")
		self.radio_stages[3].connect("toggled", self.stage_selected, "3")
		self.radio_stages[3].set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.radio_stages[3], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("The base system will be installed using precompiled packages. You can recompile later with your custom settings if you choose. This is the fastest option")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=10)

		self.check_grp = gtk.CheckButton("GRP Install")
		self.check_grp.set_sensitive(False)
		self.check_grp.set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.check_grp, expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("Any extra packages installed (beyond the stage3) will be installed using binaries from the LiveCD that you are installing from")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=10)

		self.check_dynamic = gtk.CheckButton("Dynamic")
		self.check_dynamic.set_sensitive(False)
		self.check_dynamic.connect("toggled", self.dynamic_checked)
		self.check_dynamic.set_size_request(100, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.check_dynamic, expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("The stage3 will be generated from the packages on the LiveCD")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=10)

		hbox = gtk.HBox(False, 0)
		hbox.pack_start(gtk.Label("Stage tarball URI:"), expand=False, fill=False, padding=5)
		self.entry_stage_tarball_uri = gtk.Entry()
		self.entry_stage_tarball_uri.set_width_chars(50)
		hbox.pack_start(self.entry_stage_tarball_uri, expand=False, fill=False, padding=10)
		vert.pack_end(hbox, expand=False, fill=False, padding=0)

		self.add_content(vert)

	def stage_selected(self, widget, data=None):
		self.active_selection = int(data)
		self.entry_stage_tarball_uri.set_sensitive(True)
		if int(data) == 3:
			self.check_grp.set_sensitive(True)
			self.check_dynamic.set_sensitive(True)
			if self.check_dynamic.get_active():
				self.entry_stage_tarball_uri.set_sensitive(False)
		else:
			self.check_grp.set_sensitive(False)
			self.check_dynamic.set_sensitive(False)

	def dynamic_checked(self, widget):
		if widget.get_active() and self.active_selection == 3:
			self.entry_stage_tarball_uri.set_sensitive(False)
		else:
			self.entry_stage_tarball_uri.set_sensitive(True)

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
		self.check_dynamic.set_active(self.controller.install_profile.get_dynamic_stage3())

	def deactivate(self):
		if not self.check_dynamic.get_active():
			if not self.entry_stage_tarball_uri.get_text():
				msgdlg = gtk.MessageDialog(parent=self.controller.window, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format="You did not enter a stage tarball URI. Continue?")
				resp = msgdlg.run()
				msgdlg.destroy()
				if resp == gtk.RESPONSE_NO:
					return False
			elif not GLIUtility.validate_uri(self.entry_stage_tarball_uri.get_text()):
				msgdlg = gtk.MessageDialog(parent=self.controller.window, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format="The stage tarball URI you entered does not exist. Continue?")
				resp = msgdlg.run()
				msgdlg.destroy()
				if resp == gtk.RESPONSE_NO:
					return False
		self.controller.install_profile.set_install_stage(None, self.active_selection, None)
		if self.active_selection == 3:
			self.controller.install_profile.set_grp_install(None, self.check_grp.get_active(), None)
			self.controller.install_profile.set_dynamic_stage3(None, self.check_dynamic.get_active(), None)
		else:
			self.controller.install_profile.set_grp_install(None, False, None)
		try: self.controller.install_profile.set_stage_tarball_uri(None, self.entry_stage_tarball_uri.get_text(), None)
		except: pass
		return True
