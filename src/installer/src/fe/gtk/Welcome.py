import gtk
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = "Welcome to the Gentoo Linux Installer"

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(gtk.FALSE, 10) # This box is content so it should fill space to force title to top
		horiz = gtk.HBox(gtk.FALSE, 10)

		content_str = """
Welcome to The Gentoo Linux Installer. This is a TESTING release.
If your system dies a horrible, horrible death, don't come crying
to us (okay, you can cry to klieber).

In this part of the installer, you will make all of your decisions
for how you want your system setup. No changes will be made to your
system until you click the "Install" button. At any point before you
click "Install", you can click "Save" to save your install profile
and come back at a later time to finish.

If you have installed Gentoo Linux previously using this installer
and you saved your configuration settings, you can click the "Load"
button to load your previous settings as defaults.
"""

		content_str2 = """Click the "Forward" button below to begin your
Gentoo Linux installation."""
 	
		content_label = gtk.Label(content_str)
		content_label2 = gtk.Label(content_str2)
		vert.pack_start(content_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)            
		container = gtk.HBox(gtk.FALSE,30)
		floppy_image  = gtk.Image()
		floppy_image.set_from_file(self.full_path + '/content_images/gnome-dev-floppy.png')
		entry_box = gtk.HBox(gtk.FALSE, 5)
		entry_box2 = gtk.HBox(gtk.TRUE, 5)
		load_label = gtk.Label("Profile URI:")
		self.load_status_label = gtk.Label("")
		self.load_text = gtk.Entry(max=256)
		self.load_text.set_width_chars(40)
		self.load_text.set_flags(gtk.CAN_FOCUS)
		self.load_text.grab_focus()
		entry_box.pack_start(load_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		entry_box.pack_start(self.load_text, expand=gtk.FALSE, fill=gtk.FALSE)
		load_button = gtk.Button("_Load Profile", use_underline=gtk.TRUE)
		load_button.connect("clicked", self.load_profile, None)
		entry_box.pack_start(load_button, expand=gtk.FALSE, fill=gtk.FALSE, padding=30)
		entry_box2.pack_start(entry_box, expand=gtk.FALSE, fill=gtk.FALSE)
		vert.pack_start(entry_box2, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		vert.pack_start(self.load_status_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		container.pack_start(floppy_image, expand=gtk.FALSE, fill=gtk.FALSE, padding=40)
		container.pack_start(content_label2, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		vert.pack_end(container, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		self.add_content(vert)

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.FALSE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
		if not self.controller.install_profile_xml_file == "":
			self.load_status_label.set_text("Profile '" + self.controller.install_profile_xml_file + "' loaded successfully")
		self.load_text.set_text(self.controller.install_profile_xml_file)

	def load_profile(self, widget, data=None):
		install_profile_xml_file = self.load_text.get_text()
		self.load_status_label.set_text("Loading '" + install_profile_xml_file + "'")
		try:
			self.controller.install_profile.parse(install_profile_xml_file)
			self.controller.install_profile_xml_file = install_profile_xml_file
			self.load_status_label.set_text("Profile '" + install_profile_xml_file + "' loaded successfully")
		except:
			self.load_status_label.set_text("Problem loading profile '" + install_profile_xml_file + "'")
