import gtk
import GLIScreen
import commands
import gobject

class Panel(GLIScreen.GLIScreen):

	title = "make.conf"
	make_conf_values = {}
	use_flags = []
	use_desc = {}
	columns = []
	arch_procs = { 'x86': ("i386", "i486", "i586", "pentium", "pentium-mmx", "i686", "pentiumpro", "pentium2", "pentium3", "pentium3m", "pentium-m", "pentium4", "pentium4m", "prescott", "nocona", "k6", "k6-2", "k6-3", "athlon", "athlon-tbird", "athlon-4", "athlon-xp", "athlon-mp", "k8", "opteron", "athlon64", "athlon-fx", "winchip-c6", "winchip2", "c3", "c3-2") }
	optimizations = ["-O0", "-O1", "-O2", "-Os", "-O3"]

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)

#		self.system_use_flags = commands.getoutput("emerge info | grep -e '^USE' | sed -e 's:USE=\"::' -e 's:\"::'").split(" ")
		self.system_use_flags = commands.getoutput("portageq envvar USE").strip()

		vert = gtk.VBox(gtk.FALSE, 0)
		vert.set_border_width(10)

		content_str = """On this screen, you'll define all of your /etc/make.conf settings.
"""

		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)

		f = open("/usr/portage/profiles/use.desc", "r")
		for line in f:
			line = line.strip()
			if not line or line.startswith("#"): continue
			dash_pos = line.find(" - ")
			if dash_pos == -1: continue
			flagname = line[:dash_pos] or line[dash_pos-1]
			desc = line[dash_pos+3:]
			self.use_desc[flagname] = desc
		f.close()

		f = open("/usr/portage/profiles/use.local.desc", "r")
		for line in f:
			line = line.strip()
			if not line or line.startswith("#"): continue
			dash_pos = line.find(" - ")
			if dash_pos == -1: continue
			colon_pos = line.find(":", 0, dash_pos)
			pkg = line[:colon_pos]
			flagname = line[colon_pos+1:dash_pos] or line[colon_pos+1]
			desc = "(" + pkg + ") " + line[dash_pos+3:]
			self.use_desc[flagname] = desc
		f.close()

		hbox = gtk.HBox(gtk.FALSE, 0)
		label = gtk.Label()
		label.set_markup("<b>USE flags:</b>")
		hbox.pack_start(label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)

		sorted_use = self.use_desc.keys()
		sorted_use.sort()
                self.treedata = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING)
		for flag in sorted_use:
                        self.treedata.append([(flag in self.use_flags and self.use_flags[flag] == 1), flag, self.use_desc[flag]])
                self.treeview = gtk.TreeView(self.treedata)
		self.toggle_renderer = gtk.CellRendererToggle()
		self.toggle_renderer.set_property("activatable", True)
		self.toggle_renderer.connect("toggled", self.flag_toggled)
		self.columns.append(gtk.TreeViewColumn("Active", self.toggle_renderer, active=0))
                self.columns.append(gtk.TreeViewColumn("Flag", gtk.CellRendererText(), text=1))
                self.columns.append(gtk.TreeViewColumn("Description", gtk.CellRendererText(), text=2))
                for column in self.columns:
                        column.set_resizable(gtk.TRUE)
                        self.treeview.append_column(column)
                self.treewindow = gtk.ScrolledWindow()
                self.treewindow.set_size_request(-1, 170)
                self.treewindow.set_shadow_type(gtk.SHADOW_IN)
                self.treewindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
                self.treewindow.add(self.treeview)
                vert.pack_start(self.treewindow, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

		hbox = gtk.HBox(gtk.FALSE, 0)
		label = gtk.Label()
		label.set_markup("<b>CFLAGS:</b>")
		hbox.pack_start(label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)

		hbox = gtk.HBox(gtk.FALSE, 0)
		hbox.pack_start(gtk.Label("Processor:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		self.proc_combo = gtk.combo_box_new_text()
		for proc in self.arch_procs['x86']:
			self.proc_combo.append_text(proc)
		self.proc_combo.set_active(0)
		hbox.pack_start(self.proc_combo, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		hbox.pack_start(gtk.Label("Optimizations:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		self.optimizations_combo = gtk.combo_box_new_text()
		for opt in self.optimizations:
			self.optimizations_combo.append_text(opt)
		self.optimizations_combo.set_active(0)
		hbox.pack_start(self.optimizations_combo, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		hbox.pack_start(gtk.Label("Custom:"), expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
		self.custom_cflags_entry = gtk.Entry()
		self.custom_cflags_entry.set_width_chars(25)
		self.custom_cflags_entry.set_text("-pipe")
		hbox.pack_start(self.custom_cflags_entry, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		vert.pack_start(hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=5)

		self.add_content(vert)

	def flag_toggled(self, cell, path):
		model = self.treeview.get_model()
		model[path][0] = not model[path][0]
		flag = model[path][1]
		if model[path][0]:
			self.use_flags[flag] = 1
		else:
			if flag in self.use_flags:
				self.use_flags[flag] = 0
		return

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
		self.make_conf_values = self.controller.install_profile.get_make_conf()
		self.use_flags = {}
		if not self.make_conf_values.has_key('USE') or not self.make_conf_values['USE']:
			self.make_conf_values['USE'] = self.system_use_flags
		for flag in self.make_conf_values['USE'].split(" "):
			if flag.startswith("-"):
				flag = flag[1:]
				self.use_flags[flag] = 0
			else:
				self.use_flags[flag] = 1
		sorted_use = self.use_desc.keys()
		sorted_use.sort()
                self.treedata = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING)
		for flag in sorted_use:
			if flag in self.use_flags and self.use_flags[flag] == 1:
	                        self.treedata.append([True, flag, self.use_desc[flag]])
			else:
        	                self.treedata.append([False, flag, self.use_desc[flag]])
		self.treeview.set_model(self.treedata)

	def deactivate(self):
		temp_use = ""
		sorted_use = self.use_flags.keys()
		sorted_use.sort()
		for flag in sorted_use:
			if self.use_flags[flag]:
				temp_use += " " + flag
			else:
				temp_use += " -" + flag
		self.make_conf_values['USE'] = temp_use
		self.make_conf_values['CFLAGS'] = "-march=" + self.arch_procs['x86'][self.proc_combo.get_active()] + " " + self.optimizations[self.optimizations_combo.get_active()] + " " + self.custom_cflags_entry.get_text()
		print self.make_conf_values['CFLAGS']
		self.controller.install_profile.set_make_conf(self.make_conf_values)
		return True
