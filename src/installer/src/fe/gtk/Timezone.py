import gtk
import GLIScreen
import os
import string
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
	
	# creates the drop-down
	#menu=widgets.createComboEntry(self,"Timezone",self.generate_timezones())
	# packs the label and the option menu
	#packIt = widgets.hBoxThese(gtk.FALSE,0,[gtk.Label("Timezones"),menu])
	#packItV=widgets.hBoxIt(packIt)
	#vert.pack_start(packItV,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	
	self.treestore = gtk.TreeStore(str)
	# generates/adds to the treestore
	self.generate_timezones()
	#for parent in range(4):
	    #piter = self.treestore.append(None, ['parent %i' % parent])
	    #for child in range(3):
		#piter2=self.treestore.append(piter, ['child %i of parent %i' % (child, parent)])
		#for child2 in range(2):
		    #self.treestore.append(piter2, ['child2 %i of child %i' % (child2, child)])
	
	self.treeview = gtk.TreeView(self.treestore)
	self.tvcolumn = gtk.TreeViewColumn('Please Select A Timezone: ')
	self.treeview.append_column(self.tvcolumn)
	self.cell = gtk.CellRendererText()
	self.tvcolumn.pack_start(self.cell, True)
	self.tvcolumn.add_attribute(self.cell, 'text', 0)
	self.treeview.set_search_column(0)
	
	scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
	scrolled_window.add_with_viewport(self.treeview)
	scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
	
	#treeview=widgets.hBoxIt3(gtk.FALSE,10,scrolled_window,10)
	vert.pack_start(scrolled_window,expand=gtk.TRUE,fill=gtk.TRUE,padding=0)
    	
    	self.add_content(vert)

    # call back for when they change the timezone
    def callback2(self,widget,data=None):
	print "Selected %s" % (data)

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
       
    def generate_timezones(self):
	# /usr/share/zoneinfo
	path="/usr/share/zoneinfo"
	put, get = os.popen4("find "+path+"/*")
	self.last=[]
	self.lastpiter=""
	self.global_iter={}
	for timezone in get.readlines():
	    timezone=timezone[20:] # remove /usr/share/zoneinfo/ prefix
	    timezone.strip()
	    timezone=timezone[:-1] # strips the newline
	    self.timezone_list=timezone.split("/")
	    self.depth=len(self.timezone_list)-1
	    
	    # If its more than 1 element, ( ie more than 1 deep )
	    # it is NOT a base parent.
	    if(self.depth>=1):
		self.append_to_treestore(self.depth)
	    else:
		# its a base parent
		self.lastpiter = self.treestore.append(None, [self.timezone_list[self.depth]])
		self.global_iter[self.timezone_list[self.depth]]=self.lastpiter
		self.last=[]
		self.last.append(self.timezone_list[self.depth])
		
    def append_to_treestore(self,depth):
	iter=self.global_iter[self.timezone_list[depth-1]]
	self.global_iter[self.timezone_list[depth]]=self.treestore.append(iter, [self.timezone_list[depth]])
	
	if(len(self.last)<len(self.timezone_list)):
	    self.last.append(self.timezone_list[depth])
	else:
	    self.last[depth]=self.timezone_list[depth]
	
	if(depth<len(self.timezone_list)-1):
	    self.append_to_treestore(depth+1)

    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
