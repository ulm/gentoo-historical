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
	
	makeoptions=["Add an interface"]
	
	for makeoption in makeoptions:
	 new_label=gtk.Label(makeoption)
	 new_box=widgets.textBox2(self,26)
	 new_button=widgets.normalButton("Add")
	 packIt = widgets.hBoxThese(gtk.FALSE,0,[new_label,new_box,new_button])
	 packItV = widgets.hBoxIt(packIt)
	 vert.pack_start(packItV, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
        
	# now we have:
	# Heading _______
	self.data=[]
	# get their devices
	self.devices=[]
	put, get = os.popen4("ifconfig -a | egrep -e '^[^ ]'|sed -e 's/ .\+$//'")
	for device in get.readlines():
	 device=device.strip()
	 self.devices.append(device)
	 # append a dummy size for callback later on
	 self.data.append("")
	 
	# creates the drop-down
	menu=widgets.createAndAppendOptionMenu(self,"EDevs",self.devices)
	#new_box=widgets.hBoxIt(menu)
	#set default
	self.lastSelected=self.devices[0]
	
	# create a checkbox for DHCP
	button = gtk.CheckButton("DHCP")
	button.connect("toggled", self.callback, "check button 1")
	
	packIt = widgets.hBoxThese(gtk.FALSE,10,[gtk.Label("Current Devices"),menu,button])
	packItV=widgets.hBoxIt(packIt)
	vert.pack_start(packItV,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	#self.add_content(vert)
	
	table=gtk.Table(4,2,gtk.FALSE)
	table.set_col_spacing(0,10)
	tableH=widgets.hBoxIt2(gtk.TRUE,20,table)
	vert.pack_start(tableH,expand=gtk.FALSE,fill=gtk.FALSE,padding=10)

	# ( whats in resolv.conf )
	list=["Ip Address","Mask","Broadcast","Default Gateway"]
	
	# attaches the stuff into the left frame of the table.
	i=0
	for item in list:
	 #box=self.createSettings(item)
	 #vert.pack_start(box,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	 table.attach(gtk.Label(item),0,1,i,i+1)
	 i=i+1
	
	self.textBoxen=[] # the list of textboxen so we can get data later
	# attaches the stuff into the right frame of the table
	i=0
	for item in list:
	 tb=widgets.textBox2(self,15)
	 self.textBoxen.append(tb)
	 table.attach(tb,1,2,i,i+1)
	 i=i+1

	self.add_content(vert)
	
    def createSettings(self,name):
      widgets=Widgets()
      new_box=widgets.hBoxThese(gtk.FALSE,0,[gtk.Label(name),widgets.textBox2(self,15)])
      new_box=widgets.hBoxIt2(gtk.FALSE,10,new_box)
      return new_box

    def callback(self, widget, data=None):
      print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
      if ("OFF","ON")[widget.get_active()]=="ON":
       # deactivate the boxen for entering data into.
       for item in self.textBoxen:
	   item.set_sensitive(gtk.FALSE)
      else:
	  # activate them all
	for item in self.textBoxen:
	    item.set_sensitive(gtk.TRUE)
    # call back for when they change eth device
    def callback2(self,widget,data=None):
     print data
     for item in self.textBoxen:
      print item.get_text()
     
     number=self.whichSelected(self.lastSelected)
     if number!=-1:
      # save the data
      self.data[number]=[self.lastSelected,self.textBoxen[0].get_text(),self.textBoxen[1].get_text(),
     		       self.textBoxen[2].get_text(),self.textBoxen[3].get_text()]
      # clear the boxen
      for item in self.textBoxen:
       item.set_text("")
      # reset last selected
      self.lastSelected=data
 
      # load the selected data
      number=self.whichSelected(data)
      # means it hasn't been set
      if len(self.data[number])>=1:
       print "Len: %s" % len(self.data[number])
       i=0
       for item in self.textBoxen:
        #if i!=1:
	box=self.data[number]
        item.set_text(box[i+1])
        i=i+1

    # figures out which one is selected
    def whichSelected(self,data):
     num=0
     number=-1
     for item in self.devices:
      print "Item %s" % item
      print "DATA %s" % data
      if item==data:
       #This is it!
       number=num
       break
      else:
       num=num+1
     return number
     
    # call back for when they activate the entry box
    def entrycallback(self,widget,data=None):
     print "got here"
     print "Entry contents: %s\n" % data.get_text()

    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE