import gtk
import GLIScreen
from Widgets import Widgets

class Panel(GLIScreen.GLIScreen):
    """
    The summary of all installation options.
    
    @author:    John N. Laliberte <allanonl@bu.edu>
    @license:   GPL
    """
    # Attributes:
    title="Summary of Installation Options"
    # Operations
    def __init__(self, controller):
	GLIScreen.GLIScreen.__init__(self, controller)

        vert    = gtk.VBox(False, 10) # This box is content so it should fill space to force title to top
	horiz   = gtk.HBox(False, 10)

        content_str = """
If you click finish here, the installer will generate the xml profile.
"""
	# pack the description
	vert.pack_start(gtk.Label(content_str), expand=False, fill=False, padding=10)

	widgets=Widgets()
	self.treestore = gtk.TreeStore(str)
	
        # we'll add some data now - 4 rows with 3 child rows each
	#for parent in range(5):
	# piter = self.treestore.append(None, ['parent %i' % parent])
	# for child in range(4):
	#  self.treestore.append(piter, ['child %i of parent %i' % (child, parent)])
	for item in self.controller.menuItems:
	    self.treestore.append(None, [item['text']])
	self.treeview = gtk.TreeView(self.treestore)
	self.tvcolumn = gtk.TreeViewColumn('Current Install Options')
	self.treeview.append_column(self.tvcolumn)
	self.cell = gtk.CellRendererText()
	self.tvcolumn.pack_start(self.cell, True)
	self.tvcolumn.add_attribute(self.cell, 'text', 0)
	self.treeview.set_search_column(0)
	
	scrolled_window = gtk.ScrolledWindow()
	scrolled_window.set_border_width(10)
	scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	vert.pack_start(scrolled_window, True, True, 0)
	scrolled_window.show()
	scrolled_window.add_with_viewport(self.treeview)
	#vert.pack_start(self.treeview, expand=False, fill=False, padding=10)
	
    	self.add_content(vert)

    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = True
	self.controller.SHOW_BUTTON_HELP    = True
	self.controller.SHOW_BUTTON_BACK    = True
	self.controller.SHOW_BUTTON_FORWARD = True
	self.controller.SHOW_BUTTON_FINISH  = True