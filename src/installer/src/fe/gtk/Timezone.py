import gtk
import GLIScreen
import os
import string
import timezone_map_gui
import zonetab
from Widgets import Widgets

class Panel(GLIScreen.GLIScreen):
	"""
	The Timezone section of the installer.
	
	@author:    John N. Laliberte <allanonjl@gentoo.org>
	@license:   GPL
	"""
	# Attributes:
	title="Timezone"
	# Operations
	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)

		vert    = gtk.VBox(False, 10) # This box is content so it should fill space to force title to top
		horiz   = gtk.HBox(False, 10)
			
		self.zonetab2 = zonetab.ZoneTab()
		self.map = timezone_map_gui.TimezoneMap(self.zonetab2)

		vert.pack_start(self.map, expand=True, fill=True, padding=5)
		
		self.add_content(vert)
		self.show_all()

	def activate(self):
		# grab from the install profile, and if its not blank, create it
		try:
			loaded = self.controller.install_profile.get_time_zone()
			if loaded:
				if loaded.beginswith("/usr/share/zoneinfo/"):
					# strip the path /usr/share/zoneinfo/
					loaded = loaded[20:]
				zonetab_entry = self.zonetab2.findEntryByTZ(loaded)
				self.map.setCurrent(zonetab_entry)
		except:
			# this isn't a valid timezone entry, or its not set!
			print "Invalid timezone or timezone not set."
			
		self.controller.SHOW_BUTTON_EXIT    = True
		self.controller.SHOW_BUTTON_HELP    = True
		self.controller.SHOW_BUTTON_BACK    = True
		self.controller.SHOW_BUTTON_FORWARD = True
		self.controller.SHOW_BUTTON_FINISH  = False
		
	def deactivate(self):
		try:
			# retrieve the current selected timezone
#			final_path = "/usr/share/zoneinfo/" + self.map.getCurrent().tz
#			self.controller.install_profile.set_time_zone(None, final_path, None)
			self.controller.install_profile.set_time_zone(None, self.map.getCurrent().tz, None)
		except:
			# page loading for the first time, no timezone is selected for
			# NoneType
			pass
		
		return True
