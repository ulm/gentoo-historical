import gtk, gobject
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = "Network Mounts"
	columns = []

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(gtk.FALSE, 0)
		vert.set_border_width(10)

		self.treedata = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
		self.treedata.append(["kagome", "/usr/portage", "NFS", "/usr/portage", "ro"])
		self.treedata.append(["kagome", "/var/cache/edb/dep", "NFS", "/var/cache/edb/dep", "rw,noauto"])
		self.treedatasort = gtk.TreeModelSort(self.treedata)
		self.treeview = gtk.TreeView(self.treedatasort)
		self.columns.append(gtk.TreeViewColumn("Host/IP", gtk.CellRendererText(), text=0))
		self.columns.append(gtk.TreeViewColumn("Export/Share", gtk.CellRendererText(), text=1))
		self.columns.append(gtk.TreeViewColumn("Type", gtk.CellRendererText(), text=2))
		self.columns.append(gtk.TreeViewColumn("Mount Point", gtk.CellRendererText(), text=3))
		self.columns.append(gtk.TreeViewColumn("Mount Options", gtk.CellRendererText(), text=4))
		col_num = 0
		for column in self.columns:
			column.set_resizable(gtk.TRUE)
			column.set_sort_column_id(col_num)
			self.treeview.append_column(column)
			col_num += 1
		self.treewindow = gtk.ScrolledWindow()
		self.treewindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.treewindow.add(self.treeview)
		vert.pack_start(self.treewindow, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)

		self.add_content(vert)

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
