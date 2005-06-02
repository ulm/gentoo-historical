import gtk
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = "Kernel Sources"
	active_selection = None
	kernel_sources = {}

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(False, 0)
		vert.set_border_width(10)

		content_str = """Here, you will select which kernel sources package you would like to use. Each option has
a brief description beside it.
"""
		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=False, fill=False, padding=0)

		self.kernel_sources['gentoo-sources'] = gtk.RadioButton(None, "gentoo-sources")
		self.kernel_sources['gentoo-sources'].set_name("gentoo-sources")
		self.kernel_sources['gentoo-sources'].connect("toggled", self.stage_selected, "gentoo-sources")
		self.kernel_sources['gentoo-sources'].set_size_request(150, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.kernel_sources['gentoo-sources'], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("These are the vanilla sources patched with the Gentoo patchset. These are generally considered stable.")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=10)

		self.kernel_sources['vanilla-sources'] = gtk.RadioButton(self.kernel_sources['gentoo-sources'], "vanilla-sources")
		self.kernel_sources['vanilla-sources'].set_name("vanilla-sources")
		self.kernel_sources['vanilla-sources'].connect("toggled", self.stage_selected, "vanilla-sources")
		self.kernel_sources['vanilla-sources'].set_size_request(150, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.kernel_sources['vanilla-sources'], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("These are the kernel sources straight from kernel.org without patches (except where necessary)")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=10)

		self.kernel_sources['livecd-kernel'] = gtk.RadioButton(self.kernel_sources['gentoo-sources'], "livecd-kernel")
		self.kernel_sources['livecd-kernel'].set_name("livecd-kernel")
		self.kernel_sources['livecd-kernel'].connect("toggled", self.stage_selected, "livecd-kernel")
		self.kernel_sources['livecd-kernel'].set_size_request(150, -1)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(self.kernel_sources['livecd-kernel'], expand=False, fill=False, padding=5)
		tmplabel = gtk.Label("This will install the LiveCD's kernel/initrd into your new system. Use this option to get your system up and running quickly. You should not tell the installer to emerge any packages that require kernel sources as they won't be present.")
		tmplabel.set_line_wrap(True)
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=20)
		vert.pack_start(hbox, expand=False, fill=False, padding=10)

		self.add_content(vert)

	def stage_selected(self, widget, data=None):
		self.active_selection = data

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = True
		self.controller.SHOW_BUTTON_HELP    = True
		self.controller.SHOW_BUTTON_BACK    = True
		self.controller.SHOW_BUTTON_FORWARD = True
		self.controller.SHOW_BUTTON_FINISH  = False
		self.active_selection = self.controller.install_profile.get_kernel_source_pkg() or "gentoo-sources"
		self.kernel_sources[self.active_selection].set_active(True)

	def deactivate(self):
		self.controller.install_profile.set_kernel_source_pkg(None, self.active_selection, None)
		return True
