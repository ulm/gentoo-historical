# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.

import gtk
import gobject
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = "Bootloader"
	active_selection = None
	install_in_mbr = True
	boot_loaders = {}

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(False, 0)
		vert.set_border_width(10)

		content_str = """Here, you will select which bootloader you would like to use. Each option has
a brief description beside it.
"""
		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=False, fill=False, padding=0)

		self.boot_loaders['grub'] = gtk.RadioButton(None, "grub")
		self.boot_loaders['grub'].set_name("grub")
		self.boot_loaders['grub'].connect("toggled", self.loader_selected, "grub")
		self.boot_loaders['grub'].set_size_request(125, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.boot_loaders['grub'], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("This is the more popular bootloader. If you are installing on AMD64, this is your only choice")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=20)

		self.boot_loaders['lilo'] = gtk.RadioButton(self.boot_loaders['grub'], "lilo")
		self.boot_loaders['lilo'].set_name("lilo")
		self.boot_loaders['lilo'].connect("toggled", self.loader_selected, "lilo")
		self.boot_loaders['lilo'].set_size_request(125, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.boot_loaders['lilo'], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("This bootloader isn't as flexible as grub, but some people still prefer it")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=15)

		self.boot_loaders['none'] = gtk.RadioButton(self.boot_loaders['grub'], "None")
		self.boot_loaders['none'].set_name("none")
		self.boot_loaders['none'].connect("toggled", self.loader_selected, "none")
		self.boot_loaders['none'].set_size_request(125, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.boot_loaders['none'], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("Choose this if you don't want a bootloader installed")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=15)

		self.check_install_in_mbr = gtk.CheckButton("Install in MBR")
		self.check_install_in_mbr.connect("toggled", self.mbr_selected)
		self.check_install_in_mbr.set_size_request(125, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.check_install_in_mbr, expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("This controls whether the bootloader is installed in the MBR or not")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=15)

		hbox = gtk.HBox(False, 0)
		tmplabel = gtk.Label("Boot Drive:")
		tmplabel.set_alignment(0.0, 0.5)
		tmplabel.set_size_request(160, -1)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=0)
#		self.boot_device_data = gtk.ListStore(gobject.TYPE_STRING)
#		self.boot_device_combo = gtk.ComboBox(self.boot_drive_data)
		self.boot_device_combo = gtk.combo_box_new_text()
		hbox.pack_start(self.boot_device_combo, expand=False, fill=False, padding=15)
		vert.pack_start(hbox, expand=False, fill=False, padding=15)

		hbox = gtk.HBox(False, 0)
		tmplabel = gtk.Label("Extra kernel parameters:")
		tmplabel.set_alignment(0.0, 0.5)
		tmplabel.set_size_request(160, -1)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=0)
		self.kernel_params_entry = gtk.Entry()
		self.kernel_params_entry.set_width_chars(40)
		hbox.pack_start(self.kernel_params_entry, expand=False, fill=False, padding=15)
		vert.pack_start(hbox, expand=False, fill=False, padding=15)

		self.add_content(vert)
		self.boot_devices = None

	def loader_selected(self, widget, data=None):
		self.active_selection = data

	def mbr_selected(self, widget, data=None):
		if self.check_install_in_mbr.get_active():
			self.boot_device_combo.set_sensitive(True)
		else:
			self.boot_device_combo.set_sensitive(False)

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = True
		self.controller.SHOW_BUTTON_HELP    = True
		self.controller.SHOW_BUTTON_BACK    = True
		self.controller.SHOW_BUTTON_FORWARD = True
		self.controller.SHOW_BUTTON_FINISH  = False
		self.active_selection = self.controller.install_profile.get_boot_loader_pkg() or "grub"
		self.boot_loaders[self.active_selection].set_active(True)
		self.check_install_in_mbr.set_active(self.install_in_mbr)
		self.boot_devices = self.controller.install_profile.get_partition_tables().keys()
		self.boot_devices.sort()
		self.boot_device_combo.get_model().clear()
		boot_device = self.controller.install_profile.get_boot_device()
		for i, device in enumerate(self.boot_devices):
			self.boot_device_combo.get_model().append([device])
			if boot_device == device:
				self.boot_device_combo.set_active(i)
		if self.boot_device_combo.get_active() == -1:
			self.boot_device_combo.set_active(0)

	def deactivate(self):
		self.controller.install_profile.set_boot_loader_pkg(None, self.active_selection, None)
		self.controller.install_profile.set_boot_loader_mbr(None, self.check_install_in_mbr.get_active(), None)
		if self.check_install_in_mbr.get_active():
			self.controller.install_profile.set_boot_device(None, self.boot_devices[self.boot_device_combo.get_active()], None)
		self.controller.install_profile.set_bootloader_kernel_args(None, self.kernel_params_entry.get_text(), None)
		return True
