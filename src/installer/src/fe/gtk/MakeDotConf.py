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

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)

		self.system_use_flags = commands.getoutput("emerge info | grep -e '^USE' | sed -e 's:USE=\"::' -e 's:\"::'").split(" ")

		vert = gtk.VBox(gtk.FALSE, 0)
		vert.set_border_width(10)

		content_str = """On this screen, you'll define all of your /etc/make.conf settings.
"""

		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)

		f = open("/usr/portage/profiles/use.desc", "r")
		for line in f:
			line.strip()
			if line == "" or line.startswith("#"): continue
			dash_pos = line.find(" - ")
			if dash_pos == -1: continue
			flagname = line[:dash_pos] or line[dash_pos-1]
			desc = line[dash_pos+3:]
			self.use_desc[flagname] = desc
		f.close()

		f = open("/usr/portage/profiles/use.local.desc", "r")
		for line in f:
			line.strip()
			if line == "" or line.startswith("#"): continue
			dash_pos = line.find(" - ")
			if dash_pos == -1: continue
			colon_pos = line.find(":", 0, dash_pos)
			pkg = line[:colon_pos]
			flagname = line[colon_pos+1:dash_pos] or line[colon_pos+1]
			desc = "(" + pkg + ") " + line[dash_pos+3:]
			self.use_desc[flagname] = desc
		f.close()

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
                self.treewindow.set_size_request(-1, 300)
                self.treewindow.set_shadow_type(gtk.SHADOW_IN)
                self.treewindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
                self.treewindow.add(self.treeview)
                vert.pack_start(self.treewindow, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
 	
		self.add_content(vert)

	def flag_toggled(self, cell, path):
		model = self.treeview.get_model()
		model[path][0] = not model[path][0]
		if model[path][0]:
			self.use_flags['path'] = 1
		else:
			if path in self.use_flags: self.use_flags['path'] = 0
		return

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
		self.make_conf_values = self.controller.install_profile.get_make_conf()
		self.use_flags = {}
		if not self.make_conf_values.has_key('USE') or self.make_conf_values['USE'] == "":
			self.make_conf_values['USE'] = self.system_use_flags
		for flag in self.make_conf_values['USE']:
			if flag.startswith("-"):
				flag = flag[1:] or flag[1]
				self.use_flags[flag] = 0
			else:
				self.use_flags[flag] = 1
		sorted_use = self.use_desc.keys()
		sorted_use.sort()
                self.treedata = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING)
		for flag in sorted_use:
                        self.treedata.append([(flag in self.use_flags), flag, self.use_desc[flag]])
		self.treeview.set_model(self.treedata)

	def deactivate(self):
		self.make_conf_values['USE'] = " ".join(self.use_flags)
		set.controller.install_profile.set_make_conf(self.make_conf_values)
		return True
