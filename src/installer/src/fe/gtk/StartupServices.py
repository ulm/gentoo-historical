# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.

import gtk
import GLIScreen
from gettext import gettext as _

class Panel(GLIScreen.GLIScreen):

	title = _("Startup Services")

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(False, 0)
		vert.set_border_width(10)

		content = """
On this screen, you can select services that you would like to startup at boot.
Common choices are sshd (remote access) and xdm (graphical login...choose this
for kdm, gdm, and entrance, as well). Adding a service here does not
automatically emerge the corresponding package. You will need to add it on the
Extra Packages screen yourself.
"""
		content_label = gtk.Label(content)
		vert.pack_start(content_label, expand=False, fill=False, padding=0)

		self.add_content(vert)

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = True
		self.controller.SHOW_BUTTON_HELP    = True
		self.controller.SHOW_BUTTON_BACK    = True
		self.controller.SHOW_BUTTON_FORWARD = True
		self.controller.SHOW_BUTTON_FINISH  = False
