import gtk
import GLIScreen
import GLIInstallProfile
from Widgets import Widgets

class Panel(GLIScreen.GLIScreen):
    """
    The stage selection section of the installer.
    
    @author:    John N. Laliberte <allanonl@bu.edu>
    @license:   GPL
    """
    # Attributes:
    title="Stage Selection"
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
	
	options=["Stage 1","Stage 2","Stage 3"]
	
	i=0
	#new_vbox=gtk.
	new_boxt=widgets.radioButton(None,self.callback,options[0],1)
	new_boxt.set_active(gtk.TRUE)
	hBoxed=widgets.hBoxIt(new_boxt) 
	vert.pack_start(hBoxed,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	#for option in options:
	for counter in range(len(options)):
	 print counter
	 if i!=0: 
	  new_box=widgets.radioButton(new_boxt,self.callback,options[counter],counter)
	  print counter
          new_box.show()
	  hBoxed=widgets.hBoxIt(new_box)			  
	  vert.pack_start(hBoxed, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
	 else:
	  i=-1

	makeoptions=["Where is the stage located?"]
	
	for makeoption in makeoptions:
	 new_box=widgets.textBox(26,makeoption)
	 vert.pack_start(new_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
	 
	self.add_content(vert)

    def callback(self, widget, data=None):
      print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
      print widget.get_name()
      self.controller.install_profile.set_install_stage(None,widget.get_name(),None)
      print self.controller.install_profile.get_install_stage()

    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE