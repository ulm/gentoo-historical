import gtk

class Widgets:
    """
    Commonly used widgets
    
    @author:    John N. Laliberte <allanonl@bu.edu>
    @license:   GPL

    TODO: 
    
    fix textBox to not Hbox/Vbox automatically and use
    hBoxIt and vBoxIt.

    remove extraneous hBox methods
    """

    # Operations
    def __init__(self):
     self.text=""
    
    # This creates a new Vbox
    def newVbox(self):
      new_vbox=gtk.VBox(gtk.FALSE, 10)
      return new_vbox
      
    # This creates a textbox with a specified max length,
    # And heading:
    # HEADING ____________
    # Is what it would approximatly look like.
    def textBox(self,length,heading):
      STRINGLENGTH=length
	
      new_string = heading
      new_label = gtk.Label(new_string)
      self.new_entry = gtk.Entry(max=STRINGLENGTH)
      self.new_entry.set_width_chars(26)

      # This creates the actual box to enter stuff
      self.new_entry_hbox       = gtk.HBox(gtk.TRUE, 10)
      self.new_entry_hbox.pack_start(new_label, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
      self.new_entry_hbox.pack_end(self.new_entry, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)	

      new_vbox = gtk.VBox(gtk.FALSE, 10)
      new_vbox.pack_start(self.new_entry_hbox, expand=gtk.FALSE, fill=gtk.FALSE, padding=0)
      return new_vbox
    
    # this is a temporary class to port over textBox
    def textBox2(self,controller,length):
      new_entry=gtk.Entry(max=length)
      new_entry.connect("changed",controller.entrycallback,new_entry)
      new_entry.set_width_chars(length)
      return new_entry
      
    # a method that can box an arbitrary number of things into an hbox
    def hBoxThese(self,homogenous,spacing,list):
     new_box=gtk.HBox(homogenous,spacing)
     for item in list:
      new_box.pack_start(item,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
     return new_box
     
    # This makes a label on the left hand of any element
    def labelIt(self,label,object):
     new_label=gtk.Label(label)
     new_box = gtk.HBox(gtk.TRUE,10)
     new_box.pack_start(new_label,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
     new_box.pack_start(object,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
     return new_box

    # This creates the *first* radio button
    # o HEADING
    def radioButton(self,group,heading):
      new_vbox=self.newVbox()
      button = gtk.RadioButton(group, heading)
      button.connect("toggled", self.callback, heading)
      #button.set_active(gtk.TRUE)
      #new_vbox.pack_start(button, gtk.TRUE, gtk.TRUE, 0)
      button.show()
      #return new_vbox
      return button
    
    # This is the callback for the radio buttons
    def callback(self, widget, data=None):
      print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
    
    # This is the callback for the dropdown menu
    def callback2(self,widget,data=None):
     print "%s was selected " % (data)
    
    # This will create a regular button
    def normalButton(self,heading):
      button = gtk.Button(heading)
      button.connect("clicked",self.callback,heading)
      button.show()
      return button
    
    #------Drop-down Menu-----#
    # This will create a menu
    def createOptionMenu(self):
     opt = gtk.OptionMenu()
     return opt
    
    # creates a regular gtk menu
    def createMenu(self,heading):
     menu = gtk.Menu()
     #menu.connect("activate",self.callback,heading)
     return menu
    
    # This will create an option in a menu
    def menuOption(self,controller,heading):
     item = gtk.MenuItem(heading)
     item.connect("activate",controller.callback2,heading)
     item.show()
     return item
    
    # This will append to a menu given
    def appendToMenu(self,menu,optionToAppend):
     menu.append(optionToAppend)
     return menu

    # This will append a list of options to the given menu
    def appendListToMenu(self,controller,menu,optionsToAppend):
     for option in optionsToAppend:
      item = self.menuOption(controller,option)
      menu.append(item)
     return menu
    
    # This will create a menu and append a list of options
    def createAndAppendMenu(self,controller,name,optionsToAppend):
     menu=self.createMenu(name)
     menu=self.appendListToMenu(controller,menu,optionsToAppend)
     return menu

    # This will create an option menu and append a list of options
    def createAndAppendOptionMenu(self,controller,name,optionsToAppend):
     menu=self.createMenu(name)
     menu=self.appendListToMenu(controller,menu,optionsToAppend)
     optionMenu=self.createOptionMenu()
     optionMenu.set_menu(menu)
     return optionMenu
    #--------------------------#
    
    # This creates a table of any size
    def createTable(self,x,y,value):
     return gtk.Table(x,y,value)
    
    # This h boxes anything you give it!
    def hBoxIt(self,whatToBox):
      self.new_hbox=gtk.HBox(gtk.TRUE,10)
      self.new_hbox.pack_start(whatToBox,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
      return self.new_hbox

    def hBoxIt2(self,homogeneous,spacing,whatToBox):
      new_hbox=gtk.HBox(homogeneous,spacing)
      new_hbox.pack_start(whatToBox,expand=gtk.FALSE,fill=gtk.FALSE,padding=5)
      return new_hbox
    
    def hBoxIt3(self,homogeneous,spacing,whatToBox,pad):
      new_hbox=gtk.HBox(homogeneous,spacing)
      new_hbox.pack_start(whatToBox,expand=gtk.FALSE,fill=gtk.FALSE,padding=pad)
      return new_hbox
      
    # This v boxes anything you give it!
    def vBoxIt(self,whatToBox):
      new_vbox=gtk.VBox(gtk.TRUE,10)
      new_vbox.pack_start(whatToBox,expand=gtk.FALSE,fill=gtk.FALSE,padding=0)
      return new_vbox
