import gtk
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = "Bootloader"
	active_selection = None
	install_in_mbr = True
	boot_loaders = {}

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(gtk.FALSE, 0)
		vert.set_border_width(10)

		content_str = """Here, you will select which bootloader you would like to use. Each option has
a brief description beside it.
"""
		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)

		self.boot_loaders['grub'] = gtk.RadioButton(None, "grub")
		self.boot_loaders['grub'].set_name("grub")
		self.boot_loaders['grub'].connect("toggled", self.stage_selected, "grub")
		self.boot_loaders['grub'].set_size_request(100, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.boot_loaders['grub'], expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("This is the more popular bootloader. If you are installing on AMD64, this is\nyour only choice"), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)

		self.boot_loaders['lilo'] = gtk.RadioButton(self.boot_loaders['grub'], "lilo")
		self.boot_loaders['lilo'].set_name("lilo")
		self.boot_loaders['lilo'].connect("toggled", self.stage_selected, "lilo")
		self.boot_loaders['lilo'].set_size_request(100, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.boot_loaders['lilo'], expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("This bootloader isn't as flexible as grub, but some people still prefer it"), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)

		self.boot_loaders['none'] = gtk.RadioButton(self.boot_loaders['grub'], "None")
		self.boot_loaders['none'].set_name("none")
		self.boot_loaders['none'].connect("toggled", self.stage_selected, "none")
		self.boot_loaders['none'].set_size_request(100, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.boot_loaders['none'], expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("Choose this if you don't want a bootloader installed"), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)

		self.check_install_in_mbr = gtk.CheckButton("Install in MBR")
		self.check_install_in_mbr.connect("toggled", self.mbr_selected)
		self.check_install_in_mbr.set_size_request(100, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.check_install_in_mbr, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("This controls whether the bootloader is installed in the MBR or not"), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)

		self.add_content(vert)

	def stage_selected(self, widget, data=None):
		self.active_selection = data

	def mbr_selected(self, widget, data=None):
		self.install_in_mbr = self.check_install_in_mbr.get_active()

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
		self.active_selection = self.controller.install_profile.get_boot_loader_pkg() or "grub"
		self.boot_loaders[self.active_selection].set_active(gtk.TRUE)
		self.check_install_in_mbr.set_active(self.install_in_mbr)

	def deactivate(self):
		self.controller.install_profile.set_boot_loader_pkg(None, self.active_selection, None)
		self.controller.install_profile.set_boot_loader_mbr(None, self.install_in_mbr, None)
		return True
