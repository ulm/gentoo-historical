import gtk
import GLIScreen
from Widgets import Widgets

class Panel(GLIScreen.GLIScreen):
    """
    The portage tree section of the installer.
    
    @author:    John N. Laliberte <allanonl@bu.edu>
    @license:   GPL
    """
    # Attributes:
    title="Portage Tree"
    # Operations
    def __init__(self, controller):
	GLIScreen.GLIScreen.__init__(self, controller)

        vert    = gtk.VBox(gtk.FALSE, 10) # This box is content so it should fill space to force title to top
	horiz   = gtk.HBox(gtk.FALSE, 10)

        content_str = """
This is where you select what kind of portage tree you will use.
[short explanation here]
"""
	# pack the description
	vert.pack_start(gtk.Label(content_str), expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

	widgets=Widgets()
	
	self.options=["Normal (emerge sync)","Webrsync (firewalled)","None (snapshop/NFS mount)"]
	
	i=0
	#new_vbox=gtk.
	new_boxt=widgets.radioButton(None,self.callback,self.options[0],self.options[0])
	new_boxt.set_active(gtk.TRUE)
	hBoxed=widgets.hBoxIt(new_boxt) 
	vert.pack_start(hBoxed,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	for counter in range(len(self.options)):
	 if i!=0: 
	  new_box=widgets.radioButton(new_boxt,self.callback,self.options[counter],self.options[counter])
          #new_vbox.pack_start(new_box, gtk.TRUE, gtk.TRUE, 0)
          new_box.show()
	  hBoxed=widgets.hBoxIt(new_box)			  
	  vert.pack_start(hBoxed, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
	 else:
	  i=-1
     
	self.add_content(vert)

    def callback(self, widget, data=None):
      print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
      # the last one needs to be added to display a URI if you need snapshot etc....
      if widget.get_name() == self.options[0]: self.controller.install_profile.set_portage_tree_sync_type(None, "sync", None)
      if widget.get_name() == self.options[1]: self.controller.install_profile.set_portage_tree_sync_type(None, "webrsync", None)
      if widget.get_name() == self.options[2]: self.controller.install_profile.set_portage_tree_sync_type(None, "custom", None)
      print "current portage tree: "+self.controller.install_profile.get_portage_tree_sync_type()
      
    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE