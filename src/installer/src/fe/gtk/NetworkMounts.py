import gtk, gobject
import GLIScreen
import GLIUtility
import Widgets
import commands, string
import copy

class Panel(GLIScreen.GLIScreen):

	title = "Network Mounts"
	columns = []
	netmounts = []
	active_entry = -1

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(gtk.FALSE, 0)
		vert.set_border_width(10)

		self.netmounts.append({ 'host': "kagome", 'export': "/usr/portage", 'type': "NFS", 'mountpoint': "/usr/portage", 'mountopts': "ro"})
		self.netmounts.append({ 'host': "kagome", 'export': "/var/cache/edb/dep", 'type': "NFS", 'mountpoint': "/var/cache/edb/dep", 'mountopts': "rw,noauto"})

		self.treedata = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
		for i in range(0, len(self.netmounts)):
			self.treedata.append([i, self.netmounts[i]['host'], self.netmounts[i]['export'], self.netmounts[i]['type'], self.netmounts[i]['mountpoint'], self.netmounts[i]['mountopts']])
		self.treedatasort = gtk.TreeModelSort(self.treedata)
		self.treeview = gtk.TreeView(self.treedatasort)
		self.treeview.connect("cursor-changed", self.selection_changed)
		self.columns.append(gtk.TreeViewColumn("Host/IP", gtk.CellRendererText(), text=1))
		self.columns.append(gtk.TreeViewColumn("Export/Share", gtk.CellRendererText(), text=2))
		self.columns.append(gtk.TreeViewColumn("Type", gtk.CellRendererText(), text=3))
		self.columns.append(gtk.TreeViewColumn("Mount Point", gtk.CellRendererText(), text=4))
		self.columns.append(gtk.TreeViewColumn("Mount Options", gtk.CellRendererText(), text=5))
		col_num = 0
		for column in self.columns:
			column.set_resizable(gtk.TRUE)
			column.set_sort_column_id(col_num)
			self.treeview.append_column(column)
			col_num += 1
		self.treewindow = gtk.ScrolledWindow()
		self.treewindow.set_size_request(-1, 100)
		self.treewindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.treewindow.add(self.treeview)
		vert.pack_start(self.treewindow, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)

		self.mount_info_box = gtk.HBox(gtk.FALSE, 0)
		mount_info_table = gtk.Table(5, 2, gtk.FALSE)
		mount_info_table.set_col_spacings(10)
		mount_info_table.set_row_spacings(6)
		mount_info_host_label = gtk.Label("Host/IP:")
		mount_info_host_label.set_alignment(0.0, 0.5)
		mount_info_table.attach(mount_info_host_label, 0, 1, 0, 1)
		self.mount_info_host = gtk.Entry()
		self.mount_info_host.set_width_chars(25)
		mount_info_table.attach(self.mount_info_host, 1, 2, 0, 1)
		mount_info_export_label = gtk.Label("Export/Share:")
		mount_info_export_label.set_alignment(0.0, 0.5)
		mount_info_table.attach(mount_info_export_label, 0, 1, 1, 2)
