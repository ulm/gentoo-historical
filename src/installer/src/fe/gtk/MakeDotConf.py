import gtk
import GLIScreen
from Widgets import Widgets

class Panel(GLIScreen.GLIScreen):
    """
    The make.conf section of the installer.
    
    @author:    John N. Laliberte <allanonl@bu.edu>
    @license:   GPL
    """
    # Attributes:
    title="Make.conf Settings"
    # Operations
    # commands.getoutput("source /etc/make.conf; echo $VALUE_YOU_WANT")
    # blah = GLIUtility.get_value_from_config(filename, value)
    def __init__(self, controller):
	GLIScreen.GLIScreen.__init__(self, controller)

        vert    = gtk.VBox(gtk.FALSE, 10) # This box is content so it should fill space to force title to top
	horiz   = gtk.HBox(gtk.FALSE, 10)

        content_str = """
This is where you setup make.conf.
[short explanation of what make.conf is here]
"""
	# pack the description
	vert.pack_start(gtk.Label(content_str), expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

	widgets=Widgets()
	
	makeoptions=["ACCEPT_KEYWORDS","CFLAGS","CHOST","MAKEOPTS","FEATURES","USE"]
	
	for makeoption in makeoptions:
	 #new_box=widgets.textBox(26,makeoption)
	 new_box=widgets.textBox2(self,26,makeoption)
	 new_box=widgets.labelIt(makeoption,new_box)
	 new_box=widgets.hBoxIt(new_box)
	 vert.pack_start(new_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
	
    	self.add_content(vert)

    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
	
    def entrycallback(self,widget,data=None):
	print data.get_text()
	make_conf = self.controller.install_profile.get_make_conf()
	make_conf[widget.get_name()]=data.get_text()
	print "Stored make.conf"
	print self.controller.install_profile.get_make_conf()
	self.controller.install_profile.set_make_conf(make_conf)
	
