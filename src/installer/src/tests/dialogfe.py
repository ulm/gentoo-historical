#!/usr/bin/python

import dialog
import GLIInstallProfile
import GLIClientConfiguration
import GLIClientController
import GLIUtility
import sys
import crypt
import random
import commands
import string
import copy
import signal

d = dialog.Dialog()
client_profile = GLIClientConfiguration.ClientConfiguration()
install_profile = GLIInstallProfile.InstallProfile()
waiting_for_install = False
gauge_progress = 0

def signal_handler(signum, frame):
	global gauge_progress
	global waiting_for_install
	gauge_progress += 10
	d.gauge_iterate(gauge_progress, "Install progress:")
	if gauge_progress >= 100:
		waiting_for_install = False
		d.gauge_stop()

def run(cmd):
	output_string = commands.getoutput(cmd)
	output_list = []
	while output_string.find("\n") != -1:
		index = output_string.find("\n") + 1
		output_list.append(output_string[:index])
		output_string = output_string[index:]

	return output_list

def get_random_salt():
        chars = "./abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        chars = list(chars)
        c1 = chars[random.randint(0,len(chars)-1)]
        c2 = chars[random.randint(0,len(chars)-1)]
        return c1 + c2

def set_partitions():
	import string, re
	try:
		import GLIStorageDevice
	except:
		d.msgbox("Sorry, you don't have agaffney's kickass GLIStorageDevice module")
		return

	if not d.yesno("If you continue, your previous changes (if any) will be reset. Continue?"): return
	use_existing = d.yesno("Do you want to use the existing disk partitions?")

	devices = {}
	drives = GLIStorageDevice.detect_devices()
	drives.sort()
	for drive in drives:
		devices[drive] = GLIStorageDevice.Device(drive)
		if use_existing: devices[drive].set_partitions_from_disk()
	while 1:
		drive_to_partition = d.menu("Which drive would you like to partition?", list=drives, cancellabel="Done")
		if drive_to_partition == None: break
		while 1:
			partitions = devices[drive_to_partition].get_partitions()
			partsmenu = devices[drive_to_partition].get_ordered_partition_list()
			part_to_edit = d.menu("Which partition would you like to edit?", list=partsmenu, cancellabel="Back")
			if part_to_edit == None: break
			if re.compile("^Free Space").match(part_to_edit) != None:
				new_start, new_end = re.compile("^Free Space \((\d+)\s*-\s*(\d+)\)").match(part_to_edit).groups()
				new_start2 = d.inputbox("New partition start (minimum " + new_start + ")?", init=new_start)
				new_end2 = d.inputbox("New partition end (maximum " + new_end + ")?", init=new_end)
				minor = devices[drive_to_partition].get_partition_at(int(new_start) - 1) + 1
				id = d.inputbox("New partition's type?", init="ext3")
				if (int(new_start2) < int(new_start)) or (int(new_end2) > int(new_end)):
					d.msgbox("Cannot create new partition because it is not within the bounds of the selected free space.")
					continue
				devices[drive_to_partition].add_partition(devices[drive_to_partition].get_free_minor_at(int(new_start2), int(new_end2)), int(new_start2), int(new_end2), id)
			else:
				while 1:
					tmpdevice, tmpminor = re.compile("^(/dev/[a-zA-Z]+)(\d+):").search(part_to_edit).groups()
					tmppart = partitions[int(tmpminor)]
					tmptitle = tmpdevice + tmpminor + ": " + str(tmppart.get_start()) + "-" + str(tmppart.get_end())
					part_action = d.menu(tmptitle, list=["Delete", "Resize", "Change type (linux, swap, etc.)"], cancellabel="Back")
					if part_action == "Delete":
						answer = d.yesno("Are you sure you want to delete the partition " + tmpdevice + tmpminor + "?");
						if answer == True:
							tmpdev = tmppart.get_device()
							tmpdev.remove_partition(int(tmpminor))
							break
					elif part_action == "Resize":
						min_end = tmppart.get_min_cylinders_for_resize()
						max_end = tmppart.get_max_cylinders_for_resize()
						tmptitle = "Resize " + part_to_edit + " (minimum end: " + str(min_end) + ", maximum end: " + str(max_end) + ")"
						tmpinit = str(tmppart.get_start()) + "-" + str(tmppart.get_end())
						answer = d.inputbox(tmptitle, init=tmpinit)
						if answer == None: continue
						new_start, new_end = re.compile("^(\d+)\s*-\s*(\d+)$").match(answer).groups()
						if int(new_end) < min_end:
							d.msgbox("New end specified is too small")
							continue
						if int(new_end) > max_end:
							d.msgbox("New end specified is too large")
							continue
						if not tmppart.resize(int(new_start), int(new_end)):
							d.msgbox("Cannot resize partition because the new size conflicts with an existing partition.")
							continue
					elif part_action == "Change type (linux, swap, etc.)":
						answer = d.inputbox("Enter a type for partition" + str(tmpminor), init=tmppart.get_type())
						tmppart.set_type(answer)
					elif part_action == None:
						break
	if d.yesno("Would you like to save changes?"):
		parts_tmp = install_profile.get_partition_tables()
		for part in devices.keys():
			if GLIUtility.is_file(part) and parts_tmp.has_key(part): del parts_tmp[part]
			parts_tmp[part] = devices[part].get_install_profile_structure()
		install_profile.set_partition_tables(parts_tmp)

