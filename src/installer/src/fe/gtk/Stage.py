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
	self.stage_options=options
	self.stage_widgets=[]
	self.valid=False
	
	i=0
	#new_vbox=gtk.
	new_boxt=widgets.radioButton(None,self.callback,options[0],1)
	self.stage_widgets.append(new_boxt)
	new_boxt.set_active(gtk.TRUE)
	hBoxed=widgets.hBoxIt(new_boxt) 
	vert.pack_start(hBoxed,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	#for option in options:
	for counter in range(len(options)):
	 if i!=0: 
	  new_box=widgets.radioButton(new_boxt,self.callback,options[counter],counter+1)
	  self.stage_widgets.append(new_box)
          new_box.show()
	  hBoxed=widgets.hBoxIt(new_box)			  
	  vert.pack_start(hBoxed, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
	 else:
	  i=-1

	makeoptions=["Where is the stage located?"]
	
	for makeoption in makeoptions:
	 new_box=widgets.textBox3(self.button_callback,0,makeoption)
	 self.stage_uri_widget=new_box
	 label=gtk.Label(makeoption)
	 label=widgets.hBoxThese(gtk.TRUE,10,[label])
	 #new_box=widgets.hBoxThese(gtk.TRUE,10,[new_box])
	 vert.pack_start(label, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
	 vert.pack_start(new_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
	 
	self.add_content(vert)

    def callback(self, widget, data=None):
      print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
      self.controller.install_profile.set_install_stage(None,widget.get_name(),None)
      

    def button_callback(self,widget,data=None):
	try:
	    self.controller.install_profile.set_stage_tarball_uri(None,widget.get_text(),None)
	    widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
	    self.valid=True
	except:
	    # do stuff
	    self.valid=False
	    widget.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("pink"))
	
    def activate(self):
	# grab from the install profile
	stage=self.controller.install_profile.get_install_stage()
	print "Stage Selection from profile: " + str(stage)
	
	# now select it
	for count in range(len(self.stage_options)):
	    if(str(stage)==self.stage_widgets[count].get_name()):
		# This is it, select it.
		self.stage_widgets[count].set_active(gtk.TRUE)
	
	# grab the uri from the install profile
	stage_uri=self.controller.install_profile.get_stage_tarball_uri()
	print "Stage Selection URI from profile: " + str(stage_uri)
	
	# now load it
	self.stage_uri_widget.set_text(stage_uri)
		
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
    
    def deactivate(self):
	if(self.valid==False):
	    return True
	else:
	    return True