import gtk,gobject
import os
import re
import GLIScreen
from Widgets import Widgets
import GLIUtility
# GLIUtility.hash_password(whatever)
# ( <user name>, <password hash>, (<tuple of groups>), <shell>, 
#    <home directory>, <user id>, <user comment> )
#
class Panel(GLIScreen.GLIScreen):
    """
    The Users section of the installer.
    
    @author:    John N. Laliberte <allanonjl@gentoo.org>
    @license:   GPL
    """
    # Attributes:
    title="User Settings"
    columns = []
    users = []
    current_users=[]
    root_verified = False
    
    def __init__(self,controller):
	GLIScreen.GLIScreen.__init__(self, controller)

	content_str = "User screen!"
	
	vert = gtk.VBox(False, 0)
	vert.set_border_width(10)
	
	# setup the top box that data will be shown to the user in.
	self.treedata = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING, gobject.TYPE_STRING, 
				      gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING,
				      gobject.TYPE_STRING)
	
	#for i in range(0, len(self.networking)):
	#	self.treedata.append([i, self.networking[i]['Username'], self.networking[i]['groups'], 
	#			      self.networking[i]['shell'], self.networking[i]['homedir'], 
	#			      self.networking[i]['userid'],self.users['comment']])
		
	self.treeview = gtk.TreeView(self.treedata)
	self.treeview.connect("cursor-changed", self.selection_changed)
	self.columns.append(gtk.TreeViewColumn("Username    ", gtk.CellRendererText(), text=1))
	self.columns.append(gtk.TreeViewColumn("Groups", gtk.CellRendererText(), text=2))
	self.columns.append(gtk.TreeViewColumn("Shell      ", gtk.CellRendererText(), text=3))
	self.columns.append(gtk.TreeViewColumn("HomeDir ", gtk.CellRendererText(), text=4))
	self.columns.append(gtk.TreeViewColumn("UserID", gtk.CellRendererText(), text=5))
	self.columns.append(gtk.TreeViewColumn("Comment", gtk.CellRendererText(), text=6))
	col_num = 0
	for column in self.columns:
		column.set_resizable(True)
		column.set_sort_column_id(col_num)
		self.treeview.append_column(column)
		col_num += 1
	
	self.treewindow = gtk.ScrolledWindow()
	self.treewindow.set_size_request(-1, 125)
	self.treewindow.set_shadow_type(gtk.SHADOW_IN)
	self.treewindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	self.treewindow.add(self.treeview)
	vert.pack_start(self.treewindow, expand=False, fill=False, padding=0)
	
	# now add in the gtk.Notebook
	self.notebook = gtk.Notebook()
	self.notebook.set_tab_pos(gtk.POS_BOTTOM)
	#notebook.set_size_request(-1, -1)
	self.notebook.show()
	self.notebook.set_show_tabs(False)
	self.notebook.set_show_border(False)
	#notebookshow_border = True

	frame = gtk.Frame("")
	frame.set_border_width(10)
	frame.set_size_request(100, 75)
	frame.show()
	
	frame_vert = gtk.VBox(False,0)
	hbox = gtk.HBox(False, 0)
	#frame.add(frame_vert)
	
	# setup the action buttons
	reset = gtk.Button("(Re)Set Root Pass", stock=None)
	reset.connect("clicked", self.reset, "root")
	reset.set_size_request(150, -1)
	reset.show()
	hbox.pack_start(reset, expand=False, fill=False, padding=5)

	edit = gtk.Button("Add/Edit user", stock=None)
	edit.connect("clicked", self.edit, "edit")
	edit.set_size_request(150, -1)
	edit.show()
	hbox.pack_start(edit, expand=False, fill=False, padding=5)
	
	delete = gtk.Button("Delete user", stock=None)
	delete.connect("clicked", self.delete, "delete")
	delete.set_size_request(150, -1)
	delete.show()
	hbox.pack_start(delete, expand=False, fill=False, padding=5)
	
	vert.pack_start(hbox, expand=False, fill=False, padding=0)
	
	# setup the first page
	frame_vert = gtk.VBox(False,0)
	
	# three blank hboxes
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	label = gtk.Label("")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("Root Password")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	self.root1 = gtk.Entry()
	self.root1.set_visibility(False)
	self.root1.set_size_request(150, -1)
	hbox.pack_start(self.root1, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("Verify Password")
	label.set_size_request(150, -1)
	label.show()
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	self.root2 = gtk.Entry()
	self.root2.set_visibility(False)
	self.root2.set_size_request(150, -1)
	hbox.pack_start(self.root2, expand=False, fill=False, padding=5)
	verify = gtk.Button("Verify!")
	verify.connect("clicked", self.verify_root_password, "delete")
	verify.set_size_request(150, 5)
	hbox.pack_start(verify, expand=False, fill=False, padding=5)
	self.verified = gtk.Image()
	self.verified.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_SMALL_TOOLBAR)
	hbox.pack_start(self.verified, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	
	# two more blank hboxes
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	label = gtk.Label("Please Setup Your Root Password")
	self.notebook.append_page(frame_vert, label)
	
	# setup the second page
	frame_vert = gtk.VBox(False,0)
	self.user = {}
	
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("Username")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	self.username = gtk.Entry()
	self.user['username'] = self.username
	self.username.set_size_request(150, -1)
	self.username.set_name("username")
	hbox.pack_start(self.username, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("Password")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	self.password = gtk.Entry()
	self.user['password'] = self.password
	self.password.set_size_request(150, -1)
	self.password.set_name("password")
	self.password.set_visibility(False)
	hbox.pack_start(self.password, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("Groups")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	self.groups = gtk.Entry()
	self.user['groups'] = self.groups
	self.groups.set_size_request(150, -1)
	self.groups.set_name("groups")
	hbox.pack_start(self.groups, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("Shell")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	self.shell = gtk.Entry()
	self.user['shell'] = self.shell
	self.shell.set_size_request(150, -1)
	self.shell.set_name("shell")
	hbox.pack_start(self.shell, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("HomeDir")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	self.homedir = gtk.Entry()
	self.user['homedir'] = self.homedir
	self.homedir.set_size_request(150, -1)
	self.homedir.set_name("homedir")
	hbox.pack_start(self.homedir, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("UserID")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	self.userid = gtk.Entry()
	self.user['userid'] = self.userid
	self.userid.set_size_request(150, -1)
	self.userid.set_name("userid")
	hbox.pack_start(self.userid, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	
	hbox = gtk.HBox(False, 0)
	label = gtk.Label("Comment")
	label.set_size_request(150, -1)
	hbox.pack_start(label, expand=False, fill=False, padding=5)
	self.comment = gtk.Entry()
	self.user['comment'] = self.comment
	self.comment.set_size_request(150, -1)
	self.comment.set_name("comment")
	hbox.pack_start(self.comment, expand=False, fill=False, padding=5)
	button = gtk.Button("Add/Modify User")
	button.connect("clicked", self.add_edit_user, "add/edit user")
	button.set_size_request(150, -1)
	hbox.pack_start(button, expand=False, fill=False, padding=5)
	frame_vert.add(hbox)
	
	label = gtk.Label("Add/Edit a user")
	self.notebook.append_page(frame_vert, label)
	
	# add a blank page
	frame_vert = gtk.VBox(False,0)
	label = gtk.Label("Blank page")
	self.notebook.append_page(frame_vert, label)
	
	vert.pack_start(self.notebook, expand=False, fill=False, padding=0)
	self.add_content(vert)

	
    def selection_changed(self, treeview, data=None):
	treeselection = treeview.get_selection()
	treemodel, treeiter = treeselection.get_selected()
	row = treemodel.get(treeiter, 0)
	print row
    
    def reset(self, widget, data=None):
	# enable the boxen
	self.root_verified=False
	self.root1.set_sensitive(True)
	self.root2.set_sensitive(True)
	self.root1.set_text("")
	self.root2.set_text("")
	self.verified.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_SMALL_TOOLBAR)
	self.blank_the_boxes()
	self.notebook.set_current_page(0)
    
    def edit(self, widget, data=None):
	self.blank_the_boxes()
	# retrieve the selected stuff from the treeview
	treeselection = self.treeview.get_selection()
	treemodel, treeiter = treeselection.get_selected()
	
	# if theres something selected, need to show the details
	if treeiter != None:
	    data={}
	    data["password"],data["username"],data["groups"],data["shell"],\
		data["homedir"],data["userid"],data["comment"] = \
		treemodel.get(treeiter, 0,1,2,3,4,5,6)
	    
	    # fill the current entries
	    for entry_box in self.user:
		box=self.user[entry_box]
		box.set_text(data[box.get_name()])
	
	# show the edit box
	self.notebook.set_current_page(1)
    
    def delete(self, widget, data=None):
	self.blank_the_boxes()
	self.notebook.set_current_page(2)
	self.delete_user()
    
    def add_edit_user(self, widget, data=None):
	# retrieve the entered data
	data={}
	for entry_box in self.user:
	    box=self.user[entry_box]
	    data[box.get_name()] = box.get_text()
	
	# if its not empty, then its valid data! ( just replace i
	#if self.is_data_empty(data) and self.was_previously_added(data):
	if self.is_data_empty(data):
	    # now add it to the box
	    # ( <user name>, <password hash>, (<tuple of groups>), <shell>, 
	    #    <home directory>, <user id>, <user comment> )
	    
	    # if they were previously added, modify them
	    if not self.was_previously_added(data):
		list = self.find_iter(data)
		self.treedata.set(list[data['username']],0,data["password"],
				  1,data['username'],
				  2,data["groups"],
				  3,data["shell"],
				  4,data["homedir"],
				  5,data["userid"],
				  6,data["comment"]
				  )
	    else:
		self.treedata.append([data["password"],data["username"], data["groups"],
				      data["shell"], data["homedir"], 
				      data["userid"], data["comment"]])
	    
	    # blank the current entries
	    self.blank_the_boxes()
    
    def delete_user(self):
	# get which one is selected
	treeselection = self.treeview.get_selection()
	treemodel, treeiter = treeselection.get_selected()
	# if something is selected, remove it!
	if treeiter != None:
	    row = treemodel.get(treeiter, 1)
	    
	    # remove it from the current_users
	    self.current_users.remove(row[0])
	    
	    # remove it from the profile
	    self.controller.install_profile.remove_user(row[0])
	    
	    # remove it from the treeview
	    iter = self.treedata.remove(treeiter)
    
    def verify_root_password(self, widget, data=None):
	if self.root1.get_text() == self.root2.get_text():
	    # passwords match!
	    self.root_verified = True
	    # disable the boxen
	    self.root1.set_sensitive(False)
	    self.root2.set_sensitive(False)
	    self.verified.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_SMALL_TOOLBAR)
	    
    def blank_the_boxes(self):
	# blank the current entries
	for entry_box in self.user:
	    box=self.user[entry_box]
	    box.set_text("")
    
    def is_data_empty(self,data):
	value = True
	for item in data:
	    # if any of the items are blank, return False!
	    if item == "":
		value = False
	    
	return value
    
    def was_previously_added(self,data):
	value = False
	# if the username appears in the treestore, display error
	username_list = self.get_treeview_usernames()
	if data["username"] in username_list:
	    # show error box to modify, duplicate user.
	    error = Widgets().error_Box("Duplicate User","This will modify the user!")
	    result = error.run()
	    if result == gtk.RESPONSE_ACCEPT:
		error.destroy()
	else:
	    value = True
	    
	return value
    
    def find_iter(self,data):
	data_stor = {}
	treeiter = self.treedata.get_iter_first()
	
	while treeiter != None:
	    username = self.treedata.get_value(treeiter, 1)
	    if username == data["username"]:
		data_stor[username]=treeiter
	    treeiter = self.treedata.iter_next(treeiter)

	return data_stor
    
    def get_treeview_usernames(self):
	data = []
	treeiter = self.treedata.get_iter_first()
	
	while treeiter != None:
	    data.append(self.treedata.get_value(treeiter, 1))
	    treeiter = self.treedata.iter_next(treeiter)

	return data

    def get_treeview_data(self):
	data = []
	treeiter = self.treedata.get_iter_first()
	
	while treeiter !=None:
	    user = self.treedata.get_value(treeiter,1)
	    passwd = self.treedata.get_value(treeiter,0)
	    pass_hash = GLIUtility.hash_password(passwd)
	    groups = self.treedata.get_value(treeiter,2)
	    shell = self.treedata.get_value(treeiter,3)
	    homedir = self.treedata.get_value(treeiter,4)
	    userid = self.treedata.get_value(treeiter,5)
	    comment = self.treedata.get_value(treeiter,6)
	    try:
		group_tuple = tuple(groups.split(","))
	    except:
		# must be only 1 group
		group_tuple = (groups)
	    
	    data.append([user,pass_hash,group_tuple,shell,homedir,userid,comment])
	    treeiter = self.treedata.iter_next(treeiter)
	    
	return data
    
    def activate(self):
	self.controller.SHOW_BUTTON_EXIT    = True
	self.controller.SHOW_BUTTON_HELP    = True
	self.controller.SHOW_BUTTON_BACK    = True
	self.controller.SHOW_BUTTON_FORWARD = True
	self.controller.SHOW_BUTTON_FINISH  = False
    
    def deactivate(self):
	# store everything
	if (self.root_verified):
	    # store the root password
	    root_hash = GLIUtility.hash_password(self.root1.get_text())
	    self.controller.install_profile.set_root_pass_hash(None,root_hash,None)
	    
	    # now store all the entered users
	    #( <user name>, <password hash>, (<tuple of groups>), <shell>, 
	    #  <home directory>, <user id>, <user comment> )
	    # retrieve everything
	    data = self.get_treeview_data()
	    print data

	    i=0
	    for user in data:
		if data[i][0] not in self.current_users:
		    self.controller.install_profile.add_user(None,(data[i][0],data[i][1],
								   data[i][2],data[i][3],data[i][4],
								   data[i][5],data[i][6]),None
							 )
		    self.current_users.append(data[i][0])
		else:
		    # they must already be added
		    pass
		i=i+1
		
	    return True
	else:
	    msgbox=Widgets().error_Box("Error","You have not verified your root password!")
	    msgbox.run()
	    msgbox.destroy()
	