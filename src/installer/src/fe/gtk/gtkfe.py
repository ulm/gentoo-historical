#!/usr/bin/python

import sys
sys.path.append("../..")

import GLIInstallProfile
import GLIClientConfiguration
import GLIClientController
import GLIUtility
import gtk
import crypt
import random

import Welcome
import PartitioningMain
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
import NetworkMounts

import RunInstall

class Installer:

	SHOW_BUTTON_FINISH = 1
	SHOW_BUTTON_FORWARD = 1
	SHOW_BUTTON_BACK = 1
	SHOW_BUTTON_HELP = 1
	SHOW_BUTTON_EXIT = 1
	install_profile_xml_file = ""
	install_window = None

	menuItems = [ { 'text': 'Welcome', 'module': Welcome },
                      { 'text': 'Partitioning', 'module': PartitioningMain },
                      { 'text': 'Network Mounts', 'module': NetworkMounts },
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
                      { 'text': 'Review', 'module': InstallSummary }
                    ]

	def __init__(self):
		self.client_profile = GLIClientConfiguration.ClientConfiguration()
		self.install_profile = GLIInstallProfile.InstallProfile()
		# Removed the training wheels!
		if len(sys.argv) > 1 and (sys.argv[1] == "-p" or sys.argv[1] == "--pretend"):
			self.cc = GLIClientController.GLIClientController(pretend=True)
		else:
			self.cc = GLIClientController.GLIClientController()
		# I'm feeling lazy
		self.client_profile.set_interactive(None, True, None)
		self.client_profile.set_architecture_template(None, "x86", None)
		self.client_profile.set_log_file(None, "/tmp/install.log", None)
		self.client_profile.set_root_mount_point(None, "/mnt/gentoo", None)
		self.client_profile.set_root_passwd(None, GLIUtility.hash_password("blah"), None)
		self.client_profile.set_enable_ssh(None, False, None)
		self.cc.set_configuration(self.client_profile)
		self.cc.start_pre_install()

		self.window = None
		self.panel = None
		self._cur_panel = 0
		self.__full_path = self.get_current_path()
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.title="Gentoo Linux Installer"
		self.window.realize()
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		self.window.set_border_width(0)
		self.window.set_default_size(800,600)
		self.window.set_geometry_hints(None, min_width=800, min_height=600, max_width=800, max_height=600)
		self.window.set_title("Gentoo Linux Installer")
		self.globalbox = gtk.VBox(False, 0)
		self.window.add(self.globalbox)
		self.headerbox = gtk.HBox(False, 0)
		headerimg = gtk.Image()
		headerimg.set_from_file(self.__full_path + '/installer-banner-800x64.png') # '/header.png')
		self.headerbox.add(headerimg)
		self.topbox = gtk.HBox(False, 0)
		self.bottombox = gtk.HBox(False, 0)
		self.globalbox.pack_start(self.headerbox, expand=False, fill=False, padding=0)
		self.globalbox.pack_start(self.topbox, expand=True, fill=True, padding=5)
		self.globalbox.pack_end(self.bottombox, expand=False, fill=False, padding=5)
		self.leftframe = gtk.Frame()
		self.rightframe = gtk.Frame()
		self.leftframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.rightframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.topbox.pack_start(self.leftframe, expand=False, fill=False, padding=5)
		self.topbox.pack_end(self.rightframe, expand=True, fill=True, padding=5)
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
		self.right_pane_box.set_show_tabs(False)
		self.right_pane_box.set_show_border(False)
		self.rightframe.add(self.right_pane_box)

		buttons_info = [ ('exit', " _Exit ", '/button_images/stock_exit.png', self.exit_button, 'start'),
                                 ('help', " _Help ", '/button_images/stock_help.png', self.help, 'start'),
                                 ('load', " _Load ", '/button_images/stock_open.png', self.load_button, 'start'),
                                 ('save', " _Save ", '/button_images/stock_save.png', self.save_button, 'start'),
                                 ('finish', " _Install ", '/button_images/stock_exec.png', self.finish, 'end'),
                                 ('forward', " _Forward ", '/button_images/stock_right.png', self.forward, 'end'),
                                 ('back', " _Back ", '/button_images/stock_left.png', self.back, 'end')
                               ]
		self.buttons = {}

		for button in buttons_info:
			self.buttons[button[0]] = gtk.Button()
			tmpbuttonbox = gtk.HBox(False, 0)
			tmpbuttonimg = gtk.Image()
			tmpbuttonimg.set_from_file(self.__full_path + button[2])
			tmpbuttonbox.pack_start(tmpbuttonimg)
			tmpbuttonlabel = gtk.Label(button[1])
			tmpbuttonlabel.set_use_underline(True)
			tmpbuttonbox.pack_start(tmpbuttonlabel)
			self.buttons[button[0]].add(tmpbuttonbox)
			self.buttons[button[0]].connect("clicked", button[3], None)
			if button[4] == "start":
				self.bottombox.pack_start(self.buttons[button[0]], expand=False, fill=False, padding=5)
			else:
				self.bottombox.pack_end(self.buttons[button[0]], expand=False, fill=False, padding=5)

		self.make_visible()

	def redraw_left_pane(self, firstrun=False):
		if not firstrun: self.leftframe.remove(self.navlinks)
		self.navlinks = gtk.VBox(False, 5)
		self.navlinks.set_size_request(140, -1)
		navlinkslabel = gtk.Label("    Installation Steps    ")
		self.navlinks.pack_start( navlinkslabel, expand=False, fill=False, padding=10)
		self.num_times = 0
		for item_ in self.menuItems:
			item = str(self.num_times+1) + ". " + item_['text']
			self.box = gtk.HBox(False,5)
			box_string = item
			box_label=gtk.Label(box_string)
			box_label.set_alignment(0,0)
			self.box.pack_start( box_label, expand=False, fill=False, padding=5)
			self.navlinks.pack_start( self.box, expand=False, fill=False, padding=3)
			box_label.set_sensitive(True)

			if self._cur_panel == self.num_times:
				box_label.set_markup('<b>'+box_string+'</b>')

			self.num_times = self.num_times + 1
		self.leftframe.add(self.navlinks)
		self.leftframe.show_all()

	def redraw_buttons(self):
		self.bottombox.hide_all()
