import gtk
import os
import GLIScreen
from Widgets import Widgets

class Panel(GLIScreen.GLIScreen):
	"""
	The make.conf section of the installer.
	
	@author:    John N. Laliberte <allanonl@bu.edu>
	@license:   GPL
	"""
	# Attributes:
	title="rc.conf Settings" 
	# Operations
	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)

		vert    = gtk.VBox(False, 10) # This box is content so it should fill space to force title to top
		horiz   = gtk.HBox(False, 10)

		content_str = """
This is where you setup rc.conf."""
		# pack the description
		vert.pack_start(gtk.Label(content_str), expand=False, fill=False, padding=10)
		
		# keymap
		hbox = gtk.HBox(False, 0)
		label = gtk.Label("KEYMAP:")
		label.set_size_request(150, -1)
		#label.set_justify(gtk.JUSTIFY_LEFT)
		hbox.pack_start(label, expand=False, fill=False, padding=25)
		self.keymap = gtk.combo_box_new_text()
		self.keymap.set_size_request(150, -1)
		hbox.pack_start(self.keymap, expand=False, fill=False, padding=5)
		vert.pack_start(hbox,expand=False,fill=False,padding=0)
		
		# set_windowskeys
		hbox = gtk.HBox(False, 0)
		label = gtk.Label("SET_WINDOWKEYS:")
		label.set_size_request(150, -1)
		hbox.pack_start(label, expand=False, fill=False, padding=25)
		self.windowkeys = gtk.combo_box_new_text()
		self.windowkeys.set_size_request(150, -1)
		hbox.pack_start(self.windowkeys, expand=False, fill=False, padding=5)
		vert.pack_start(hbox,expand=False,fill=False,padding=0)
		
		# extended_keymaps
		hbox = gtk.HBox(False, 0)
		label = gtk.Label("EXTENDED_KEYMAPS:")
		label.set_size_request(150, -1)
		hbox.pack_start(label, expand=False, fill=False, padding=25)
		self.extended_keymaps = gtk.Entry()
		self.extended_keymaps.set_size_request(150, -1)
		hbox.pack_start(self.extended_keymaps, expand=False, fill=False, padding=5)
		vert.pack_start(hbox,expand=False,fill=False,padding=0)
		
		# consolefont
		hbox = gtk.HBox(False, 0)
		label = gtk.Label("CONSOLEFONT:")
		label.set_size_request(150, -1)
		hbox.pack_start(label, expand=False, fill=False, padding=25)
		self.consolefont = gtk.combo_box_new_text()
		self.consolefont.set_size_request(150, -1)
		hbox.pack_start(self.consolefont, expand=False, fill=False, padding=5)
		vert.pack_start(hbox,expand=False,fill=False,padding=0)
		
		# consoletranslation
		hbox = gtk.HBox(False, 0)
		label = gtk.Label("CONSOLETRANSLATION:")
		label.set_size_request(150, -1)
		hbox.pack_start(label, expand=False, fill=False, padding=25)
		self.consoletranslation = gtk.combo_box_new_text()
		self.consoletranslation.set_size_request(150, -1)
		hbox.pack_start(self.consoletranslation, expand=False, fill=False, padding=5)
		vert.pack_start(hbox,expand=False,fill=False,padding=0)
		
		# clock
		hbox = gtk.HBox(False, 0)
		label = gtk.Label("CLOCK:")
		label.set_size_request(150, -1)
		hbox.pack_start(label, expand=False, fill=False, padding=25)
		self.clock = gtk.combo_box_new_text()
		self.clock.set_size_request(150, -1)
		hbox.pack_start(self.clock, expand=False, fill=False, padding=5)
		vert.pack_start(hbox,expand=False,fill=False,padding=0)
		
		# editor
		hbox = gtk.HBox(False, 0)
		label = gtk.Label("EDITOR:")
		label.set_size_request(150, -1)
		hbox.pack_start(label, expand=False, fill=False, padding=25)
		self.editor = gtk.combo_box_entry_new_text()
		self.editor.set_size_request(150, -1)
		hbox.pack_start(self.editor, expand=False, fill=False, padding=5)
		vert.pack_start(hbox,expand=False,fill=False,padding=0)
		
		# protocols
		hbox = gtk.HBox(False, 0)
		label = gtk.Label("PROTOCOLS:")
		label.set_size_request(150, -1)
		hbox.pack_start(label, expand=False, fill=False, padding=25)
		self.protocols = gtk.Entry()
		self.protocols.set_size_request(150, -1)
		hbox.pack_start(self.protocols, expand=False, fill=False, padding=5)
		vert.pack_start(hbox,expand=False,fill=False,padding=0)
		
		# displaymanager
		hbox = gtk.HBox(False, 0)
		label = gtk.Label("DISPLAYMANAGER:")
		label.set_size_request(150, -1)
		hbox.pack_start(label, expand=False, fill=False, padding=25)
		self.displaymanager = gtk.combo_box_new_text()
		self.displaymanager.set_size_request(150, -1)
		hbox.pack_start(self.displaymanager, expand=False, fill=False, padding=5)
		vert.pack_start(hbox,expand=False,fill=False,padding=0)
		
		# xsession
		hbox = gtk.HBox(False, 0)
		label = gtk.Label("XSESSION:")
		label.set_size_request(150, -1)
		hbox.pack_start(label, expand=False, fill=False, padding=25)
		self.xsession = gtk.combo_box_entry_new_text()
		self.xsession.set_size_request(150, -1)
		hbox.pack_start(self.xsession, expand=False, fill=False, padding=5)
		vert.pack_start(hbox,expand=False,fill=False,padding=0)
		
		# populate the gui elements
		self.populate_keymap_combo()
		self.populate_windowkeys_combo()
		self.populate_consolefont_combo()
		self.populate_consoletranslation_combo()
		self.populate_clock_combo()
		self.populate_editor_combo()
		self.protocols.set_text("1 2")
		self.populate_displaymanager_combo()
		self.populate_xsession_combo()
		
		self.add_content(vert)
	
	def populate_keymap_combo(self, default="us"):
		# Adds all the keymaps to the dropdown
		keymaps = self.generate_keymap_list()
		
		for i in range(len(keymaps)):
			keymap = keymaps[i]
			self.keymap.append_text(keymap)
			
			# select the default
			if keymap == default:
				self.keymap.set_active(i)
	
	def populate_windowkeys_combo(self, default=1):
		self.windowkeys.append_text("No")
		self.windowkeys.append_text("Yes")
		self.windowkeys.set_active(default)
	
	def populate_consolefont_combo(self, default="default8x16"):
		# Adds all the consolefonts
		consolefonts = self.generate_consolefont_list()
		for i in range(len(consolefonts)):
			consolefont = consolefonts[i]
			self.consolefont.append_text(consolefont)
			
			# select the default
			if consolefont == default:
				self.consolefont.set_active(i)
	
	def populate_consoletranslation_combo(self, default=0):
		self.consoletranslation.append_text("commented out")
		
		consoletranslations = self.generate_consoletranslation_list()
		
		for i in range(len(consoletranslations)):
			consoletran = consoletranslations[i]
			self.consoletranslation.append_text(consoletran)
			
		self.consoletranslation.set_active(default)
				
	def populate_clock_combo(self, default=0):
		self.clock.append_text("UTC")
		self.clock.append_text("local")
		self.clock.set_active(default)
	
	def populate_editor_combo(self,default=0):
		self.editor.append_text("/bin/nano")
		self.editor.append_text("/usr/bin/vim")
		self.editor.append_text("/usr/bin/emacs")
		self.editor.set_active(default)
	
	def populate_displaymanager_combo(self,default=0):
		self.displaymanager.append_text("commented out")
		self.displaymanager.append_text("xdm")
		self.displaymanager.append_text("kdm")
		self.displaymanager.append_text("gdm")
		self.displaymanager.append_text("entrance")
		self.displaymanager.set_active(0)
	
	def populate_xsession_combo(self,default=-1):
		self.xsession.append_text("Gnome")
		self.xsession.append_text("Xsession")
		self.xsession.set_active(-1)
		
	def generate_keymap_list(self):
		keymap_list = []
		path = "/usr/share/keymaps"
		
		# find /usr/share/keymaps -iname *.map.gz -printf "%f \n"
		put, get = os.popen4("find "+path+" -iname *.map.gz -printf \"%f \n\"")
		for keymap in get.readlines():
			# strip the last 9 chars ( .map.gz\n )
			keymap.strip()
			keymap = keymap[:-9]
			keymap_list.append(keymap)
		
		# sort the keymap list
		keymap_list.sort()
		
		return keymap_list
	
	def generate_consolefont_list(self):
		consolefont_list=[]
		path = "/usr/share/consolefonts"
		
		# find /usr/share/consolefonts -iname *.gz -printf "%f \n"
		put, get = os.popen4("find "+path+" -iname *.gz -printf \"%f \n\"")
		for consolefont in get.readlines():
			# strip the last 5 chars ( .gz\n )
			consolefont.strip()
			consolefont = consolefont[:-5]
			
			# test if its psfu or psf or fnt
			# and remove it if necessary
			if consolefont[-4:]== "psfu":
				consolefont = consolefont[:-5]
			if consolefont[-3:]== "psf":
				consolefont = consolefont[:-4]
			if consolefont[-3:]=="fnt":
				consolefont = consolefont[:-4]
				
			consolefont_list.append(consolefont)
				
		# sort the keymap list
		consolefont_list.sort()
		
		return consolefont_list
	
	def generate_consoletranslation_list(self):
		consoletranslation_list=[]
		path = "/usr/share/consoletrans"
		
		# find /usr/share/keymaps -iname *.trans -printf "%f \n"
		put, get = os.popen4("find "+path+" -iname *.trans -printf \"%f \n\"")
		for consoletran in get.readlines():
			# strip the last 8 chars ( .trans\n )
			consoletran.strip()
			consoletran = consoletran[:-8]
			consoletranslation_list.append(consoletran)
			
		consoletranslation_list.sort()
		
		return consoletranslation_list
	
	def activate(self):
		rc_conf = self.controller.install_profile.get_rc_conf()
				
		self.controller.SHOW_BUTTON_EXIT    = True
		self.controller.SHOW_BUTTON_HELP    = True
		self.controller.SHOW_BUTTON_BACK    = True
		self.controller.SHOW_BUTTON_FORWARD = True
		self.controller.SHOW_BUTTON_FINISH  = False