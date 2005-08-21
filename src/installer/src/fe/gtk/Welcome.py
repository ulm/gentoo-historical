import gtk
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = _("Welcome to the Gentoo Linux Installer")

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(False, 10)
		vert.set_border_width(10)

		content_str = _("""
Welcome to the GTK+ frontend for the Gentoo Linux Installer. This is a TESTING
release. If your system dies a horrible, horrible death, don't come crying to us.
No, really, don't. We'll all just point and laugh and tell you that we told you so.

In this part of the installer, you will make all of your decisions for how you want
your system setup. No changes will be made to your system until you click the
"Install" button. At any point before you click "Install", you can click "Save" to
save your install profile and come back at a later time to finish.

If you have installed Gentoo Linux previously using this installer and you saved
your configuration settings (install profile), you can click the "Load" button to
load your previous settings as defaults.""")

		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=False, fill=False, padding=0)            

		self.add_content(vert)

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = True
		self.controller.SHOW_BUTTON_HELP    = True
		self.controller.SHOW_BUTTON_BACK    = False
		self.controller.SHOW_BUTTON_FORWARD = True
		self.controller.SHOW_BUTTON_FINISH  = False