#		self.finishbutton.set_sensitive(self.SHOW_BUTTON_FINISH)
#		self.forwardbutton.set_sensitive(self.SHOW_BUTTON_FORWARD)
#		self.backbutton.set_sensitive(self.SHOW_BUTTON_BACK)
#		self.helpbutton.set_sensitive(self.SHOW_BUTTON_HELP)
#		self.exitbutton.set_sensitive(self.SHOW_BUTTON_EXIT)
		self.buttons['finish'].set_sensitive(self.SHOW_BUTTON_FINISH)
		self.buttons['forward'].set_sensitive(self.SHOW_BUTTON_FORWARD)
		self.buttons['back'].set_sensitive(self.SHOW_BUTTON_BACK)
		self.buttons['help'].set_sensitive(self.SHOW_BUTTON_HELP)
		self.buttons['exit'].set_sensitive(self.SHOW_BUTTON_EXIT)
		if self.SHOW_BUTTON_FORWARD:
#			self.forwardbutton.set_flags(gtk.CAN_DEFAULT)
#			self.forwardbutton.grab_default()
			self.buttons['forward'].set_flags(gtk.CAN_DEFAULT)
			self.buttons['forward'].grab_default()
		elif self.SHOW_BUTTON_FINISH:
#			self.finishbutton.set_flags(gtk.CAN_DEFAULT)
#			self.finishbutton.grab_default()
			self.buttons['finish'].set_flags(gtk.CAN_DEFAULT)
			self.buttons['finish'].grab_default()
#		if self.install_profile_xml_file != "":
#			self.finishbutton.set_sensitive(True)
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
		self.right_pane_box.pack_end(content, True, True, 0)

	def get_commands(self):
		pass

	def set_active(self):
		self.active=1

	def loadPanel(self, panel = 0):
		if not self.panels[self._cur_panel].deactivate():
			return
		self._cur_panel = panel
		self.right_pane_box.set_current_page(panel)
		self.panels[panel].activate()
		self.redraw_buttons()
		self.redraw_left_pane()

	def run(self):
		self.loadPanel()
		gtk.threads_init()
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
		msgdlg = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format="Are you sure you want to exit?")
		resp = msgdlg.run()
		msgdlg.destroy()
		if resp == gtk.RESPONSE_YES:
			self.exit()

	def finish(self, widget, data=None):
		print "Finish was clicked"
		self.make_invisible()
		self.install_window = RunInstall.RunInstall(self)

	def load_button(self, widget, data=None):
		filesel = gtk.FileSelection("Select the install profile to load")
		if self.install_profile_xml_file == "":
			filesel.set_filename("installprofile.xml")
		else:
			filesel.set_filename(self.install_profile_xml_file)
		resp = filesel.run()
		filename = filesel.get_filename()
		filesel.destroy()
		if resp == gtk.RESPONSE_OK:
			self.install_profile_xml_file = filename
			try:
				tmp_install_profile = GLIInstallProfile.InstallProfile()
				tmp_install_profile.parse(self.install_profile_xml_file)
				self.install_profile = tmp_install_profile
				msgdlg = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK, message_format="Install profile loaded successfully!")
				msgdlg.run()
				msgdlg.destroy()
			except:
				errdlg = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK, message_format="An error occured loading the install profile")
				errdlg.run()
				errdlg.destroy()

	def save_button(self, widget, data=None):
		filesel = gtk.FileSelection("Select the location to save the install profile")
		if self.install_profile_xml_file == "":
			filesel.set_filename("installprofile.xml")
		else:
			filesel.set_filename(self.install_profile_xml_file)
		resp = filesel.run()
		filename = filesel.get_filename()
		filesel.destroy()
		if resp == gtk.RESPONSE_OK:
			self.install_profile_xml_file = filename
			try:
				configuration = open(filename, "w")
				configuration.write(self.install_profile.serialize())
				configuration.close()
				msgdlg = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK, message_format="Install profile saved successfully!")
				msgdlg.run()
				msgdlg.destroy()
			except:
				errdlg = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK, message_format="An error occured saving the install profile")
				errdlg.run()
				errdlg.destroy()

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
	
	def exit(self):
		gtk.main_quit()
		sys.exit(0)

install = Installer()
install.run()