#		self.mount_info_export = gtk.combo_box_entry_new_text()
		self.mount_info_export = gtk.ComboBoxEntry(gtk.ListStore(gobject.TYPE_STRING))
		self.mount_info_export.set_text_column(0)
		mount_info_table.attach(self.mount_info_export, 1, 2, 1, 2)
		mount_info_type_label = gtk.Label("Type:")
		mount_info_type_label.set_alignment(0.0, 0.5)
		mount_info_table.attach(mount_info_type_label, 0, 1, 2, 3)
		self.mount_info_type = gtk.Entry()
		self.mount_info_type.set_width_chars(30)
		mount_info_table.attach(self.mount_info_type, 1, 2, 2, 3)
		mount_info_mountpoint_label = gtk.Label("Mount point:")
		mount_info_mountpoint_label.set_alignment(0.0, 0.5)
		mount_info_table.attach(mount_info_mountpoint_label, 0, 1, 3, 4)
		self.mount_info_mountpoint = gtk.Entry()
		self.mount_info_mountpoint.set_width_chars(30)
		mount_info_table.attach(self.mount_info_mountpoint, 1, 2, 3, 4)
		mount_info_mountopts_label = gtk.Label("Mount options:")
		mount_info_mountopts_label.set_alignment(0.0, 0.5)
		mount_info_table.attach(mount_info_mountopts_label, 0, 1, 4, 5)
		self.mount_info_mountopts = gtk.Entry()
		self.mount_info_mountopts.set_width_chars(30)
		mount_info_table.attach(self.mount_info_mountopts, 1, 2, 4, 5)
		self.mount_info_box.pack_start(mount_info_table, expand=gtk.FALSE, fill=gtk.FALSE)
		vert.pack_start(self.mount_info_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

		mount_button_box = gtk.HBox(gtk.FALSE, 0)
		mount_button_new = gtk.Button(" _New ")
		mount_button_new.connect("clicked", self.new_mount)
		mount_button_box.pack_start(mount_button_new, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		self.mount_button_update = gtk.Button(" _Update ")
		self.mount_button_update.connect("clicked", self.update_mount)
		self.mount_button_update.set_sensitive(gtk.FALSE)
		mount_button_box.pack_start(self.mount_button_update, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		self.mount_button_delete = gtk.Button(" _Delete ")
		self.mount_button_delete.connect("clicked", self.delete_mount)
		self.mount_button_delete.set_sensitive(gtk.FALSE)
		mount_button_box.pack_start(self.mount_button_delete, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		self.mount_button_populate = gtk.Button(" _Populate Exports ")
		self.mount_button_populate.connect("clicked", self.populate_exports)
		self.mount_button_populate.set_sensitive(gtk.FALSE)
		mount_button_box.pack_start(self.mount_button_populate, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
		vert.pack_start(mount_button_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

		self.add_content(vert)

	def disable_all_fields(self):
		self.mount_info_host.set_text("")
		self.mount_info_export.get_child().set_text("")
		self.mount_info_export.set_model(gtk.ListStore(gobject.TYPE_STRING))
		self.mount_info_type.set_text("")
		self.mount_info_mountpoint.set_text("")
		self.mount_info_mountopts.set_text("")
		self.mount_info_host.set_sensitive(gtk.FALSE)
		self.mount_info_export.set_sensitive(gtk.FALSE)
		self.mount_info_type.set_sensitive(gtk.FALSE)
		self.mount_info_mountpoint.set_sensitive(gtk.FALSE)
		self.mount_info_mountopts.set_sensitive(gtk.FALSE)

	def enable_all_fields(self):
		self.mount_info_host.set_text("")
		self.mount_info_export.get_child().set_text("")
		self.mount_info_export.set_model(gtk.ListStore(gobject.TYPE_STRING))
		self.mount_info_type.set_text("")
		self.mount_info_mountpoint.set_text("")
		self.mount_info_mountopts.set_text("")
		self.mount_info_host.set_sensitive(gtk.TRUE)
		self.mount_info_export.set_sensitive(gtk.TRUE)
		self.mount_info_type.set_sensitive(gtk.TRUE)
		self.mount_info_mountpoint.set_sensitive(gtk.TRUE)
		self.mount_info_mountopts.set_sensitive(gtk.TRUE)

	def refresh_list_at_top(self):
		self.treedata = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
		for i in range(0, len(self.netmounts)):
			self.treedata.append([i, self.netmounts[i]['host'], self.netmounts[i]['export'], self.netmounts[i]['type'], self.netmounts[i]['mountpoint'], self.netmounts[i]['mountopts']])
		self.treedatasort = gtk.TreeModelSort(self.treedata)
		self.treeview.set_model(self.treedatasort)
		self.treeview.show_all()

	def selection_changed(self, treeview, data=None):
		treeselection = treeview.get_selection()
		treemodel, treeiter = treeselection.get_selected()
		row = treemodel.get(treeiter, 0)
		self.active_entry = row[0]
		mount = self.netmounts[self.active_entry]
		self.enable_all_fields()
		self.mount_info_host.set_text(mount['host'])
		self.mount_info_export.set_model(gtk.ListStore(gobject.TYPE_STRING))
		self.mount_info_export.get_child().set_text(mount['export'])
		self.mount_info_type.set_text(mount['type'])
		self.mount_info_mountpoint.set_text(mount['mountpoint'])
		self.mount_info_mountopts.set_text(mount['mountopts'])
		self.mount_button_update.set_sensitive(gtk.TRUE)
		self.mount_button_delete.set_sensitive(gtk.TRUE)
		self.mount_button_populate.set_sensitive(gtk.TRUE)

	def new_mount(self, button, data=None):
		self.mount_info_host.set_text("")
		self.mount_info_export.get_child().set_text("")
		self.mount_info_export.set_model(gtk.ListStore(gobject.TYPE_STRING))
		self.mount_info_type.set_text("")
		self.mount_info_mountpoint.set_text("")
		self.mount_info_mountopts.set_text("")
		self.active_entry = -1
		self.mount_button_update.set_sensitive(gtk.TRUE)
		self.mount_button_delete.set_sensitive(gtk.FALSE)
		self.mount_button_populate.set_sensitive(gtk.TRUE)
		self.enable_all_fields()
		self.mount_info_host.grab_focus()

	def update_mount(self, button, data=None):
		if self.active_entry == -1:
			self.netmounts.append({ 'host': self.mount_info_host.get_text(), 'export': self.mount_info_export.get_child().get_text(), 'type': self.mount_info_type.get_text(), 'mountpoint': self.mount_info_mountpoint.get_text(), 'mountopts': self.mount_info_mountopts.get_text() })
			self.mount_info_host.set_text("")
			self.mount_info_export.get_child().set_text("")
			self.mount_info_export.set_model(gtk.ListStore(gobject.TYPE_STRING))
			self.mount_info_type.set_text("")
			self.mount_info_mountpoint.set_text("")
			self.mount_info_mountopts.set_text("")
			self.active_entry = -1
			self.mount_button_update.set_sensitive(gtk.FALSE)
			self.mount_button_delete.set_sensitive(gtk.FALSE)
			self.mount_button_populate.set_sensitive(gtk.FALSE)
		else:
			self.netmounts[self.active_entry]['host'] = self.mount_info_host.get_text()
			self.netmounts[self.active_entry]['export'] = self.mount_info_export.get_child().get_text()
			self.netmounts[self.active_entry]['type'] = self.mount_info_type.get_text()
			self.netmounts[self.active_entry]['mountpoint'] = self.mount_info_mountpoint.get_text()
			self.netmounts[self.active_entry]['mountopts'] = self.mount_info_mountopts.get_text()
		self.refresh_list_at_top()
		self.disable_all_fields()

	def delete_mount(self, button, data=None):
		self.netmounts.pop(self.active_entry)
		self.mount_info_host.set_text("")
		self.mount_info_export.get_child().set_text("")
		self.mount_info_export.set_model(gtk.ListStore(gobject.TYPE_STRING))
		self.mount_info_type.set_text("")
		self.mount_info_mountpoint.set_text("")
		self.mount_info_mountopts.set_text("")
		self.active_entry = -1
		self.mount_button_update.set_sensitive(gtk.FALSE)
		self.mount_button_delete.set_sensitive(gtk.FALSE)
		self.mount_button_populate.set_sensitive(gtk.FALSE)
		self.refresh_list_at_top()
		self.disable_all_fields()

	def populate_exports(self, button, data=None):
		host = self.mount_info_host.get_text()
		oldtext = self.mount_info_export.get_child().get_text()
		if GLIUtility.is_ip(host) or GLIUtility.is_hostname(host):
			remotemounts = commands.getoutput("/usr/sbin/showmount -e " + host + " 2>&1 | egrep '^/' | cut -d ' ' -f 1 && echo")
			mountlist = gtk.ListStore(gobject.TYPE_STRING)
			self.mount_info_export.set_model(mountlist)
			while remotemounts.find("\n") != -1:
				index = remotemounts.find("\n") + 1
				remotemount = remotemounts[:index]
				remotemounts = remotemounts[index:]
				remotemount = string.strip(remotemount)
				mountlist.append([remotemount])
			self.mount_info_export.get_child().set_text(oldtext)
		else:
			msgdialog = Widgets.Widgets().error_Box("Invalid Host or IP", "You must specify a valid hostname or IP address to scan for exports")
			result = msgdialog.run()
			if result == gtk.RESPONSE_ACCEPT:
				msgdialog.destroy()

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
		self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
		self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
		self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
		self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
		self.netmounts = copy.deepcopy(self.controller.install_profile.get_network_mounts())
		self.refresh_list_at_top()
		self.disable_all_fields()

	def deactivate(self):
		self.controller.install_profile.set_network_mounts(self.netmounts)
		return True
