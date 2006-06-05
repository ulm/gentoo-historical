# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.

import gtk
import GLIScreen
from gettext import gettext as _

class Panel(GLIScreen.GLIScreen):

	title = _("Welcome to the Gentoo Linux Installer")
	_helptext = """
<b><u>Welcome screen</u></b>

This screen is fairly straightforward. It welcomes you to the Installer and
gives you one option. The "Standard" mode is used for networked installs. It
allows you the most flexibility. The "Networkless" mode removes some options
from subsequent screens and sets a few useful defaults.
"""

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(False, 10)
		vert.set_border_width(10)

		content_str = _("""
Welcome to the GTK+ front-end for the Gentoo Linux Installer.

It is highly recommended that you have gone through the manual install process a time
or two, or at least read through the install guide. The purpose of this installer is
not to make the install easier but to make it quicker. Don't ask questions that are
covered by the install guide, or we shall taunt you a second time.

In this part of the installer, you will make all of your decisions for how you want
your system setup. No changes will be made to your system until you click the
"Install" button. At any point before you click "Install", you can click "Save" to
save your install profile and come back at a later time to finish.

If you have installed Gentoo Linux previously using this installer and you saved
your configuration settings (install profile), you can click the "Load" button to
load your previous settings as defaults.""")

		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=False, fill=False, padding=0)

		hbox = gtk.HBox(False, 0)
		hbox.pack_start(gtk.Label("Install type:"), expand=False, fill=False, padding=10)
		self.install_type_standard = gtk.RadioButton(label=_("Standard"))
		hbox.pack_start(self.install_type_standard, expand=False, fill=False, padding=15)
		self.install_type_networkless = gtk.RadioButton(group=self.install_type_standard, label=_("Networkless"))
		hbox.pack_start(self.install_type_networkless, expand=False, fill=False, padding=0)
		hbox2 = gtk.HBox(True, 0)
		hbox2.pack_start(hbox, expand=False, fill=False, padding=0)
		vert.pack_start(hbox2, expand=False, fill=False, padding=20)

		self.add_content(vert)

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = True
		self.controller.SHOW_BUTTON_HELP    = True
		self.controller.SHOW_BUTTON_BACK    = False
		self.controller.SHOW_BUTTON_FORWARD = True
		self.controller.SHOW_BUTTON_FINISH  = False

	def deactivate(self):
		if self.install_type_standard.get_active():
			self.controller.install_type = "standard"
		elif self.install_type_networkless.get_active():
			self.controller.install_type = "networkless"
		return True
