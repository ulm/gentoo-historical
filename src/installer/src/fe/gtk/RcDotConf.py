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
    title="rc.conf Settings" 
    # Operations
    def __init__(self, controller):
	GLIScreen.GLIScreen.__init__(self, controller)

        vert    = gtk.VBox(gtk.FALSE, 10) # This box is content so it should fill space to force title to top
	horiz   = gtk.HBox(gtk.FALSE, 10)

        content_str = """
This is where you setup rc.conf.
[short explanation of what rc.conf is here, and should also pull default values.]
"""
	# pack the description
	vert.pack_start(gtk.Label(content_str), expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

	widgets=Widgets()
	
	options=["KEYMAP","SET_WINDOWSKEYS","EXTENDED_KEYMAPS","CONSOLEFONT","CONSOLETRANSLATION",
		"CLOCK","EDITOR","PROTOCOLS","DISPLAYMANAGER","XSESSION"]
	self.rc_options=options
	self.rc_options_widgets=[]
	
	for option in options:
	 new_box=widgets.textBox2(self,26,option)
	 self.rc_options_widgets.append(new_box)
	 new_box=widgets.labelIt(option,new_box)
	 new_box=widgets.hBoxIt(new_box)
	 vert.pack_start(new_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
     
    	self.add_content(vert)

    def activate(self):
	rc_conf = self.controller.install_profile.get_rc_conf()
	print "From saved profile: "+str(rc_conf)
	for item in rc_conf:
	    # if the item in the dictionary is in the list, load it!
	    if(item in self.rc_options):
		number=self.rc_options.index(item)
		self.rc_options_widgets[number].set_text(rc_conf[item])
		
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
    
    def entrycallback(self,widget,data=None):
	print data.get_text()
	make_conf = self.controller.install_profile.get_rc_conf()
	make_conf[widget.get_name()]=data.get_text()
	print "Stored rc.conf"
	print self.controller.install_profile.get_rc_conf()
	self.controller.install_profile.set_rc_conf(make_conf)