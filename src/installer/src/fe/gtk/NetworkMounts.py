import gtk, gobject
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = "Network Mounts"

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(gtk.FALSE, 0)
		vert.set_border_width(10)

#		self.treedata = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
		self.treedata = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
		self.treedata.append(["kagome", "/usr/portage", "NFS", "/usr/portage", "ro"])
		self.treedata.append(["kagome", "/var/cache/edb/dep", "NFS", "/var/cache/edb/dep", "rw,noauto"])
		self.treeview = gtk.TreeView(self.treedata)
		self.treeview.append_column(gtk.TreeViewColumn("Host/IP", gtk.CellRendererText(), text=0))
		self.treeview.append_column(gtk.TreeViewColumn("Export/Share", gtk.CellRendererText(), text=1))
		self.treeview.append_column(gtk.TreeViewColumn("Type", gtk.CellRendererText(), text=2))
		self.treeview.append_column(gtk.TreeViewColumn("Mount Point", gtk.CellRendererText(), text=3))
		self.treeview.append_column(gtk.TreeViewColumn("Mount Options", gtk.CellRendererText(), text=4))
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
