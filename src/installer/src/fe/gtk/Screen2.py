import gtk

class Screen:

    def __init__(self, controller):
        self.title = "Welcome to the Gentoo Linux installer!"
	self.controller = controller
        self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
        self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
        self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
        self.controller.SHOW_BUTTON_FORWARD = gtk.FALSE
        self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE

        self.__full_path = self.controller.get_current_path()

        vert    = gtk.VBox(gtk.FALSE, 10) # This box is content so it should fill space to force title to top
	horiz   = gtk.HBox(gtk.FALSE, 10)

        content_str = """
Screen 2.

Before any permanent changes are made to your system, you will
be asked to confirm your decisions.  Any any time prior to the 
"Install!", you may click the Exit button to terminate this 
installer without altering your computer's existing 
configuration.

If you have installed Gentoo Linux previously using this installer and 
you saved your configuration settings, you can choose to not be
prompted for any further information. The settings saved on the
disk will be used to perform this install.
"""

	content_str2 = """Click the "Forward" button below to begin your
Gentoo Linux installation."""
 	
        content_label = gtk.Label(content_str)
        content_label2 = gtk.Label(content_str2)
	vert.pack_start(content_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)            

        #  _______
	# |_I_|_T_|   I = an image of a floppy disk     T = some text beside the image	
	container = gtk.HBox(gtk.FALSE,30)
	floppy_image  = gtk.Image()
        floppy_image.set_from_file(self.__full_path + '/content_images/gnome-dev-floppy.png')
	container.pack_start(floppy_image, expand=gtk.FALSE, fill=gtk.FALSE, padding=40)            	
	container.pack_start(content_label2, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)            	
	vert.pack_start(container, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)            
    	self.controller.add_content(vert)

	# Lastly we need to tell this window what widget should have primary focus	
	self.controller.forwardbutton.grab_focus()
	self.controller.make_visible()

    def get_screen(self):
        """function get_screen
        
        returns 
        """
        return None # should raise NotImplementedError()