def set_nfs_mounts():
# This is where any NFS mounts will be specified
	nfs_mounts = copy.deepcopy(install_profile.get_partition_tables())
	for i in nfs_mounts.keys():
		if GLIUtility.is_file(i): del nfs_mounts[i]
	while 1:
		menulist = []
		for host in nfs_mounts.keys():
			for export in nfs_mounts[host].keys():
				menulist.append(host + ":" + export)
		menulist.append("Add new NFS mount")
		menuitem = d.menu("Select a NFS mount", list=menulist, cancellabel="Done")
		if menuitem == None:
			if d.yesno("Do you want to save changes?"):
				parts_tmp = install_profile.get_partition_tables()
				for part in parts_tmp.keys():
					if not GLIUtility.is_file(part): del parts_tmp[part]
				for host in nfs_mounts.keys():
					parts_tmp[host] = nfs_mounts[host]
				install_profile.set_partition_tables(parts_tmp)
			break
		if menuitem == "Add new NFS mount":
			nfsmount = d.inputbox("Enter NFS mount or just enter the IP/hostname to search for available mounts")
			if nfsmount == None: continue
			if not GLIUtility.is_nfs(nfsmount):
				if GLIUtility.is_ip(nfsmount) or GLIUtility.is_hostname(nfsmount):
					remotemounts = run("/usr/sbin/showmount -e " + nfsmount + " 2>&1 | egrep '^/' | cut -d ' ' -f 1 && echo")
					if not len(remotemounts):
						d.msgbox("No NFS exports detected on " + nfsmount)
						continue
					for i in range(0, len(remotemounts)):
						remotemounts[i] = string.strip(remotemounts[i])
					nfsmount2 = d.menu("Select a NFS export", list=remotemounts, cancellabel="Back")
					if nfsmount2 == None: continue
					if not nfs_mounts.has_key(nfsmount):
						nfs_mounts[nfsmount] = {}
					if nfs_mounts[nfsmount].has_key(nfsmount2):
						if not d.yesno("There is already an entry for " + nfsmount + ":" + nfsmount2 + ". Do you want to overwrite it?"):
							continue
					nfs_mounts[nfsmount][nfsmount2] = { 'mountpoint': '', 'mountopts': '', 'type': 'nfs', 'mb': 0, 'start': 0, 'end': 0, 'format': False, 'minor': 0 }
					menuitem = nfsmount + ":" + nfsmount2
				else:
					d.msgbox("Enter '" + nfsmount + "' is not a valid IP or hostname")
		if menuitem.find(':') != -1:
			colon_location = menuitem.find(':')
			host = menuitem[:colon_location]
			export = menuitem[colon_location+1:]
			tmppart = nfs_mounts[host][export]
			mountpoint = d.inputbox("Enter a mountpoint", init=tmppart['mountpoint'])
			if mountpoint != None: tmppart['mountpoint'] = mountpoint
			mountopts = d.inputbox("Enter mount options", init=tmppart['mountopts'])
			if mountopts != None: tmppart['mountopts'] = mountopts
			nfs_mounts[host][export] = tmppart
			

def set_install_stage():
# The install stage and stage tarball will be selected here
	install_stage = d.inputbox("Which stage do you want to start at?", init=install_profile.get_install_stage())
	if install_stage != None: install_profile.set_install_stage(None, install_stage, None)
	stage_tarball = d.inputbox("Where is the stage tarball located (URL or local file)?", init=install_profile.get_stage_tarball_uri())
	try:
		if stage_tarball != None: install_profile.set_stage_tarball_uri(None, stage_tarball, None)
	except:
		d.msgbox("The specified URI is invalid")

def set_portage_tree():
# This section will ask whether to sync the tree, whether to use a snapshot, etc.
	portage_tree_sync = d.menu("How do you want to sync the portage tree?", list=["Normal 'emerge sync'", "Webrsync (rsync is firewalled)", "None (snapshot or NFS mount)"])
	if portage_tree_sync != None:
		if portage_tree_sync == "Normal 'emerge sync'": install_profile.set_portage_tree_sync_type(None, "sync", None)
		if portage_tree_sync == "Webrsync (rsync is firewalled)": install_profile.set_portage_tree_sync_type(None, "webrsync", None)
		if portage_tree_sync == "None (snapshot or NFS mount)": install_profile.set_portage_tree_sync_type(None, "custom", None)
	if portage_tree_sync == "None (snapshot or NFS mount)":
		if d.yesno("Do you want to use a portage tree snapshot?"):
			snapshot = d.inputbox("Enter portage tree snapshot URI", init=install_profile.get_portage_tree_snapshot_uri())
			try:
				if snapshot != None: install_profile.set_portage_tree_snapshot_uri(None, snapshot, None)
			except:
				d.msgbox("The specified URI is invalid")

def set_make_conf():
# This section will be for setting things like CFLAGS, ACCEPT_KEYWORDS, and USE
	make_conf = install_profile.get_make_conf()
	while 1:
		menuitem = d.menu("Choose a variable to edit", list=["ACCEPT_KEYWORDS", "CFLAGS", "CHOST", "MAKEOPTS", "FEATURES", "USE"], cancellabel="Done")
		if menuitem != None:
			oldval = ""
			if make_conf.has_key(menuitem): oldval = make_conf[menuitem]
			newval = d.inputbox("Enter new value for " + menuitem, init=oldval)
			if newval != None:
				make_conf[menuitem] = newval
				install_profile.set_make_conf(make_conf)
		else:
			break

def set_kernel():
# This section will be for choosing kernel sources, choosing (and specifying) a custom config or genkernel, modules to load at startup, etc.
	kernel_sources = ("vanilla-sources", "gentoo-sources", "development-sources", "gentoo-dev-sources", "hardened-sources")
	menuitem = d.menu("Choose a kernel sources package", list=kernel_sources)
	if menuitem != None: install_profile.set_kernel_source_pkg(None, menuitem, None)

def set_boot_loader():
	boot_loaders = ("grub", "lilo")
	menuitem = d.menu("Choose a boot loader", list=boot_loaders)
	if menuitem != None: install_profile.set_boot_loader_pkg(None, menuitem, None)
	if d.yesno("Do you want the boot loader installed in the MBR?"):
		install_profile.set_boot_loader_mbr(None, True, None)
	else:
		install_profile.set_boot_loader_mbr(None, False, None)

def set_timezone():
# This section will be for setting the timezone. It will eventually pull from /usr/share/zoneinfo or something
	timezone = d.inputbox("Enter a timezone", init=install_profile.get_time_zone())
	if timezone != None: install_profile.set_time_zone(None, timezone, None)

def set_networking():
# This section will be for setting up network interfaces, defining DNS servers, default routes/gateways, etc.
	while 1:
		menuitem = d.menu("Choose an option", list=["Edit Interfaces", "DNS Servers", "Default Gateway"], cancellabel="Done")
		if menuitem == None: break
		if menuitem == "Edit Interfaces":
			while 1:
				interfaces = install_profile.get_network_interfaces()
				menu_list = interfaces.keys()
				menu_list.sort()
				menu_list.append("Add new interface")
				menuitem = d.menu("Select an interface", list=menu_list, cancellabel="Back")
				if menuitem == None: break
				newnic = None
				if menuitem == "Add new interface":
					newnic = d.inputbox("Enter name for new interface (eth0, ppp0, etc.)")
					if newnic == None: continue
					if newnic in interfaces:
						d.msgbox("An interface with the name is already defined.")
						continue
					interfaces[newnic] = ("", "", "")
					menuitem = newnic
				menuitem2 = ""
				if newnic == None:
					menuitem2 = d.menu("What do you want to do with interface " + menuitem + "?", list=["Edit", "Rename", "Delete"], cancellabel="Back")
					if menuitem2 == None: continue
				else:
					menuitem2 = "Edit"
				if menuitem2 == "Edit":
					tmpnic = [interfaces[menuitem][0], interfaces[menuitem][1], interfaces[menuitem][2]]
					ip = d.inputbox("Enter an IP address for " + menuitem + " or 'dhcp' for DHCP", init=tmpnic[0])
					if ip != None: tmpnic[0] = ip
					if ip == "dhcp" or ip == "DHCP":
						tmpnic[1] = ""
						tmpnic[2] = ""
					else:
						netmask = d.inputbox("Enter the netmask", init=tmpnic[2])
						if netmask != None: tmpnic[2] = netmask
						broadcast = d.inputbox("Enter a broadcast", init=tmpnic[1])
						if broadcast != None: tmpnic[1] = broadcast
					interfaces[menuitem] = (tmpnic[0], tmpnic[1], tmpnic[2])
				elif menuitem2 == "Rename":
					d.msgbox("Not implimented yet")
				elif menuitem2 == "Delete":
					if d.yesno("Are you sure you want to remove the interface " + menuitem + "?"):
						del interfaces[menuitem]
				install_profile.set_network_interfaces(interfaces)
		elif menuitem == "DNS Servers":
			d.msgbox("DNS Servers")
		elif menuitem == "Default Gateway":
			d.msgbox("Default Gateway")

def set_cron_daemon():
	cron_daemons = ("vixie-cron", "fcron", "dcron")
	menuitem = d.menu("Choose a cron daemon", list=cron_daemons)
	if menuitem != None:
		if menuitem == "None": menuitem == ""
		install_profile.set_cron_daemon_pkg(None, menuitem, None)

def set_logger():
	loggers = ("syslog-ng", "metalog", "syslogkd")
	menuitem = d.menu("Choose a system logger", list=loggers)
	if menuitem != None: install_profile.set_logging_daemon_pkg(None, menuitem, None)

def set_extra_packages():
	d.msgbox("This section is for selecting extra packages (pcmcia-cs, rp-pppoe, xorg-x11, etc.) and setting them up")

def set_rc_conf():
# This section is for editing /etc/rc.conf
	rc_conf = install_profile.get_rc_conf()
	menulist = ["KEYMAP", "SET_WINDOWSKEYS", "EXTENDED_KEYMAPS", "CONSOLEFONT", "CONSOLETRANSLATION", "CLOCK", "EDITOR", "PROTOCOLS", "DISPLAYMANAGER", "XSESSION"]
	while 1:
		menuitem = d.menu("Choose a variable to edit", list=menulist, cancellabel="Done")
		if menuitem != None:
			oldval = ""
			if rc_conf.has_key(menuitem): oldval = rc_conf[menuitem]
			newval = d.inputbox("Enter new value for " + menuitem, init=oldval)
			if newval != None:
				rc_conf[menuitem] = newval
				install_profile.set_rc_conf(rc_conf)
		else:
			break

def set_root_password():
# The root password will be set here
	passwd1 = d.passwordbox("Enter the new root password")
	passwd2 = d.passwordbox("Enter the new root password again")
	if passwd1 != passwd2:
		d.msgbox("The passwords do not match")
		return
	if passwd1 == None or passwd2 == None: return
	install_profile.set_root_pass_hash(None, crypt.crypt(passwd1, get_random_salt()), None)

def set_additional_users():
# This section will be for adding non-root users
	users = copy.deepcopy(install_profile.get_users())
	if type(users) == "list":
		tmpusers = {}
		for user in users:
			tmpusers[user[0]] = [user[0], user[1], user[2], user[3]
	while 1:
		menu_list = []
		for user in users:
			menu_list.append(user[0])
		menu_list.sort()
		menu_list.append("Add user")
		menuitem = d.menu("Choose a user to edit", list=menu_list, cancellabel="Done")
		if menuitem == None:
			if d.yesno("Do you want to save changes?"):
				install_profile.set_users(users)
			break
		if menuitem == "Add user":
			newuser = d.inputbox("Enter the username for the new user")
			if newuser == None: continue
			for user in users:
				if newuser == user[0]:
					d.msgbox("A user with that name already exists")
					continue
			new_user = (newuser, '', ('users'), '/bin/bash', '/home' + newuser, '', '')
			users.append(new_user)
			menuitem = newuser
		while 1:
			menuitem2 = d.menu("Choose an option for user " + menuitem, list=["Password", "Group Membership", "Shell", "Home Directory", "UID", "Comment", "Delete"], cancellabel="Back")
			if menuitem2 == None: break
			if menuitem2 == "Password":
				passwd1 = d.passwordbox("Enter the new password")
				passwd2 = d.passwordbox("Enter the new password again")
				if passwd1 != passwd2:
					d.msgbox("The passwords do not match")
					continue
				if passwd1 == None or passwd2 == None: continue
				for user in users:
					if user[0] == menuitem: user[1] = crypt.crypt(passwd1, get_random_salt())
					continue
			elif menuitem2 == "Group Membership":
				d.msgbox("Groups")
			elif menuitem2 == "Shell":
				d.msgbox("Shell")
			elif menuitem2 == "Home Directory":
				d.msgbox("homedir")
			elif menuitem2 == "UID":
				d.msgbox("UID")
			elif menuitem2 == "Comment":
				d.msgbox("Comment")
			elif menuitem2 == "Delete":
				if d.yesno("Are you sure you want to delete the user " + menuitem + "?"):
					for i in range(0, len(users)):
						if users[i][0] == menuitem:
							users.pop(i)
							break
					break


signal.signal(signal.SIGUSR1, signal_handler)
d.setBackgroundTitle("Gentoo Linux Installer")
d.msgbox("Welcome to The Gentoo Linux Installer. This is a TESTING release. If your system dies a horrible, horrible death, don't come crying to us (okay, you can cry to klieber).", height=10, width=50, title="Welcome")

#if d.yesno("Do you want to use the ClientController?"):
#	client_controller_xml = None
#	if d.yesno("Do you have a previously generated XML file for the ClientController?"):
#		client_controller_xml = d.inputbox("Enter the filename of the XML file")
#	if client_controller_xml == None:
#		pass
#		# code to fill in data in client_profile
#	else:
#		client_profile.parse(client_controller_xml)
#	# code to actually run the client_controller functions
#	d.msgbox("ClientController done")

install_profile_xml_file = None
fn = (
	{ 'text': "Partitioning", 'fn': set_partitions },
	{ 'text': "NFS mounts", 'fn': set_nfs_mounts },
	{ 'text': "Install Stage", 'fn': set_install_stage },
	{ 'text': "Portage Tree", 'fn': set_portage_tree },
	{ 'text': "make.conf", 'fn': set_make_conf },
	{ 'text': "Kernel", 'fn': set_kernel },
	{ 'text': "Bootloader", 'fn': set_boot_loader },
	{ 'text': "Timezone", 'fn': set_timezone },
	{ 'text': "Networking", 'fn': set_networking },
	{ 'text': "Cron daemon", 'fn': set_cron_daemon },
	{ 'text': "Logging daemon", 'fn': set_logger },
	{ 'text': "Extra packages", 'fn': set_extra_packages },
	{ 'text': "rc.conf", 'fn': set_rc_conf },
	{ 'text': "Root password", 'fn': set_root_password },
	{ 'text': "Additional Users", 'fn': set_additional_users },
     )
while 1:
	if d.yesno("Do you have a previously generated InstallProfile XML file?"):
		install_profile_xml_file = d.inputbox("Enter the filename of the XML file")
		if install_profile_xml_file == None: break
		if GLIUtility.is_file(install_profile_xml_file): break
		d.msgbox("Cannot open file " + install_profile_xml_file, height=7, width=50)
		install_profile_xml_file = None
		continue
	break
if install_profile_xml_file != None:
	install_profile.parse(install_profile_xml_file)
while 1:
	menu_list = []
	for item in fn:
		menu_list.append(item['text'])
	menu_list.append("Install!")
	menuitem = d.menu("Choose an option", list=menu_list, height=20, cancellabel="Exit")
	if menuitem == None:
		if d.yesno("Do you really want to exit before the install is complete?"):
			if d.yesno("Do you want to save the InstallProfile XML file?"):
				if install_profile_xml_file == None: install_profile_xml_file = ""
				filename = d.inputbox("Enter a filename for the XML file", init=install_profile_xml_file)
				if filename == None: sys.exit()
				if GLIUtility.is_file(filename):
					if not d.yesno("The file " + filename + " already exists. Do you want to overwrite it?"):
						sys.exit()
				configuration = open(filename ,"w")
				configuration.write(install_profile.serialize())
				configuration.close()
			sys.exit()
	for item in fn:
		if menuitem == item['text']:
			item['fn']()
			continue
	if menuitem == "Install!":
		waiting_for_install = True
		d.gauge_start(0, "Install progress:", title="Installing")
		while waiting_for_install: pass
		d.msgbox("Install done!")
		sys.exit()
