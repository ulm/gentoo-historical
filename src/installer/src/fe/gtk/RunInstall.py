#!/usr/bin/python

import GLIInstallProfile
import GLIClientConfiguration
import GLIClientController
import GLIUtility
import gtk
import gobject
import sys
import time
import os
import select

class RunInstall(gtk.Window):

	which_step = 0
	install_done = False

	def __init__(self, controller):
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

		self.controller = controller
		self.connect("delete_event", self.delete_event)
		self.connect("destroy", self.destroy)
		self.set_default_size(800,600)
		self.set_geometry_hints(None, min_width=800, min_height=600, max_width=800, max_height=600)
		self.set_title("Gentoo Linux Installer")

		self.globalbox = gtk.VBox(False, 0)
		self.globalbox.set_border_width(10)

		self.notebook = gtk.Notebook()

		self.tailpage = gtk.VBox(False, 0)
		self.textbuffer = gtk.TextBuffer()
		self.textbuffer.set_text("testing\ntesting again..\n\ntesting testing")
		self.textview = gtk.TextView(self.textbuffer)
		self.textview.set_editable(False)
		self.tailpage.pack_start(self.textview, expand=True, fill=True)
		self.notebook.append_page(self.tailpage, tab_label=gtk.Label("Output"))

		self.docpage = gtk.VBox(False, 0)
		# documentation
		self.notebook.append_page(self.docpage, tab_label=gtk.Label("Documentation"))

		self.globalbox.add(self.notebook)

		self.progress = gtk.ProgressBar()
		self.progress.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
		self.progress.set_text("Preparing...")
		self.globalbox.pack_end(self.progress, expand=False, fill=False, padding=10)

		self.add(self.globalbox)
		self.make_visible()

		self.controller.cc.set_install_profile(self.controller.install_profile)
		self.controller.cc.start_install()

		self.output_log = None
#os.popen("tail -F /tmp/compile_output.log 2>&1")
		gobject.timeout_add(1000, self.poll_notifications)
		gobject.timeout_add(1000, self.tail_logfile)

	def poll_notifications(self):
		if self.install_done: return False
		notification = self.controller.cc.getNotification()
		if notification == None:
			return True
		ntype = notification.get_type()
		ndata = notification.get_data()
		if ntype == "exception":
			msgdlg = gtk.MessageDialog(parent=self, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK, message_format="An error occured during the install. Consult the output display for more information.")
			msgdlg.run()
			msgdlg.destroy()
			print "Exception received:"
			print ndata
		elif ntype == "int":
			if ndata == GLIClientController.NEXT_STEP_READY:
				num_steps = self.controller.cc.get_num_steps()
				if self.controller.cc.has_more_steps():
					next_step = self.controller.cc.get_next_step_info()
					print "Next step: " + next_step
					self.progress.set_fraction(round(float(self.which_step)/num_steps, 2))
					self.progress.set_text(self.controller.cc.get_next_step_info())
					self.which_step += 1
					self.controller.cc.next_step()
				return True
			if ndata == GLIClientController.INSTALL_DONE:
				self.install_done = True
				self.progress.set_fraction(1)
				self.progress.set_text("Install complete!")
				print "Install done!"
				msgdlg = gtk.MessageDialog(parent=self, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK, message_format="Install completed successfully!")
				msgdlg.run()
				msgdlg.destroy()
				return False

	def tail_logfile(self):
		if self.install_done:
			self.output_log.close()
			return False
		if not self.output_log:
			try:
				self.output_log = open("/tmp/compile_output.log")
			except:
				return True
#		if select.select([self.output_log], [], [], 0)[0]:
		while 1:
			line = self.output_log.readline()
			if not line: break
			iter_end = self.textbuffer.get_iter_at_offset(-1)
			self.textbuffer.insert(iter_end, line, -1)
			self.textview.scroll_to_iter(iter_end, 0.0)

		return True

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
		return False

	# Destroy callback
	def destroy(self, widget, data=None):
		print "destroy function"
		gtk.main_quit()
		return True
