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
    added_devices=[]
    #gateway_set=False
    gateway_info=(None,None)
    
    # Operations
    def __init__(self, controller):
	GLIScreen.GLIScreen.__init__(self, controller)

        content_str = """
This is where you setup Networking.
[short explanation of what to do here]
"""
	self.ethernet_devices = self.get_ethernet_devices()
	
	vert = gtk.VBox(False, 0)
	vert.set_border_width(10)
	
	self.treedata = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
	for i in range(0, len(self.networking)):
		self.treedata.append([i, self.networking[i]['ip'], self.networking[i]['mask'], self.networking[i]['device'], self.networking[i]['broadcast'], self.networking[i]['gateway']])
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
		column.set_resizable(True)
		column.set_sort_column_id(col_num)
		self.treeview.append_column(column)
		col_num += 1
	self.treewindow = gtk.ScrolledWindow()
	self.treewindow.set_size_request(-1, 125)
	self.treewindow.set_shadow_type(gtk.SHADOW_IN)
	self.treewindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	self.treewindow.add(self.treeview)
	vert.pack_start(self.treewindow, expand=False, fill=False, padding=0)

	self.networking_info_box = gtk.HBox(False, 0)
	networking_info_table = gtk.Table(5, 5, False)
	networking_info_table.set_col_spacings(10)
	networking_info_table.set_row_spacings(6)
	
	# Device
	networking_info_device_label = gtk.Label("Devices:")
	networking_info_device_label.set_alignment(0.0, 0.5)
	networking_info_table.attach(networking_info_device_label, 0, 1, 0, 1)
	self.networking_info_device = gtk.combo_box_entry_new_text()
	
	# Device drop-down
	for device in self.ethernet_devices:
		self.networking_info_device.append_text(device)
	self.networking_info_device.set_active(0)
	networking_info_table.attach(self.networking_info_device, 1, 2, 0, 1)
	
	# or add your own device
	networking_other_device_label=gtk.Label("Select a device or type in your own")
	networking_other_device_label.set_alignment(0.0,0.5)
	networking_info_table.attach(networking_other_device_label,2,3,0,1)
	
	# IP Address
	networking_info_ip_label = gtk.Label("IP Address:")
	networking_info_ip_label.set_alignment(0.0, 0.5)
	networking_info_table.attach(networking_info_ip_label, 0, 1, 1, 2)
	self.networking_info_ip = gtk.Entry()
	self.networking_info_ip.set_width_chars(25)
	networking_info_table.attach(self.networking_info_ip, 1, 2, 1, 2)
	
	widgets=Widgets()
	# DHCP Checkbox
	self.dhcp_checkbox=gtk.CheckButton("DHCP")
	self.dhcp_checkbox.connect("toggled", self.checkbutton, "check button 1")
	networking_info_table.attach(widgets.hBoxIt2(False,0,self.dhcp_checkbox), 2, 3, 1, 2)

	
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
	self.networking_info_box.pack_start(networking_info_table, expand=False, fill=False)
	vert.pack_start(self.networking_info_box, expand=False, fill=False, padding=10)

	# The bottom box of buttons
	networking_button_box = gtk.HBox(False, 0)
	networking_button_new = gtk.Button(" _New ")
	networking_button_new.connect("clicked", self.new_device)
	networking_button_box.pack_start(networking_button_new, expand=False, fill=False, padding=10)
	self.networking_button_update = gtk.Button(" _Update ")
	self.networking_button_update.connect("clicked", self.update_device)
	self.networking_button_update.set_sensitive(False)
	networking_button_box.pack_start(self.networking_button_update, expand=False, fill=False, padding=10)
	self.networking_button_delete = gtk.Button(" _Delete ")
	self.networking_button_delete.connect("clicked", self.delete_device)
	self.networking_button_delete.set_sensitive(False)
	networking_button_box.pack_start(self.networking_button_delete, expand=False, fill=False, padding=10)
	
	vert.pack_start(networking_button_box, expand=False, fill=False, padding=10)
	
	# The hostname and dnsdomainname box
	naming_button_box = gtk.HBox(False, 0)
	naming_table = gtk.Table(5, 5, False)
	naming_table.set_col_spacings(10)
	naming_table.set_row_spacings(6)
	
	# hostname
	hostname_label = gtk.Label("Hostname:")
	hostname_label.set_alignment(0.0, 0.5)
	naming_table.attach(hostname_label, 0, 1, 0, 1)
	self.hostname = gtk.Entry()
	self.hostname.set_width_chars(25)
	naming_table.attach(self.hostname, 1, 2, 0, 1)
	hostname_explain=gtk.Label("The name of your computer, ex, 'tux'")
	naming_table.attach(widgets.hBoxIt2(False,0,hostname_explain), 2, 3, 0, 1)
	
	# dnsdomainname
	dnsdomainname_label = gtk.Label("DNS Domain Name:")
	dnsdomainname_label.set_alignment(0.0, 0.5)
	naming_table.attach(dnsdomainname_label, 0, 1, 1, 2)
	self.dnsdomainname = gtk.Entry()
	self.dnsdomainname.set_width_chars(25)
	naming_table.attach(self.dnsdomainname, 1, 2, 1, 2)
	dnsdomainname_explain=gtk.Label("ex. gentoo.org")
	naming_table.attach(widgets.hBoxIt2(False,0,dnsdomainname_explain), 2, 3, 1, 2)
	
	naming_button_box.pack_start(naming_table, expand=False, fill=False)
	vert.pack_start(naming_button_box, expand=False, fill=False, padding=10)
	
	self.add_content(vert)

    def disable_all_fields(self):
	if(self.networking_info_ip.get_text()!="dhcp"):
	    self.dhcp_checkbox.set_sensitive(False)
	    self.networking_info_ip.set_text("")
	    
	
	self.networking_info_ip.set_sensitive(False)
	    
	self.networking_info_broadcast.set_text("")
	self.networking_info_gateway.set_text("")
	self.mask.set_text("")
	
	self.mask.set_sensitive(False)
	self.networking_info_broadcast.set_sensitive(False)
	self.networking_info_gateway.set_sensitive(False)
	self.networking_info_device.set_sensitive(False)

    def enable_all_fields(self):
	self.networking_info_broadcast.set_text("")
	self.networking_info_gateway.set_text("")
	self.mask.set_text("")
	self.networking_info_ip.set_text("")
	self.networking_info_device.get_child().set_text("")
	
	if self.gateway_info[0]==None: self.networking_info_gateway.set_sensitive(True)
	else: self.networking_info_gateway.set_sensitive(False)
	
	self.networking_info_broadcast.set_sensitive(True)
	self.networking_info_device.set_sensitive(True)
	self.dhcp_checkbox.set_sensitive(True)
	self.mask.set_sensitive(True)
	self.networking_info_ip.set_sensitive(True)

    def refresh_list_at_top(self):
	self.treedata = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
	for i in range(0, len(self.networking)):
		self.treedata.append([i, self.networking[i]['device'], self.networking[i]['ip'],
				      self.networking[i]['mask'], self.networking[i]['broadcast'], 
				      self.networking[i]['gateway']])
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

	self.networking_button_update.set_sensitive(True)
	self.networking_button_delete.set_sensitive(True)
	
	self.networking_info_device.get_child().set_text(mount['device'])
	self.networking_info_ip.set_text(str(mount['ip']))
	
	if(self.networking_info_ip.get_text()=="dhcp"):   
	    self.networking_info_broadcast.set_sensitive(False)
	    self.networking_info_gateway.set_sensitive(False)
	    self.networking_info_ip.set_sensitive(False)
	    self.mask.set_sensitive(False)
	    # now check the checkbox
	    self.dhcp_checkbox.set_active(True)
	else:
	    self.dhcp_checkbox.set_active(False)	
	
	self.networking_info_device.get_child().set_text(mount['device'])
	self.networking_info_ip.set_text(str(mount['ip']))
	self.mask.set_text(str(mount['mask']))
	self.networking_info_broadcast.set_text(str(mount['broadcast']))
	print self.gateway_info[0]
	if self.networking_info_ip.get_text()!="dhcp" and (str(self.gateway_info[0])==str(mount['device']) or str(self.gateway_info[0])==str(None)): 
	    self.networking_info_gateway.set_sensitive(True)
	    self.networking_info_gateway.set_text(str(mount['gateway']))
	else: self.networking_info_gateway.set_sensitive(False)

    def new_device(self, button, data=None):
	self.active_entry = -1
	self.networking_button_update.set_sensitive(True)
	self.networking_button_delete.set_sensitive(False)
	
	# if the checkbutton is checked, uncheck it cause its a new device!
	if(self.dhcp_checkbox.get_active()):
	    self.dhcp_checkbox.set_active(False)
	    
	self.networking_info_broadcast.set_text("")
	self.networking_info_gateway.set_text("")
	self.mask.set_text("")
	self.networking_info_ip.set_text("")
	self.networking_info_device.get_child().set_text("")
	
	if self.gateway_info[0]==None: self.networking_info_gateway.set_sensitive(True)
	else: self.networking_info_gateway.set_sensitive(False)
	    
	self.networking_info_broadcast.set_sensitive(True)
	self.networking_info_device.set_sensitive(True)
	self.dhcp_checkbox.set_sensitive(True)
	self.mask.set_sensitive(True)
	self.networking_info_ip.set_sensitive(True)
	
	self.networking_info_device.grab_focus()

    def update_device(self, button, data=None):   
	    #if self.active_entry == -1:
	    if self.networking_info_device.get_child().get_text() not in self.added_devices:
		# new entry
		    self.networking.append({ 'device': self.networking_info_device.get_child().get_text(),
					    'ip': self.networking_info_ip.get_text(), 
					    'mask': self.mask.get_text(),
					    'broadcast': self.networking_info_broadcast.get_text(), 
					    'gateway': self.networking_info_gateway.get_text() })
		    self.active_entry = -1
		    self.added_devices.append(self.networking_info_device.get_child().get_text())
		    if self.networking_info_gateway.get_text() != "":
			print "got here"
			print self.networking_info_device.get_child().get_text()
			self.gateway_info=(self.networking_info_device.get_child().get_text(),self.networking_info_gateway.get_text())
	    else:
		#update entry
		widgets=Widgets()
		msgdialog=widgets.error_Box2("Duplicate Device","Replace existing data?")
		result = msgdialog.run()
		if result == gtk.RESPONSE_ACCEPT:
		    msgdialog.destroy()
		    self.networking[self.active_entry]['device'] = self.networking_info_device.get_child().get_text()
		    self.networking[self.active_entry]['ip'] = self.networking_info_ip.get_text()
		    self.networking[self.active_entry]['mask'] = self.mask.get_text()
		    self.networking[self.active_entry]['broadcast'] = self.networking_info_broadcast.get_text()
		    self.networking[self.active_entry]['gateway'] = self.networking_info_gateway.get_text()
		    if self.gateway_info[0]==None and self.networking[self.active_entry]['gateway']!="":
			self.gateway_info=(self.networking[self.active_entry]['device'],self.networking[self.active_entry]['gateway'])
		    elif self.gateway_info[0]!=None and self.networking[self.active_entry]['gateway']=="":
			self.gateway_info=(None,None)
		else:
		    msgdialog.destroy()
		    print "nothing changed"   
		    
	    self.networking_button_update.set_sensitive(False)
	    self.networking_button_delete.set_sensitive(False)
	    self.refresh_list_at_top()
	    self.disable_all_fields()

    def delete_device(self, button, data=None):
	# add in what would happen if you deleted a device that was gateway.
	if self.networking[self.active_entry]['gateway']!="":
	    self.gateway_info=(None,None)
	    
	self.added_devices.remove(self.networking_info_device.get_child().get_text())
	print self.networking
	self.networking_info_device.set_sensitive(False)
	#print self.added_devices
	self.networking.pop(self.active_entry)
	#print self.networking
	self.active_entry = -1
	self.networking_button_update.set_sensitive(False)
	self.networking_button_delete.set_sensitive(False)
	#self.added_devices.remove(self.ethernet_devices[self.networking_info_device.get_active()])
	self.refresh_list_at_top()
	self.disable_all_fields()

    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = True
	self.controller.SHOW_BUTTON_HELP    = True
	self.controller.SHOW_BUTTON_BACK    = True
	self.controller.SHOW_BUTTON_FORWARD = True
	self.controller.SHOW_BUTTON_FINISH  = False
	self.refresh_list_at_top()
	self.disable_all_fields()
	# load the saved data ( if any )
	self.hostname.set_text(self.controller.install_profile.get_hostname())
	self.dnsdomainname.set_text(self.controller.install_profile.get_domainname())
	interfaces=self.controller.install_profile.get_network_interfaces()
	print interfaces
	default_gateway=self.controller.install_profile.get_default_gateway()
	for count in range(len(interfaces.keys())):
	    print "in loading phase"
	    if interfaces.keys()[count] not in self.ethernet_devices:
		self.ethernet_devices.append(interfaces.keys()[count])
	    if interfaces.keys()[count] not in self.added_devices:
		host,export,mountpoint=interfaces[interfaces.keys()[count]]
		device,mountopts=default_gateway
		if device == interfaces.keys()[count]:
		    self.networking.append({ 'device':interfaces.keys()[count],'ip':host,'mask':export,'broadcast':mountpoint,'gateway':mountopts})
		    self.gateway_info=default_gateway
		else: self.networking.append({ 'device':interfaces.keys()[count],'ip':host,'mask':export,'broadcast':mountpoint,'gateway':""})
		self.added_devices.append(interfaces.keys()[count])		
		self.refresh_list_at_top()
	self.disable_all_fields()

    def deactivate(self):
	# fix the structure to correctly get into structure for setting
	interfaces={}
	for count in range(len(self.networking)):
	    if self.networking[count]['ip']!="dhcp":
		interfaces[self.networking[count]['device']]=(self.networking[count]['ip'],self.networking[count]['broadcast'],self.networking[count]['mask'])
	    else:
		interfaces[self.networking[count]['device']]=(self.networking[count]['ip'],None,None)
	print interfaces
	return_value = False
	# set the hostname and dnsdomainname
	self.controller.install_profile.set_hostname(None,self.hostname.get_text(),None)
	self.controller.install_profile.set_domainname(None,self.dnsdomainname.get_text(),None)
	
	try:
	    if len(interfaces)!=0:
		self.controller.install_profile.set_network_interfaces(interfaces)
		if self.networking[count]['ip']!="dhcp":
		    self.controller.install_profile.set_default_gateway(None,self.gateway_info[1],{'interface':self.gateway_info[0]})
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
	    # simulate a disable
	    self.networking_info_gateway.set_text("")
	    self.networking_info_broadcast.set_text("None")
	    self.mask.set_text("None")
	    self.networking_info_ip.set_sensitive(False)
	    self.mask.set_sensitive(False)
	    self.networking_info_broadcast.set_sensitive(False)
	    self.networking_info_gateway.set_sensitive(False)	    
	else:
	    self.networking_info_ip.set_text("")
	    self.enable_all_fields()
    
    def add_device(self,widget,data=None):
	self.ethernet_devices.append(self.networking_info_other_device.get_text())
	self.networking_info_device.append_text(self.networking_info_other_device.get_text())
	self.networking_info_device.set_active(len(self.ethernet_devices)-1)
