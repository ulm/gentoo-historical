import gtk
import os
import re
import GLIScreen
import GLIUtility
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
	#self.interfaces=self.get_ethernet_devices()
	self.menu_list=self.get_ethernet_devices()
	self.menu=widgets.createComboEntry(self,"networkdevs",self.menu_list.keys())
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
	self.static_default_gateway = static_default_gateway
	# set it so there is no default gateway to begin with
	self.static_default_gateway_status={}
	
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
	
	self.add_content(vert)
    
    def defaultcheckcall(self,widget,data=None):
	print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
	# ONLY enable it if nothing else has it set.
	if ("OFF","ON")[widget.get_active()]=="ON" and len(self.static_default_gateway_status.keys())==0:
	    self.textBoxen[3].set_sensitive(gtk.TRUE)
	    self.static_default_gateway_status[self.lastSelected]=1
	
	# if its on, and its already been set, display an error message.
	elif ("OFF","ON")[widget.get_active()]=="ON" and not self.static_default_gateway_status.has_key(self.lastSelected):
	    widgets=Widgets()
	    print "should display error"
	    error=widgets.error_Box("Error","You have already selected a default gateway!")
	    result=error.run()
	    if(result==gtk.RESPONSE_ACCEPT):
		# close the box
		error.destroy()
		# deselect the checkbox
		widget.set_active(0)
		
	# case when you return to a device that *is* the default gateway
	elif ("OFF","ON")[widget.get_active()]=="ON" and self.static_default_gateway_status.has_key(self.lastSelected):
	    widget.set_active(1)
	    self.textBoxen[3].set_sensitive(gtk.TRUE)
	    
	elif ("OFF","ON")[widget.get_active()]=="OFF" and self.static_default_gateway_status.has_key(self.lastSelected):
	    # remove it from the dictionary
	    self.static_default_gateway_status.clear()
	    # remove ability to type in the box
	    self.textBoxen[3].set_sensitive(gtk.FALSE)
	    
	else:
	    self.textBoxen[3].set_sensitive(gtk.FALSE)
	    
	
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
        widgets=Widgets()
	try:
	    print "Setting network interfaces..."
	    print "interfaces: "+ str(self.interfaces)
	    self.controller.install_profile.set_network_interfaces(self.interfaces)
	except:
	    error=widgets.error_Box("Error","One of your ip addresses is not valid!")
	    result=error.run()
	    if(result==gtk.RESPONSE_ACCEPT):
		# close the box
		error.destroy()
	
    # call back for when they change eth device
    def callback2(self,widget,data=None):
     print "This callback is being called for: " + widget.get_text()
     previously_selected_item=self.lastSelected
     currently_selected_item=self.get_active_text(self.menu)
     print "Previously selected item: "+previously_selected_item
     print "Currently selected item: "+currently_selected_item
     
     # only save the data if its been selected before ( later add if they are blank remove it )
     if previously_selected_item!="NOT_SET":
	 # save the data only if the entries are not blank!
	 if self.textBoxen[0].get_text()=="" and self.textBoxen[1].get_text()=="" and self.textBoxen[2].get_text()=="":
	     # remove it from the list if its there
	     # not done yet.
	     holder=""
	 else:
	    self.interfaces[previously_selected_item]=(self.textBoxen[0].get_text(),self.textBoxen[1].get_text(),
							self.textBoxen[2].get_text() )
	    print "Saved data: " + str(self.interfaces[previously_selected_item])
	 
	    # determine if default gateway is selected, if so, save it and adjust global
	    if self.static_default_gateway_status==1:
		self.default_gateway[previously_selected_item]=self.textBoxen[3]
	
	    # load the selected data ( -1 b/c do not include default gateway )
	    if currently_selected_item in self.interfaces.keys():
	       for count in range(len(self.textBoxen)-1):
		    self.textBoxen[count].set_text(self.interfaces[currently_selected_item][count])
	    
	       # Do they have DHCP ? ( if so, must activate the checkbox.
	       first_entry=self.interfaces[currently_selected_item][0]
	       # if dhcp is active, and dhcp of the new selected is NOT dhcp, deselect
	       if self.dhcp_radio_button.get_active()==1 and first_entry!="dhcp":
		   # deselect dhcp
		   self.static_radio_button.set_active(1)
	       # if dhcp is not active, and dhcp of the new IS dhcp, select dhcp
	       if self.dhcp_radio_button.get_active()==0 and first_entry=="dhcp":
		   # select dhcp
		   self.dhcp_radio_button.set_active(1)
	   
	       # is this device the default gateway? if so, activate the checkbox and load the data
	       if self.lastSelected in self.static_default_gateway_status.keys():
		   self.static_default_gateway.set_active(1)
	       else:
		   self.static_default_gateway.set_active(0)
	    else:
		 # if its not in the list, its not set, so blank all the boxen
		 for count in range(len(self.textBoxen)-1):
		     self.textBoxen[count].set_text("")
		 
	 self.set_networking_interfaces()
	 
     self.lastSelected=currently_selected_item
     
    # call back for when they activate the entry box
    def entrycallback(self,widget,data=None):
     print "Entry contents of: %s\n" % data.get_text()
     # hack, with this any textbox could be dhcp
     if GLIUtility.is_ip(data.get_text())==False and data.get_text()!="dhcp":
	 self.change_to_pink(data)
	 # disable the dropdown
	 self.menu.set_sensitive(gtk.FALSE)
	 
     elif GLIUtility.is_ip(data.get_text())==True:
	 self.resetBackground(data)
	 # if its the only box with an ip format error, re-enable the box
	 if self.checkAllBoxes()==True:
	     print "got here"
	     self.menu.set_sensitive(gtk.TRUE)
    
    def checkAllBoxes(self):
	return_value=True
	# if default gateway is selected, also check that box!
	for count in range(len(self.textBoxen)-1):
	    if GLIUtility.is_ip(self.textBoxen[count].get_text())==False:
		return_value=False
	return return_value
    
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
    
    def resetBackgrounds(self):
	for count in range(len(self.textBoxen)-1):
	    self.textBoxen[count].modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
    
    def resetBackground(self,textBox):
	textBox.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
	
    def findAndHighlight(self):
	for count in range(len(self.textBoxen)-1):
	    if GLIUtility.is_ip(self.textBoxen[count].get_text())==False:
		# change the background of the textbox
		self.textBoxen[count].modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("pink"))
		#textBox.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("blue"))
    
    def change_to_pink(self,textBox):
	textBox.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("pink"))
    
    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
    
    def deactivate(self):
	widgets=Widgets()
	try:
	    self.set_networking_interfaces()	    
	    return True
	except:
	    widgets.error_Box("Error","One or more of your ip addresses are not formed correctly!")
