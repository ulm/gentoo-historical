import gtk,gobject
import os
import re
import GLIScreen
import GLIUtility
import commands, string
import copy
from Widgets import Widgets

class Panel(GLIScreen.GLIScreen):
    """
    The Networking section of the installer.
    
    @author:    John N. Laliberte <allanonl@bu.edu>
    @license:   GPL
    (starting from agaffney's template of NetworkMounts)
    """
    # Attributes:
    title="Networking Settings"
    columns = []
    networking = []
    active_entry = -1
    
    # Operations
    def __init__(self, controller):
	GLIScreen.GLIScreen.__init__(self, controller)

        content_str = """
This is where you setup Networking.
[short explanation of what to do here]
"""
	self.ethernet_devices = self.get_ethernet_devices()
	
	vert = gtk.VBox(gtk.FALSE, 0)
	vert.set_border_width(10)
	
	self.treedata = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
	for i in range(0, len(self.networking)):
		self.treedata.append([i, self.networking[i]['host'], self.networking[i]['export'], self.networking[i]['type'], self.networking[i]['mountpoint'], self.networking[i]['mountopts']])
	self.treedatasort = gtk.TreeModelSort(self.treedata)
	self.treeview = gtk.TreeView(self.treedatasort)
	self.treeview.connect("cursor-changed", self.selection_changed)
	self.columns.append(gtk.TreeViewColumn("Device    ", gtk.CellRendererText(), text=1))
	self.columns.append(gtk.TreeViewColumn("IP Address", gtk.CellRendererText(), text=2))
	self.columns.append(gtk.TreeViewColumn("Mask      ", gtk.CellRendererText(), text=3))
	self.columns.append(gtk.TreeViewColumn("Broadcast ", gtk.CellRendererText(), text=4))
	self.columns.append(gtk.TreeViewColumn("Default Gateway", gtk.CellRendererText(), text=5))
	col_num = 0
	for column in self.columns:
		column.set_resizable(gtk.TRUE)
		column.set_sort_column_id(col_num)
		self.treeview.append_column(column)
		col_num += 1
	self.treewindow = gtk.ScrolledWindow()
	self.treewindow.set_size_request(-1, 200)
	self.treewindow.set_shadow_type(gtk.SHADOW_IN)
	self.treewindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	self.treewindow.add(self.treeview)
	vert.pack_start(self.treewindow, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)

	self.networking_info_box = gtk.HBox(gtk.FALSE, 0)
	networking_info_table = gtk.Table(5, 3, gtk.FALSE)
	networking_info_table.set_col_spacings(10)
	networking_info_table.set_row_spacings(6)
	
	# Device
	networking_info_device_label = gtk.Label("Device:")
	networking_info_device_label.set_alignment(0.0, 0.5)
	networking_info_table.attach(networking_info_device_label, 0, 1, 0, 1)
	self.networking_info_device = gtk.combo_box_new_text()
	# Device drop-down
	for device in self.ethernet_devices:
		self.networking_info_device.append_text(device)
	self.networking_info_device.set_active(0)
	networking_info_table.attach(self.networking_info_device, 1, 2, 0, 1)
	
	# IP Address
	networking_info_ip_label = gtk.Label("IP Address:")
	networking_info_ip_label.set_alignment(0.0, 0.5)
	networking_info_table.attach(networking_info_ip_label, 0, 1, 1, 2)
	widgets=Widgets()
	# DHCP Checkbox
	self.dhcp_checkbox=gtk.CheckButton("DHCP")
	self.dhcp_checkbox.connect("toggled", self.checkbutton, "check button 1")
	networking_info_table.attach(widgets.hBoxIt2(gtk.TRUE,0,self.dhcp_checkbox), 2, 3, 0, 1)
	self.networking_info_ip = gtk.Entry()
	self.networking_info_ip.set_width_chars(25)
	networking_info_table.attach(self.networking_info_ip, 1, 2, 1, 2)
	
	# Mask
	networking_info_mask_label = gtk.Label("Mask:")
	networking_info_mask_label.set_alignment(0.0, 0.5)
	networking_info_table.attach(networking_info_mask_label, 0, 1, 2, 3)
	self.mask=gtk.Entry()
	self.mask.set_width_chars(25)
	networking_info_table.attach(self.mask, 1, 2, 2, 3)
	
	# Broadcast
	networking_info_broadcast_label = gtk.Label("Broadcast:")
	networking_info_broadcast_label.set_alignment(0.0, 0.5)
	networking_info_table.attach(networking_info_broadcast_label, 0, 1, 3, 4)
	self.networking_info_broadcast = gtk.Entry()
	self.networking_info_broadcast.set_width_chars(30)
	networking_info_table.attach(self.networking_info_broadcast, 1, 2, 3, 4)
	
	# Default Gateway
	networking_info_gateway_label = gtk.Label("Default Gateway:")
	networking_info_gateway_label.set_alignment(0.0, 0.5)
	networking_info_table.attach(networking_info_gateway_label, 0, 1, 4, 5)
	self.networking_info_gateway = gtk.Entry()
	self.networking_info_gateway.set_width_chars(30)
	networking_info_table.attach(self.networking_info_gateway, 1, 2, 4, 5)
	
	# Pack it all
	self.networking_info_box.pack_start(networking_info_table, expand=gtk.FALSE, fill=gtk.FALSE)
	vert.pack_start(self.networking_info_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

	# The bottom box of buttons
	networking_button_box = gtk.HBox(gtk.FALSE, 0)
	networking_button_new = gtk.Button(" _New ")
	networking_button_new.connect("clicked", self.new_device)
	networking_button_box.pack_start(networking_button_new, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
	self.networking_button_update = gtk.Button(" _Update ")
	self.networking_button_update.connect("clicked", self.update_device)
	self.networking_button_update.set_sensitive(gtk.FALSE)
	networking_button_box.pack_start(self.networking_button_update, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
	self.networking_button_delete = gtk.Button(" _Delete ")
	self.networking_button_delete.connect("clicked", self.delete_device)
	self.networking_button_delete.set_sensitive(gtk.FALSE)
	networking_button_box.pack_start(self.networking_button_delete, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
	
	vert.pack_start(networking_button_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

	self.add_content(vert)

    def disable_all_fields(self):
	if(self.networking_info_ip.get_text()!="dhcp"):
	    self.dhcp_checkbox.set_sensitive(gtk.FALSE)
	    self.networking_info_ip.set_text("")
	
	self.networking_info_ip.set_sensitive(gtk.FALSE)
	    
	self.networking_info_broadcast.set_text("")
	self.networking_info_gateway.set_text("")
	self.mask.set_text("")
	
	self.mask.set_sensitive(gtk.FALSE)
	self.networking_info_broadcast.set_sensitive(gtk.FALSE)
	self.networking_info_gateway.set_sensitive(gtk.FALSE)
	self.networking_info_device.set_sensitive(gtk.FALSE)
	

    def enable_all_fields(self):
	self.networking_info_broadcast.set_text("")
	self.networking_info_gateway.set_text("")
	self.mask.set_text("")
	self.networking_info_ip.set_text("")
	
	
	self.networking_info_broadcast.set_sensitive(gtk.TRUE)
	self.networking_info_gateway.set_sensitive(gtk.TRUE)
	self.networking_info_device.set_sensitive(gtk.TRUE)
	self.dhcp_checkbox.set_sensitive(gtk.TRUE)
	self.mask.set_sensitive(gtk.TRUE)
	self.networking_info_ip.set_sensitive(gtk.TRUE)

    def refresh_list_at_top(self):
	self.treedata = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
	for i in range(0, len(self.networking)):
		self.treedata.append([i, self.networking[i]['type'], self.networking[i]['host'],
				      self.networking[i]['export'], self.networking[i]['mountpoint'], 
				      self.networking[i]['mountopts']])
	self.treedatasort = gtk.TreeModelSort(self.treedata)
	self.treeview.set_model(self.treedatasort)
	self.treeview.show_all()

    def selection_changed(self, treeview, data=None):
	treeselection = treeview.get_selection()
	treemodel, treeiter = treeselection.get_selected()
	row = treemodel.get(treeiter, 0)
	self.active_entry = row[0]
	mount = self.networking[self.active_entry]
	self.enable_all_fields()
	# find the correct device and select it!
	for count in range(len(self.ethernet_devices)):
	    if self.ethernet_devices[count] == mount['type']:
		# this is it!
		self.networking_info_device.set_active(count)
		
	self.networking_info_ip.set_text(mount['host'])
	self.mask.set_text(mount['export'])
	self.networking_info_broadcast.set_text(mount['mountpoint'])
	self.networking_info_gateway.set_text(mount['mountopts'])
	self.networking_button_update.set_sensitive(gtk.TRUE)
	self.networking_button_delete.set_sensitive(gtk.TRUE)
	if(self.networking_info_ip.get_text()=="dhcp"):
	    self.networking_info_broadcast.set_sensitive(gtk.FALSE)
	    self.networking_info_gateway.set_sensitive(gtk.FALSE)
	    self.networking_info_ip.set_sensitive(gtk.FALSE)
	    self.mask.set_sensitive(gtk.FALSE)
	    # now check the checkbox
	    self.dhcp_checkbox.set_active(gtk.TRUE)

    def new_device(self, button, data=None):
	self.active_entry = -1
	self.networking_button_update.set_sensitive(gtk.TRUE)
	self.networking_button_delete.set_sensitive(gtk.FALSE)
	# if the checkbutton is checked, uncheck it cause its a new device!
	if(self.dhcp_checkbox.get_active()):
	    self.dhcp_checkbox.set_active(gtk.FALSE)
	    
	self.enable_all_fields()
	self.networking_info_device.grab_focus()

    def update_device(self, button, data=None):
	current_devices=[]
	for item in self.networking:
	    current_devices.append(item['type'])
	    
	if self.ethernet_devices[self.networking_info_device.get_active()] not in current_devices:
	    if self.active_entry == -1:
		    self.networking.append({ 'type': self.ethernet_devices[self.networking_info_device.get_active()],
					    'host': self.networking_info_ip.get_text(), 
					    'export': self.mask.get_text(),
					    'mountpoint': self.networking_info_broadcast.get_text(), 
					    'mountopts': self.networking_info_gateway.get_text() })
		    self.active_entry = -1
		    self.networking_button_update.set_sensitive(gtk.FALSE)
		    self.networking_button_delete.set_sensitive(gtk.FALSE)
	    self.refresh_list_at_top()
	    self.disable_all_fields()
	else:
	    # update it
    	    widgets=Widgets()
	    msgdialog=widgets.error_Box2("Duplicate Entry","Replace existing data?")
	    result = msgdialog.run()
	    if result == gtk.RESPONSE_ACCEPT:
		msgdialog.destroy()
		self.networking[self.active_entry]['type'] = self.ethernet_devices[self.networking_info_device.get_active()]
		self.networking[self.active_entry]['host'] = self.networking_info_ip.get_text()
		self.networking[self.active_entry]['export'] = self.mask.get_text()
		self.networking[self.active_entry]['mountpoint'] = self.networking_info_broadcast.get_text()
		self.networking[self.active_entry]['mountopts'] = self.networking_info_gateway.get_text()
		self.refresh_list_at_top()
		self.disable_all_fields()
	    else:
		msgdialog.destroy()
		print "nothing changed"

    def delete_device(self, button, data=None):
	self.networking.pop(self.active_entry)
	self.active_entry = -1
	self.networking_button_update.set_sensitive(gtk.FALSE)
	self.networking_button_delete.set_sensitive(gtk.FALSE)
	self.refresh_list_at_top()
	self.disable_all_fields()

    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
	#self.networking = copy.deepcopy(self.controller.install_profile.get_network_mounts())
	self.refresh_list_at_top()
	self.disable_all_fields()

    def deactivate(self):
	#self.controller.install_profile.set_network_mounts(self.networking)
	# fix the structure to correctly get into structure for setting
	interfaces={}
	for count in range(len(self.networking)):
	    interfaces[self.networking[count]['type']]=(self.networking[count]['host'],self.networking[count]['export'],self.networking[0]['mountpoint'])
	#self.networking[0]['mountopts']
	print interfaces
	return_value = False
	try:
	    self.controller.install_profile.set_network_interfaces(interfaces)
	    for count in range(len(self.networking)):
		if interfaces[count]['mountopts']!="":
		    # if its not blank, its the default gateway!
		    self.controller.install_profile.set_default_gateway(None,self.networking[count]['mountopts'],{'interface':self.networking[count]['type']})
	    return_value = True
	except:
	    widgets=Widgets()
	    msgdialog=widgets.error_Box("Malformed IP","Malformed IP address, please fix it!")
	    result = msgdialog.run()
	    if result == gtk.RESPONSE_ACCEPT:
		msgdialog.destroy()
	    return_value = False
	#for item in self.networking:
	#    print item
	return return_value
    
    def get_ethernet_devices(self):
	    put, get = os.popen4("ifconfig -a | egrep -e '^[^ ]'|sed -e 's/ .\+$//'")
	    #list={}
	    devices=[]
	    for device in get.readlines():
		device=device.strip()
		if device!="lo":
		    devices.append(device)
		    #list[device]=("","","")
	    #return list
	    return devices
	    
    def checkbutton(self,widget, data=None):
	print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
	if(("OFF", "ON")[widget.get_active()]=="ON"):
	    self.networking_info_ip.set_text("dhcp")
	    self.disable_all_fields()
	    self.networking_info_broadcast.set_text("None")
	    self.networking_info_gateway.set_text("None")
	    self.mask.set_text("None")
	else:
	    self.networking_info_ip.set_text("")
	    self.enable_all_fields()
	    
