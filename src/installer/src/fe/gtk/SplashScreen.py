# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.

import gtk

class SplashScreen(gtk.Window):

	def __init__(self, fullpath):
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

		self.connect("delete_event", self.delete_event)
		self.connect("destroy", self.destroy_event)
		self.set_default_size(400,240)
		self.set_decorated(False)

		image = gtk.Image()
		image.set_from_file(fullpath + "/installer-splash.png")
		image.show()
		self.add(image)
		self.show()
		self.present()

	def delete_event(self, widget, event, data=None):
		return False

	def destroy_event(self, widget, data=None):
		return True
