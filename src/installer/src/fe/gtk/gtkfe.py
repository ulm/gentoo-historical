#!/usr/bin/python

import GLIInstallProfile
import GLIClientConfiguration
import GLIClientController
import GLIUtility
import gtk
import sys
import crypt
import random
import commands
import string
import copy
import signal
import time

import Welcome
import Partitioning
import Stage
import PortageTree
import MakeDotConf
import Kernel
import Bootloader
import Timezone
import Networking
import Daemons
import ExtraPackages
import RcDotConf
import Users
import InstallSummary

class Installer:

	SHOW_BUTTON_FINISH = 1
	SHOW_BUTTON_FORWARD = 1
	SHOW_BUTTON_BACK = 1
	SHOW_BUTTON_HELP = 1
	SHOW_BUTTON_EXIT = 1
	install_profile_xml_file = ""

	menuItems = [ { 'text': 'Welcome', 'module': Welcome },
                      { 'text': 'Partitioning', 'module': Partitioning },
                      { 'text': 'Network Mounts', 'module': Welcome },
                      { 'text': 'Stage', 'module': Stage },
                      { 'text': 'Portage tree', 'module': PortageTree },
                      { 'text': 'make.conf', 'module': MakeDotConf },
                      { 'text': 'Kernel', 'module': Kernel },
                      { 'text': 'Bootloader', 'module': Bootloader },
                      { 'text': 'Timezone', 'module': Timezone },
                      { 'text': 'Networking', 'module': Networking },
                      { 'text': 'Daemons', 'module': Daemons },
                      { 'text': 'Extra Packages', 'module': ExtraPackages },
                      { 'text': 'rc.conf', 'module': RcDotConf },
                      { 'text': 'Users', 'module': Users },
                      { 'text': 'Install!', 'module': InstallSummary }
                    ]

	def __init__(self):
		self.client_profile = GLIClientConfiguration.ClientConfiguration()
		self.install_profile = GLIInstallProfile.InstallProfile()
		self.cc = GLIClientController.GLIClientController(pretend=True)
		self.window = None
		self.panel = None
		self._cur_panel = 0
		self.__full_path = self.get_current_path()
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.title="Gentoo Linux Installer"
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		self.window.set_border_width(0)
		self.window.set_default_size(800,600)
		self.window.set_geometry_hints(None, min_width=800, min_height=600, max_width=800, max_height=600)
		self.window.set_title("Gentoo Linux Installer")
		self.globalbox = gtk.VBox(gtk.FALSE, 0)
		self.window.add(self.globalbox)
		self.headerbox = gtk.HBox(gtk.FALSE, 0)
		headerimg = gtk.Image()
		headerimg.set_from_file(self.__full_path + '/headernew.png')
		self.headerbox.add(headerimg)
		self.topbox = gtk.HBox(gtk.FALSE, 0)
		self.bottombox = gtk.HBox(gtk.FALSE, 0)
		self.globalbox.pack_start(self.headerbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		self.globalbox.pack_start(self.topbox, expand=gtk.TRUE, fill=gtk.TRUE, padding=5)
		self.globalbox.pack_end(self.bottombox, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		self.leftframe = gtk.Frame()
		self.rightframe = gtk.Frame()
		self.leftframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.rightframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.topbox.pack_start(self.leftframe, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		self.topbox.pack_end(self.rightframe, expand=gtk.TRUE, fill=gtk.TRUE, padding=5)
		self.globalbox.show_all();

		self.redraw_left_pane(firstrun=True)

		# Right frame contents
		self.panels = []
		self.right_pane_box = gtk.Notebook()
		for item in self.menuItems:
			if item['module'] == None: break
			panel = item['module'].Panel(self)
			self.panels.append(panel)
			self.right_pane_box.append_page(panel)
		self.right_pane_box.set_show_tabs(gtk.FALSE)
		self.right_pane_box.set_show_border(gtk.FALSE)
		self.rightframe.add(self.right_pane_box)

		# Bottom buttons
		self.backbutton = gtk.Button()
		self.backbuttonbox = gtk.HBox(gtk.FALSE, 0)
		self.backbuttonimg = gtk.Image()
		self.backbuttonimg.set_from_file(self.__full_path + '/button_images/stock_left.png')
		self.backbuttonbox.pack_start(self.backbuttonimg)
		self.backbutton_label = gtk.Label(" _Back ")
		self.backbuttonbox.pack_start(self.backbutton_label)
		self.backbutton_label.set_use_underline(gtk.TRUE)
		self.backbutton.add(self.backbuttonbox)

		# Creates a new button with the label "Forward".
		self.forwardbutton = gtk.Button()
		self.forwardbuttonbox = gtk.HBox(gtk.FALSE, 0)
		self.forwardbuttonimg = gtk.Image()
		self.forwardbuttonimg.set_from_file(self.__full_path + '/button_images/stock_right.png')
		self.forwardbuttonbox.pack_start(self.forwardbuttonimg)
		self.forwardbutton_label = gtk.Label(" _Forward ")
		self.forwardbuttonbox.pack_start(self.forwardbutton_label)
		self.forwardbutton_label.set_use_underline(gtk.TRUE)
		self.forwardbutton.add(self.forwardbuttonbox)

		# Creates a new button with the label "Show Help".
		self.helpbutton = gtk.Button()
		self.helpbuttonbox = gtk.HBox(gtk.FALSE, 0)
		self.helpbuttonimg = gtk.Image()
		self.helpbuttonimg.set_from_file(self.__full_path + '/button_images/stock_help.png')
		self.helpbuttonbox.pack_start(self.helpbuttonimg)
		self.helpbutton_label = gtk.Label(" _Show Help ")
		self.helpbuttonbox.pack_start(self.helpbutton_label)
		self.helpbutton_label.set_use_underline(gtk.TRUE)
		self.helpbutton.add(self.helpbuttonbox)

		# Creates a new button with the label "Exit".
		self.exitbutton = gtk.Button()
		self.exitbuttonbox = gtk.HBox(gtk.FALSE, 0)
		self.exitbuttonimg = gtk.Image()
		self.exitbuttonimg.set_from_file(self.__full_path + '/button_images/stock_exit.png')
		self.exitbuttonbox.pack_start(self.exitbuttonimg)
		self.exitbutton_label = gtk.Label(" _Exit ")
		self.exitbuttonbox.pack_start(self.exitbutton_label)
		self.exitbutton_label.set_use_underline(gtk.TRUE)
		self.exitbutton.add(self.exitbuttonbox)

		# Creates a new button with the label "Finish".
		self.finishbutton = gtk.Button()
		self.finishbuttonbox = gtk.HBox(gtk.FALSE, 0)
		self.finishbuttonimg = gtk.Image()
		self.finishbuttonimg.set_from_file(self.__full_path + '/button_images/stock_exit.png')
		self.finishbuttonbox.pack_start(self.finishbuttonimg)
		self.finishbutton_label = gtk.Label(" _Finish ")
		self.finishbuttonbox.pack_start(self.finishbutton_label)
		self.finishbutton_label.set_use_underline(gtk.TRUE)
		self.finishbutton.add(self.finishbuttonbox)

		# We pack in the buttons
		if self.SHOW_BUTTON_FINISH:
			self.bottombox.pack_end(self.finishbutton, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		if self.SHOW_BUTTON_FORWARD:
			self.bottombox.pack_end(self.forwardbutton, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		if self.SHOW_BUTTON_BACK:
			self.bottombox.pack_end(self.backbutton, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		if self.SHOW_BUTTON_HELP:
			self.bottombox.pack_end(self.helpbutton, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		if self.SHOW_BUTTON_EXIT:
			self.bottombox.pack_start(self.exitbutton, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)

		# We register the buttons with their callbacks
		self.finishbutton.connect("clicked", self.finish, None)
		self.forwardbutton.connect("clicked", self.forward, None)
		self.backbutton.connect("clicked", self.back, None)
		self.helpbutton.connect("clicked", self.help, None)
		self.exitbutton.connect("clicked", self.exit_button, None)

		self.make_visible()

	def redraw_left_pane(self, firstrun=False):
		if not firstrun: self.leftframe.remove(self.navlinks)
		self.navlinks = gtk.VBox(gtk.FALSE, 5)
		navlinkslabel = gtk.Label("    Installation Steps    ")
		self.navlinks.pack_start( navlinkslabel, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		self.num_times = 0
		for item_ in self.menuItems:
			item = str(self.num_times+1) + ". " + item_['text']
			self.box = gtk.HBox(gtk.FALSE,5)
#			self.boximg = gtk.Image()
#			if self._cur_panel != self.num_times:
#				self.boximg.set_from_file(self.__full_path+'/dot_images/previous.png')
#			else:
#				self.boximg.set_from_file(self.__full_path+'/dot_images/excited.png')
#			self.box.pack_start(self.boximg,expand=gtk.FALSE,fill=gtk.FALSE,padding=5)
			box_string = item
			box_label=gtk.Label(box_string)
			box_label.set_alignment(0,0)
			self.box.pack_start( box_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
			self.navlinks.pack_start( self.box, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
			box_label.set_sensitive(gtk.TRUE)

			if self._cur_panel == self.num_times:
				box_label.set_markup('<b>'+box_string+'</b>')

			self.num_times = self.num_times + 1
		self.leftframe.add(self.navlinks)
		self.leftframe.show_all()

	def redraw_buttons(self):
		self.bottombox.hide_all()
		self.finishbutton.set_sensitive(self.SHOW_BUTTON_FINISH)
		self.forwardbutton.set_sensitive(self.SHOW_BUTTON_FORWARD)
		self.backbutton.set_sensitive(self.SHOW_BUTTON_BACK)
		self.helpbutton.set_sensitive(self.SHOW_BUTTON_HELP)
		self.exitbutton.set_sensitive(self.SHOW_BUTTON_EXIT)
		if self.SHOW_BUTTON_FORWARD:
			self.forwardbutton.set_flags(gtk.CAN_DEFAULT)
			self.forwardbutton.grab_default()
		elif self.SHOW_BUTTON_FINISH:
			self.finishbutton.set_flags(gtk.CAN_DEFAULT)
			self.finishbutton.grab_default()
		if self.install_profile_xml_file != "":
			self.finishbutton.set_sensitive(gtk.TRUE)
		self.bottombox.show_all()

	def refresh_right_panel(self):
		self.rightframe.show_all()

	def make_visible(self):
		self.window.show_all()
		self.window.present()

	def make_invisible(self):
		self.window.hide_all()

	def get_current_path(self):
		# this will return the absolute path to the
		# directory containing this file
		# it will only work if this file is imported somewhere,
		# not if it is run directly (__file__ will be undefined)
		import os.path
		return os.path.abspath(os.path.dirname(__file__))

	def add_content(self, content):
		self.right_pane_box.pack_end(content, gtk.TRUE, gtk.TRUE, 0)

	def get_commands(self):
		pass

	def set_active(self):
		self.active=1

	def loadPanel(self, panel = 0):
		self._cur_panel = panel
		self.right_pane_box.set_current_page(panel)
		self.panels[panel].activate()
		self.redraw_buttons()
		self.redraw_left_pane()
#		self.make_visible()

	def run(self):
		self.loadPanel()
		gtk.main()

	def back(self, widget, data=None):
		if self._cur_panel > 0:
			self.loadPanel(self._cur_panel - 1)

	def forward(self, widget, data=None):
		if self._cur_panel < (len(self.menuItems) - 1):
			self.loadPanel(self._cur_panel + 1)

	def help(self, widget, data=None):
		print "Help was clicked"

	def exit_button(self, widget, data=None):
		print "Exit was clicked"
		self.exit()

	def finish(self, widget, data=None):
		print "Finish was clicked"

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
	
	def exit(self):
		gtk.main_quit()
		sys.exit(0)

install = Installer()
install.run()
