import gtk
import GLIScreen
from Widgets import Widgets

class Panel(GLIScreen.GLIScreen):
    """
    The Timezone section of the installer.
    
    @author:    John N. Laliberte <allanonl@bu.edu>
    @license:   GPL
    """
    # Attributes:
    title="Timezone"
    # Operations
    def __init__(self, controller):
	GLIScreen.GLIScreen.__init__(self, controller)

        vert    = gtk.VBox(gtk.FALSE, 10) # This box is content so it should fill space to force title to top
	horiz   = gtk.HBox(gtk.FALSE, 10)

        content_str = """
This is where you select what timezone you are in.
[short explanation here]
"""
 	
	# pack the description
	vert.pack_start(gtk.Label(content_str), expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

	widgets=Widgets()
	
	# here we set the timezone options (/usr/share/zoneinfo)
	self.timezoneOptions=["EST5EDT",
			      "UTC",
			      "GMT",
			      "MoreToCome"
			      ]
	
	# creates the drop-down
	menu=widgets.createAndAppendOptionMenu(self,"Timezone",self.timezoneOptions)
	# packs the label and the option menu
	packIt = widgets.hBoxThese(gtk.FALSE,0,[gtk.Label("Timezones"),menu])
	packItV=widgets.hBoxIt(packIt)
	vert.pack_start(packItV,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
     
    	self.add_content(vert)

#    def callback(self, widget, data=None):
#      print "%s was toggled %s" % (data)
    # call back for when they change the timezone
    def callback2(self,widget,data=None):
	print "Selected %s" % (data)
     #print data
     #for item in self.textBoxen:
      #print item.get_text()
     
     #number=self.whichSelected(self.lastSelected)
     #if number!=-1:
      ## save the data
      #self.data[number]=[data,self.textBoxen[0].get_text(),self.textBoxen[1].get_text(),
     		       #self.textBoxen[2].get_text(),self.textBoxen[3].get_text()]
      ## clear the boxen
      #for item in self.textBoxen:
       #item.set_text("")
      ## reset last selected
      #self.lastSelected=data
 
      ## load the selected data
      #number=self.whichSelected(data)
      ## means it hasn't been set
      #if len(self.data[number])!=1:
       #print "Len: %s" % len(self.data[number])
       #i=0
       #for item in self.textBoxen:
        ##if i!=1:
	#box=self.data[number]
        #item.set_text(box[i+1])
        #i=i+1

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
      else:
       num=num+1
     return number
 
    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
