import gtk
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = "Kernel Sources"
	active_selection = 1
	kernel_sources = {}

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(gtk.FALSE, 0)
		vert.set_border_width(10)

		content_str = """Here, you will select which kernel sources package you would like to use. Each option has
a brief description beside it.
"""
		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)

		self.kernel_sources['vanilla-sources'] = gtk.RadioButton(None, "vanilla-sources")
		self.kernel_sources['vanilla-sources'].set_name("vanilla-sources")
		self.kernel_sources['vanilla-sources'].connect("toggled", self.stage_selected, "vanilla-sources")
		self.kernel_sources['vanilla-sources'].set_size_request(150, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.kernel_sources['vanilla-sources'], expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("These are the kernel sources straight from kernel.org without\npatches (except where necessary)"), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)

		self.kernel_sources['gentoo-sources'] = gtk.RadioButton(self.kernel_sources['vanilla-sources'], "gentoo-sources")
		self.kernel_sources['gentoo-sources'].set_name("gentoo-sources")
		self.kernel_sources['gentoo-sources'].connect("toggled", self.stage_selected, "gentoo-sources")
		self.kernel_sources['gentoo-sources'].set_size_request(150, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.kernel_sources['gentoo-sources'], expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("These are the vanilla sources patched with the Gentoo patchset. These\nare generally considered stable."), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)

		self.kernel_sources['hardened-sources'] = gtk.RadioButton(self.kernel_sources['vanilla-sources'], "hardened-sources")
		self.kernel_sources['hardened-sources'].set_name("hardened-sources")
		self.kernel_sources['hardened-sources'].connect("toggled", self.stage_selected, "hardened-sources")
		self.kernel_sources['hardened-sources'].set_size_request(150, -1)
		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(self.kernel_sources['hardened-sources'], expand=gtk.FALSE, fill=gtk.FALSE, padding=5)
		hbox.pack_start(gtk.Label("These sources are patched with security-related patches that generally\ntighten system security."), expand=gtk.FALSE, fill=gtk.FALSE, padding=20)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=20)

		self.add_content(vert)

	def stage_selected(self, widget, data=None):
		self.active_selection = data

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
		self.active_selection = self.controller.install_profile.get_kernel_source_pkg() or "vanilla-sources"
		self.kernel_sources[self.active_selection].set_active(gtk.TRUE)

	def deactivate(self):
		self.controller.install_profile.set_kernel_source_pkg(None, self.active_selection, None)
		return True
