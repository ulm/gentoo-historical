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
    title="Do you need any extra packages?"
    # slocate, esearch, and dhcpcd
    # Operations
    def __init__(self, controller):
	GLIScreen.GLIScreen.__init__(self, controller)

        vert    = gtk.VBox(gtk.FALSE, 10) # This box is content so it should fill space to force title to top
	horiz   = gtk.HBox(gtk.FALSE, 10)

        content_str = """
This is where you emerge extra packages that your system may need.
[short explanation of what this is here]
"""
	# pack the description
	vert.pack_start(gtk.Label(content_str), expand=gtk.FALSE, fill=gtk.FALSE, padding=10)

	widgets=Widgets()
	
	item=gtk.Label("")
	item.set_markup('<b>'+"Common Packages"+'</b>')
	
	# common packages list
	list=["xorg-x11","gaim","gentoolkit","gnome","kde"]
	list2=["a common windowing system",
		"a common multiplatform chat client",
		"a package that conatins lots of gentoo specific utilities",
		"a metapackage for a common window manager",
		"a metapackage for another common window manager"
		]

	# create a table here of common options
	table=gtk.Table(3,len(list),gtk.FALSE)
	table.set_col_spacings(10)
	i=0
	# put it in the table
	for listitem in list:
	 table.attach(gtk.CheckButton(),0,1,i,i+1)
	 table.attach(gtk.Label(listitem),1,2,i,i+1)
	 i=i+1
	i=0
	for listitem in list2:
	 table.attach(gtk.Label(listitem),2,3,i,i+1)
	 i=i+1
	# add the table to the layout
	hBoxed=widgets.hBoxIt3(gtk.TRUE,0,table,0)
	vert.pack_start(hBoxed,expand=gtk.FALSE,fill=gtk.FALSE,padding=10)
	
	options=["Extra packages: "]
	
	for option in options:
	 new_box=widgets.textBox(26,option)
	 vert.pack_start(new_box, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
        
	vert.pack_start(gtk.Label("(Space seperated list)"),expand=gtk.FALSE,fill=gtk.FALSE,padding=0)

    	self.add_content(vert)

    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE