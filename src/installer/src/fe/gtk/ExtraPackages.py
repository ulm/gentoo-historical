import gtk,gobject
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
    # {section: [{category:description},...}
    data={'Applications':[{"Editors":["These are text editors that allow you to create text files.",None,None]}],
	  'Desktops':[{"X Window System":["These are the base packages which provide support for other X-Windowing environments. ",None,
					  {"x11-base/xorg-x11":["An X11 implementation maintained by the X.Org Foundation",True],
					   "x11-base/opengl-update":["Utility to change the OpenGL interface being used",True],
					   "x11-misc/xscreensaver":["a modular screensaver for X11",False]}
					  ],
		       "Gnome Desktop Enviroment":["GNOME is a powerful graphical user interface which is lighter than KDE.","extra_packages/GNOME-Foot.png",None],
		       "KDE Desktop Environment":["KDE is a powerful graphical user interface which is suitable for anyone.","extra_packages/kde_icon.png",None]
		       }]
	  }
    # slocate, esearch, and dhcpcd
    # Operations
    def __init__(self, controller):
	GLIScreen.GLIScreen.__init__(self, controller)

        vert    = gtk.VBox(gtk.FALSE, 10) # This box is content so it should fill space to force title to top
	horiz   = gtk.HBox(gtk.FALSE, 10)
	
	vert2    = gtk.VBox(gtk.FALSE, 10)
        
        content_str = """
This is where you emerge extra packages that your system may need.
[short explanation of what this is here]
"""
	#self.categories={""}
	# pack the description
	vert.pack_start(gtk.Label(content_str), expand=gtk.FALSE, fill=gtk.FALSE, padding=10)
	
	scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
	scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
	
	for section in self.data:
	    new_section=self.Section(section)
	    category_dict=self.data[section][0]
	    for category in category_dict:
		new_category=self.Category(category,category_dict[category][0],category_dict[category][1],category_dict[category][2])
		new_section.add_category(new_category)
	    new_section.create_gtk_gui(vert2)
	    #new_section.print_all()
	    
	# add the custom space-seperated list bar
	self.custom_box=Widgets().textBox3(self.custom_box_callback,0,"custom_box")

	scrolled_window.add_with_viewport(vert2)
	viewport = scrolled_window.get_children()[0]
        viewport.set_shadow_type (gtk.SHADOW_IN)
	viewport.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse ("white"))
	
	vert.pack_start(scrolled_window,expand=gtk.TRUE,fill=gtk.TRUE,padding=0)
	vert.pack_start(self.custom_box,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	self.add_content(vert)
	

	
    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = gtk.TRUE
	self.controller.SHOW_BUTTON_HELP    = gtk.TRUE
	self.controller.SHOW_BUTTON_BACK    = gtk.TRUE
	self.controller.SHOW_BUTTON_FORWARD = gtk.TRUE
	self.controller.SHOW_BUTTON_FINISH  = gtk.FALSE
	
	# load the custom packages bar
	s=" ".join(self.controller.install_profile.get_install_packages())
	print "loaded custom packages: "+s
	self.custom_box.set_text(s)
    
    def custom_box_callback(self,widget,data=None):
	pass
    
    def deactivate(self):
	return_value = False
	# save the space seperated list
	#print self.custom_box.get_text()
	try:
	    self.controller.install_profile.set_install_packages(None,self.custom_box.get_text(),None)
	    #print self.custom_box.get_text()
	    return_value = True
	except:
	    box = Widgets().error_Box("Error saving packages","You need to fix your input! \n Theres a problem, are you sure didn't enter \n funny characters?")
	    box.show()
	    return_value = False
	    
	return return_value
    
    class Section:
	"This is the Section associated with packages."
	def __init__(self,title):
	    self.title=title
	    self.section_list=[]
	    
	def add_category(self,category):
	    self.section_list.append(category)
	
	def remove_category(self,category):
	    self.section_list.remove(category)
	
	def print_all(self):
	    print "Section Title: "+self.title+"\n"
	    print "Categories: \n"
	    for item in self.section_list:
		print item.print_name()
	
	def create_gtk_gui(self,vert2):
	    """ Adds the section and categories to the given element.
	    """
	    section_hbox=gtk.HBox(gtk.TRUE,0)
	    section_name=gtk.Label("")
	    section_name.set_markup('<span size="x-large" weight="bold" foreground="white">'+self.title+'</span>')
	    section_name.set_justify(gtk.JUSTIFY_LEFT)
	    
	    test_table = gtk.Table(1, 1, gtk.FALSE)
	    test_table.set_col_spacings(10)
	    test_table.set_row_spacings(6)
	    test_table.attach(section_name,0,1,0,1)
	    
	    eb=gtk.EventBox()
	    eb.add(Widgets().hBoxIt2(gtk.FALSE,0,test_table))
	    eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#737db5"))
	    
	    vert2.pack_start(eb,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	    
	    # now create each category gui and add it to the section.
	    for item in self.section_list:
		item.create_gtk_gui(vert2)
	    
    class Category:
	"This is an individual category inside a Section"
	
	def __init__(self,title,description,picture_path=None,details_dictionary=None):
	    self.title=title
	    self.description=description
	    self.details_click=self.Details(self.title,details_dictionary,self)
	    
	    if picture_path!=None:
		self.picture=gtk.Image()
		self.picture.set_from_file(picture_path)
	    else: self.picture=None
	    
	def print_name(self):
	    print self.title + "\n"
	
	def create_gtk_gui(self,vert2):
	    category_hbox=gtk.HBox(gtk.FALSE,0)
	    category_table = gtk.Table(5, 5, gtk.FALSE)
	    category_table.set_col_spacings(10)
	    category_table.set_row_spacings(6)
	    
	    button = gtk.CheckButton()
	    
	    category_title=gtk.Label("")
	    category_title.set_markup('<span weight="bold">'+self.title+'</span>')
	    button.add(category_title)
	    
	    button.connect("toggled", self.Category1, self.title)
	    category_table.attach(Widgets().hBoxIt2(gtk.FALSE,0,button),1,2,0,1)
	    
	    self.button = button
	    # the image on the left side
	    category_hbox=gtk.HBox(gtk.FALSE,0)
	    if self.picture==None:
		left_image=gtk.Image()
		left_image.set_from_stock(gtk.STOCK_ADD,gtk.ICON_SIZE_LARGE_TOOLBAR)
	    else:
		left_image=self.picture
	    
	    
	    category_description=gtk.Label(self.description)
	    #category_description.set_width_chars(45)
	    category_description.set_line_wrap(gtk.TRUE)
	    category_table.attach(Widgets().hBoxThese(gtk.FALSE,10,[left_image,category_description],0),1,2,1,2,xpadding=25)
	    #category_table.attach(widgets.hBoxIt2(gtk.FALSE,0,category_description),2,3,1,2)
	    category_table.attach(self.details_click.get_details_gui(),1,2,2,3)
	    # the details button
	    #category_button=gtk.Button("Details")
	    #category_button.connect("clicked", self.Category1,self.title)
	    #category_table.attach(Widgets().hBoxIt2(gtk.FALSE,0,category_button),4,5,0,1)
	    
	    
	    category_hbox.pack_start(category_table,expand=gtk.FALSE,fill=gtk.FALSE,padding=5)
	    vert2.pack_start(category_hbox,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
	    
	def Category1(self,widget,data=None):
	    #self.details_click.show()
	    print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
	    # now need to check off the default values.
	    print data
	    if data == self.title and ("OFF","ON")[widget.get_active()]=="ON":
		self.details_click.activate_treeview()
		self.details_click.toggle_default()
	    else:
		self.details_click.untoggle_all()
		self.details_click.deactivate_treeview()
	
	def turn_off_checkbox(self,value):
	    #self.Category1(self.button,"NO")
	    if value != gtk.TRUE:
		self.button.set_active(value)
	    
	class Details:
	    "This is for the details window"
	    def __init__(self,title,details_dictionary,controller):
		self.title=title
		self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.dictionary=details_dictionary
		self.details_view_gui=self.create_gtk_gui()
		#self.checkbox=checkbox
		self.controller=controller
		
	    def create_gtk_gui(self):
		
		MY_FIRST_ROW, MY_SECOND_ROW = range(2)
		
		self.treestore = gtk.TreeStore(gobject.TYPE_BOOLEAN,gobject.TYPE_STRING)
		self.treeview = gtk.TreeView(self.treestore)
		self.treeview.set_headers_visible(gtk.FALSE)
		
		self.renderer = gtk.CellRendererToggle()
		self.renderer.set_property('activatable', True)
		self.renderer.connect( 'toggled', self.col0_toggled_cb, self.treestore )
		
		self.column0 = gtk.TreeViewColumn("", self.renderer )
		self.column0.add_attribute( self.renderer, "active", MY_FIRST_ROW)
		self.treeview.append_column( self.column0 )
		
		self.renderer1 = gtk.CellRendererText()
		self.column1 = gtk.TreeViewColumn("Description", self.renderer1,markup=MY_SECOND_ROW)
		self.treeview.append_column( self.column1 )
		
		if self.dictionary != None:
		    piter = self.treestore.append(None, [None,"Expand"])
		    print self.dictionary
		    i=0
		    self.toggle_f=[]
		    for child in self.dictionary:
			test='<span><b>'+child+'</b></span>'+"\n"+self.dictionary[child][0]
			self.treestore.append(piter, [None,test])
			if self.dictionary[child][1]==True:
			    # activate the checkbox
			    #self.col0_toggled_cb(0,"0:"+str(i),self.treestore)
			    self.toggle_f.append(i)
			i=i+1
		    self.number=i
		    print "outside here"+str(self.number)
		else:
		    piter = self.treestore.append(None,(None,"No Extra Packages To Select"))
		self.treeview.set_sensitive(gtk.FALSE)
		return self.treeview
	    
	    def show(self):
		self.create_gtk_gui()
		
		#self.window.show()
		print "shows the window"
		
	    def hide(self,widget,data=None):
		print "hides the window"
		# also need to save the selections here
		#gtk_widget_destroy(widget)
	    
	    def get_details_gui(self):
		return self.details_view_gui
	    
	    def col0_toggled_cb( self, cell, path, model ):
		"""
		Sets the toggled state on the toggle button to true or false.
		"""
		if path=="0":
		    # toggle them all!
		    value = model[path+":"+str(0)][0]
		    for i in range(self.number):
			newpath=path+":"+str(i)
			model[newpath][0] = not model[path][0]
		    model[path][0] = not model[path][0]
		    
		    # also untoggle the big one
		    if model["0"][0] == True:
			self.controller.turn_off_checkbox(gtk.TRUE)
		    else:
			self.controller.turn_off_checkbox(gtk.FALSE)
		    
		else:
		    # toggle just that one
		    model[path][0] = not model[path][0]
		    print "Toggle '%s' to: %s" % (model[path][1], model[path][0])
		    # check if the top one is set, if it is, uncheck it.
		    if model["0"][0] == True and model[path][0]== False:
			# uncheck it
			model["0"][0] = False
		    
		    # check to see if its the last one unchecked!
		    if model[path][0] == False:
			value_h=False
			for i in range(self.number):
			    if self.treestore["0:"+str(i)][0]!=False:
				value_h=True
			if value_h==False:
			    # its the last one unchecked so uncheck the big box
			    self.controller.turn_off_checkbox(gtk.FALSE)
		
		return
	    
	    def toggle_default(self):
		for i in range(self.number):
		    if i in self.toggle_f:
			# toggle it!
			self.col0_toggled_cb(0,"0:"+str(i),self.treestore)
	    
	    def activate_treeview(self):
		self.treeview.expand_all()
		self.treeview.set_sensitive(gtk.TRUE)
	    
	    def deactivate_treeview(self):
		self.treeview.collapse_all()
		self.treeview.set_sensitive(gtk.FALSE)
	    
	    def untoggle_all(self):
		# toggle them all off!
		path="0"
		model=self.treestore
		for i in range(self.number):
		    newpath=path+":"+str(i)
		    model[newpath][0] = False
		model[path][0] = False