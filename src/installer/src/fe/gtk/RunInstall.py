#!/usr/bin/python

import GLIInstallProfile
import GLIClientConfiguration
import GLIClientController
import GLIUtility
import gtk
import gobject
import sys
import time
import threading

class RunInstall(gtk.Window):

	which_step = 0

	def __init__(self, controller):
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

		self.controller = controller
		self.connect("delete_event", self.delete_event)
		self.connect("destroy", self.destroy)
		self.set_default_size(800,600)
		self.set_geometry_hints(None, min_width=800, min_height=600, max_width=800, max_height=600)
		self.set_title("Gentoo Linux Installer")

		self.globalbox = gtk.VBox(gtk.FALSE, 0)
		self.globalbox.set_border_width(10)

		self.notebook = gtk.Notebook()
		self.tailpage = gtk.VBox(gtk.FALSE, 0)
		self.notebook.append_page(self.tailpage, tab_label=gtk.Label("Output"))
		self.docpage = gtk.VBox(gtk.FALSE, 0)
		self.notebook.append_page(self.docpage, tab_label=gtk.Label("Documentation"))
		self.globalbox.add(self.notebook)

		self.progress = gtk.ProgressBar()
		self.progress.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
		self.progress.set_text("Preparing...")
		self.globalbox.pack_end(self.progress, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

		self.add(self.globalbox)
		self.make_visible()

		self.controller.cc.set_install_profile(self.controller.install_profile)
		self.controller.cc.start_install()
#		gobject.timeout_add(1000, self.poll_notifications)
		gobject.idle_add(self.poll_notifications)

	def poll_notifications(self):
		notification = self.controller.cc.getNotification()
		if notification == None:
			return True
		type = notification.get_type()
		data = notification.get_data()
		if type == "exception":
			print "Exception received:"
			print data
		elif type == "int":
			if data == GLIClientController.NEXT_STEP_READY:
				num_steps = self.controller.cc.get_num_steps()
				if self.controller.cc.has_more_steps():
					next_step = self.controller.cc.get_next_step_info()
					print "Next step: " + next_step
					self.progress.set_fraction(round(float(self.which_step)/num_steps, 2))
					self.progress.set_text(self.controller.cc.get_next_step_info())
					self.which_step += 1
					time.sleep(1)
					self.controller.cc.next_step()
				return True
			if data == GLIClientController.INSTALL_DONE:
				self.progress.set_fraction(1)
				self.progress.set_text("Install complete!")
				print "Install done!"
				return False

	def make_visible(self):
		self.show_all()
		self.present()

	def make_invisible(self):
		self.hide_all()

	def delete_event(self, widget, event, data=None):
		# If you return FALSE in the "delete_event" signal handler,
		# GTK will emit the "destroy" signal. Returning TRUE means
		# you don't want the window to be destroyed.
		# This is useful for popping up 'are you sure you want to quit?'
		# type dialogs.
		print "delete event occurred"
		# Change TRUE to FALSE and the main window will be destroyed with
		# a "delete_event".
		return gtk.FALSE

	# Destroy callback
	def destroy(self, widget, data=None):
		print "destroy function"
		gtk.main_quit()
		return gtk.TRUE
