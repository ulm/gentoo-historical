import gtk
import GLIScreen
from Widgets import Widgets

class Panel(GLIScreen.GLIScreen):
    """
    The Daemons section of the installer.
    
    @author:    John N. Laliberte <allanonl@bu.edu>
    @license:   GPL
    """
    # Attributes:
    title="Daemons"
    # Operations
    def __init__(self, controller):
	GLIScreen.GLIScreen.__init__(self, controller)

        vert    = gtk.VBox(gtk.FALSE, 10) # This box is content so it should fill space to force title to top
	horiz   = gtk.HBox(gtk.FALSE, 10)

        content_str = """
This is where you select what cron and logging daemons you want, if any.
[short explanation here]
"""
	content_label=gtk.Label(content_str)
	
	content_str2 = """Click the "Forward" button below when you are finished with this step."""
 	
	# pack the description
	vert.pack_start(content_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

	widgets=Widgets()
	
	item = gtk.Label("")
	item.set_markup('<b>'+"Crontab Daemon"+'</b>')	
        vert.pack_start(widgets.hBoxIt3(gtk.FALSE,0,item,5),expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
		
	# cron daemon
	options=["Vixie-cron","fcron","dcron","None"]
	
	i=0
	#new_vbox=gtk.
	new_boxt=widgets.radioButton(None,self.callback_cron,options[0],options[0])
	new_boxt.set_active(gtk.TRUE)
	hBoxed=widgets.hBoxIt3(gtk.FALSE,5,new_boxt,10) 
	vert.pack_start(hBoxed,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	for counter in range(len(options)):
	 if i!=0: 
	  new_box=widgets.radioButton(new_boxt,self.callback_cron,options[counter],options[counter])
          #new_vbox.pack_start(new_box, gtk.TRUE, gtk.TRUE, 0)
          new_box.show()
	  hBoxed=widgets.hBoxIt3(gtk.FALSE,5,new_box,10)			  
	  vert.pack_start(hBoxed, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
	 else:
	  i=-1
        
	item = gtk.Label("")
	item.set_markup('<b>'+"Logging Daemon"+'</b>')
	vert.pack_start(widgets.hBoxIt3(gtk.FALSE,0,item,5),expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	options=["syslog-ng","metalog","syslogkd","None"]
	# logging daemon
	i=0
	#new_vbox=gtk.
	new_boxt=widgets.radioButton(None,self.callback_logger,options[0],options[0])
	new_boxt.set_active(gtk.TRUE)
	hBoxed=widgets.hBoxIt3(gtk.FALSE,5,new_boxt,10)
	vert.pack_start(hBoxed,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	for counter in range(len(options)):
	 if i!=0:
	  new_box=widgets.radioButton(new_boxt,self.callback_logger,options[counter],options[counter])
	  #new_vbox.pack_start(new_box, gtk.TRUE, gtk.TRUE, 0)
	  new_box.show()
	  hBoxed=widgets.hBoxIt3(gtk.FALSE,5,new_box,10)
	  vert.pack_start(hBoxed, expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
	 else:
	  i=-1
													      
    	self.add_content(vert)

    def callback_cron(self, widget, data=None):
      print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
      self.controller.install_profile.set_cron_daemon_pkg(None,widget.get_name(),None)
      print "current cron: "+self.controller.install_profile.get_cron_daemon_pkg()
      
    def callback_logger(self, widget, data=None):
      print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
      self.controller.install_profile.set_logging_daemon_pkg(None,widget.get_name(),None)
      print "current logger: "+self.controller.install_profile.get_logging_daemon_pkg()
      
    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE