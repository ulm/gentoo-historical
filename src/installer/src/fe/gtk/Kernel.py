import gtk
import GLIScreen
from Widgets import Widgets
from Storage import Storage

class Panel(GLIScreen.GLIScreen):
    """
    The Kernel section of the installer.
    
    @author:    John N. Laliberte <allanonl@bu.edu>
    @license:   GPL
    """
    # Attributes:
    title="Kernel"
    # Operations
    def __init__(self, controller):
	GLIScreen.GLIScreen.__init__(self, controller)
 
        vert    = gtk.VBox(gtk.FALSE, 10) # This box is content so it should fill space to force title to top
	horiz   = gtk.HBox(gtk.FALSE, 10)

        content_str = """
This is where you select which kind of kernel you wish to have.
[short explanation here]
"""
	# pack the description
	vert.pack_start(gtk.Label(content_str), expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

	widgets=Widgets()
	
	options=["vanilla-sources","gentoo-sources","development-sources",
		 "gentoo-dev-sources","hardened-sources"]
	
	i=0
	#new_vbox=gtk.
	new_boxt=widgets.radioButton(None,self.callback,options[0],options[0])
	new_boxt.set_active(gtk.TRUE)
	hBoxed=widgets.hBoxIt(new_boxt) 
	vert.pack_start(hBoxed,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	for counter in range(len(options)):
	 if i!=0: 
	  new_box=widgets.radioButton(new_boxt,self.callback,options[counter],options[counter])
          #new_vbox.pack_start(new_box, gtk.TRUE, gtk.TRUE, 0)
          new_box.show()
	  hBoxed=widgets.hBoxIt(new_box)			  
	  vert.pack_start(hBoxed, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
	 else:
	  i=-1
     
    	self.add_content(vert)

    def callback(self, widget, data=None):
      print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
      self.controller.install_profile.set_kernel_source_pkg(None, widget.get_name(), None)
      print "current kernel: "+self.controller.install_profile.get_kernel_source_pkg()

    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE