import gtk
import os
import re
import GLIScreen
from Widgets import Widgets

class Panel(GLIScreen.GLIScreen):
    """
    The Networking section of the installer.
    
    @author:    John N. Laliberte <allanonl@bu.edu>
    @license:   GPL
    """
    # Attributes:
    title="Networking Settings"
    # Operations
    def __init__(self, controller):
	GLIScreen.GLIScreen.__init__(self, controller)

        vert    = gtk.VBox(gtk.FALSE, 10) # This box is content so it should fill space to force title to top
	horiz   = gtk.HBox(gtk.FALSE, 10)

        content_str = """
This is where you setup Networking.
[short explanation of what to do here]
"""
	# pack the description
	vert.pack_start(gtk.Label(content_str), expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

	widgets=Widgets()
        
	self.interfaces={}
	self.default_gateway={}
	
	self.textBoxen=[] # the list of textboxen so we can get data later	 
	self.lastSelected="NOT_SET" #set default selected device
	
	# ethernet device drop-down
	self.interfaces=self.get_ethernet_devices()
	self.menu=widgets.createComboEntry(self,"networkdevs",self.interfaces.keys())
	ethernet_menu_hBoxed = widgets.hBoxThese(gtk.FALSE,10,[gtk.Label("Current Devices"),self.menu])
	ethernet_menu_hBoxed=widgets.hBoxIt(ethernet_menu_hBoxed)
	
	# static frame creation
	static_frame = gtk.Frame()
	static_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
	static_frame.show()
	
	# static table
	static_table=gtk.Table(4,2,gtk.FALSE)
	static_table.set_col_spacing(0,10)
	
	# static table - radio button select
	static_radio_button=widgets.radioButton(None,self.callback,"Static Ethernet",1)
	#static_radio_button.set_active(gtk.TRUE)
	self.static_radio_button=static_radio_button
	static_radio_button_hBoxed=widgets.hBoxIt(static_radio_button) 	
	
	# static table - populate the table with labels and entry boxes
	list=["Ip Address","Mask","Broadcast","Default Gateway"]
	self.fill_left_static_table(static_table,list)
	self.fill_right_static_table(static_table,list)
	static_table_hBoxed=widgets.hBoxIt2(gtk.TRUE,20,static_table)
	
	# static table - checkbox for default gateway
	static_default_gateway = gtk.CheckButton("Default gateway")
	static_default_gateway.connect("toggled", self.defaultcheckcall, "default_check")
	# make it so its disabled to begin with.
	self.textBoxen[3].set_sensitive(gtk.FALSE)
	static_default_gateway_hBoxed = widgets.hBoxThese(gtk.FALSE,10,[static_default_gateway])
	# set it so there is no default gateway to begin with
	self.static_default_gateway_status=0
	
	# dhcp frame creation
	dhcp_frame = gtk.Frame()
	dhcp_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
	dhcp_frame.show()
	
	# dhcp table
	dhcp_table=gtk.Table(4,2,gtk.FALSE)
	dhcp_table.set_col_spacing(0,10)
	dhcp_table_hBoxed=widgets.hBoxIt2(gtk.TRUE,20,dhcp_table)
	
	# dhcp table - radio button select
	dhcp_radio_button=widgets.radioButton(static_radio_button,self.callback,"Dhcp Ethernet",1)
	dhcp_radio_button.set_active(gtk.TRUE)
	self.dhcp_radio_button=dhcp_radio_button
	dhcp_radio_button_hBoxed=widgets.hBoxIt(dhcp_radio_button) 
	
	# add the radio buttons to the correct frames
	static_frame.add(widgets.vBoxThese(gtk.FALSE,0,[static_radio_button_hBoxed,
							static_table_hBoxed,
							static_default_gateway_hBoxed]))
	dhcp_frame.add(widgets.vBoxThese(gtk.FALSE,0,[dhcp_radio_button_hBoxed,dhcp_table_hBoxed]))
	
	# add the ethernet menu to the window
	vert.pack_start(ethernet_menu_hBoxed,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	# add static and dhcp frames to the window
	vert.pack_start(widgets.hBoxThese(gtk.TRUE,0,[static_frame,dhcp_frame]),expand=gtk.FALSE,fill=gtk.FALSE,padding=10)
	
	# hide the frames because there is no default selection
	# this is because they *may* not have an ethernet device in their system
	
	
	# make the alert
	#image=gtk.Image()
	#image.set_from_stock(gtk.STOCK_DIALOG_WARNING,10)
	#self.ip_label=gtk.Label("One of your ip addresses is not valid!")
	#packIt = widgets.hBoxThese(gtk.FALSE,10,[image,self.ip_label])
	#packItV=widgets.hBoxIt(packIt)
	#vert.pack_start(packItV,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	
	self.add_content(vert)
    
    def defaultcheckcall(self,widget,data=None):
	print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
	# ONLY enable it if nothing else has it set.
	if ("OFF","ON")[widget.get_active()]=="ON" and self.static_default_gateway_status==0:
	    self.textBoxen[3].set_sensitive(gtk.TRUE)
	    self.static_default_gateway_status=1
	if ("OFF","ON")[widget.get_active()]=="ON" and self.static_default_gateway_status==1:
	    widgets=Widgets()
	    print "should display error"
	    error=widgets.error_Box("Error","You have already selected a default gateway!")
	    result=error.run()
	    if(result==gtk.RESPONSE_ACCEPT):
		# close the box
		error.destroy()
	    
	else:
	    self.textBoxen[3].set_sensitive(gtk.FALSE)
	    # unset it here if its the selected one.
	    self.static_default_gateway_status=0
	
    def callback(self, widget, data=None):
      print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
      if ("OFF","ON")[widget.get_active()]=="ON" and data=="Dhcp Ethernet":
       # deactivate the boxen for entering data into.
       for count in range(len(self.textBoxen)-1):  
	   if count==0:
	       self.textBoxen[count].set_text("dhcp")
	   #else:
	       #self.textBoxen[count].set_text=""
	   self.textBoxen[count].set_sensitive(gtk.FALSE)
      else:
	  # activate them all
	for count in range(len(self.textBoxen)-1):
	    self.textBoxen[count].set_sensitive(gtk.TRUE)
    
    def set_networking_interfaces(self):
	try:
	    self.controller.install_profile.set_network_interfaces(self.interfaces)
	    self.ip_label.set_text("All ip addresses are valid.")
	except:
	    self.ip_label.set_text("One of your ip addresses is not valid!")
	
    # call back for when they change eth device
    def callback2(self,widget,data=None):
     #print "Last selected networking device: " + str(self.lastSelected)
     print "This callback is being called for: " + widget.get_text()
     
     if self.lastSelected!="NOT_SET":
	 # save the data
	 self.interfaces[self.lastSelected]=[self.textBoxen[0].get_text(),self.textBoxen[1].get_text(),
					     self.textBoxen[2].get_text() ]
	 print "Saved data: " + str(self.interfaces[self.lastSelected])
	 
	 # determine if default gateway is selected, if so, save it and adjust global
	 if self.static_default_gateway_status==1:
	     self.default_gateway[self.lastSelected]=self.textBoxen[3]
	 
     # reset last selected
     self.lastSelected=self.get_active_text(self.menu)
     
     if self.lastSelected!="NOT_SET":
	 # load the selected data ( -1 b/c do not include default gateway )
	 for count in range(len(self.textBoxen)-1):
	     self.textBoxen[count].set_text(self.interfaces[self.lastSelected][count])
     
	 # Do they have DHCP ? ( if so, must activate the checkbox.
	 first_entry=self.interfaces[self.lastSelected][0]
	 # if dhcp is active, and dhcp of the new selected is NOT dhcp, deselect
	 if self.dhcp_radio_button.get_active()==1 and first_entry!="dhcp":
	     # deselect dhcp
	     self.static_radio_button.set_active(1)
	 # if dhcp is not active, and dhcp of the new IS dhcp, select dhcp
	 if self.dhcp_radio_button.get_active()==0 and first_entry=="dhcp":
	     # select dhcp
	     self.dhcp_radio_button.set_active(1)
	
	 # is this device the default gateway? if so, activate the checkbox and load the data
	 if self.lastSelected in self.default_gateway.keys():
	     self.static_default_gateway_status.set_active(1)
	 else:
	     self.static_default_gateway_status.set_active(0)
	     
     #self.set_networking_interfaces()
     
    # call back for when they activate the entry box
    def entrycallback(self,widget,data=None):
     #print "got here"
     #print "widget name: "+widget.get_name()
     print "Entry contents of: %s\n" % data.get_text()
     
    def get_ethernet_devices(self):
	    put, get = os.popen4("ifconfig -a | egrep -e '^[^ ]'|sed -e 's/ .\+$//'")
	    list={}
	    for device in get.readlines():
		device=device.strip()
		if device!="lo":
		    list[device]=("","","")
	    return list
    
    def fill_left_static_table(self,table,list):
	""" Attaches the stuff into the left frame of the table.
	"""
	i=0
	for item in list:
	 table.attach(gtk.Label(item),0,1,i,i+1)
	 i=i+1
    
    def fill_right_static_table(self,table,list):
	""" Attaches the stuff into the right frame of the table
	"""
	widgets=Widgets()
	i=0
	for count in range(len(list)):
	 tb=widgets.textBox3(self.entrycallback,15,list[count])
	 tb.set_name(str(count))
	 self.textBoxen.append(tb)
	 table.attach(tb,1,2,i,i+1)
	 i=i+1
    
    def get_active_text(self,combobox):
      model = combobox.get_model()
      active = combobox.get_active()
      if active < 0:
          return None
      return model[active][0]
  
    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE