#!/usr/bin/python

import sys
sys.path.append("../..")

import dialog
import GLIInstallProfile
import GLIClientConfiguration
import GLIClientController
import GLIUtility
import GLIStorageDevice
import crypt
import random
import commands
import string
import copy
import signal
#import pprint
import time
import string
import re
import glob
import os

d = dialog.Dialog()
client_profile = GLIClientConfiguration.ClientConfiguration()
install_profile = GLIInstallProfile.InstallProfile()
cc = GLIClientController.GLIClientController(pretend=True)
exception_waiting = None
next_step_waiting = False
install_done = False
local_install = True

DLG_OK = 0
DLG_YES = 0
DLG_CANCEL = 1
DLG_NO = 1
DLG_ESC = 2
DLG_ERROR = 3
DLG_EXTRA = 4
DLG_HELP = 5

def dmenu_list_to_choices(list):
	choices = []
	for i in range(0, len(list)):
		choices.append((str(i + 1), list[i]))

	return choices

def run(cmd):
	output_string = commands.getoutput(cmd)
	output_list = []
	while output_string.find("\n") != -1:
		index = output_string.find("\n") + 1
		output_list.append(output_string[:index])
		output_string = output_string[index:]

	return output_list

def set_partitions():
	if not d.yesno("This will reset any changes you have made. Continue?") == DLG_YES: return
#	devices = copy.deepcopy(install_profile.get_partition_tables())
	devices = {}
	drives = GLIStorageDevice.detect_devices()
	drives.sort()
#	use_existing = False
#	if not devices:
	use_existing = local_install #(d.yesno("Do you want to use the existing disk partitions?") == DLG_YES)
	for drive in drives:
		devices[drive] = GLIStorageDevice.Device(drive)
		if use_existing: devices[drive].set_partitions_from_disk()
	while 1:
		code, drive_to_partition = d.menu("Which drive would you like to partition?", choices=dmenu_list_to_choices(drives), cancel="Done")
		if code != DLG_OK: break
		drive_to_partition = drives[int(drive_to_partition)-1]
		while 1:
			partitions = devices[drive_to_partition].get_partitions()
			partsmenu = devices[drive_to_partition].get_ordered_partition_list()
			code, part_to_edit = d.menu("Which partition would you like to edit?", choices=dmenu_list_to_choices(partsmenu), cancel="Back")
			if code != DLG_OK: break
			part_to_edit = partsmenu[int(part_to_edit)-1]
			if re.compile("^Free Space").match(part_to_edit) != None:
				new_start, new_end = re.compile("^Free Space \((\d+)\s*-\s*(\d+)\)").match(part_to_edit).groups()
				code, new_start2 = d.inputbox("New partition start (minimum " + new_start + ")?", init=new_start)
				if code != DLG_OK: continue
				code, new_end2 = d.inputbox("New partition end (maximum " + new_end + ")?", init=new_end)
				if code != DLG_OK: continue
				minor = devices[drive_to_partition].get_partition_at(int(new_start) - 1) + 1
				part_types = ["ext2", "ext3", "linux-swap", "fat32", "ntfs", "extended", "other"]
				code, type = d.menu("Type for new partition", choices=dmenu_list_to_choices(part_types))
				if code != DLG_OK: continue
				type = part_types[int(type)-1]
				if type == "other":
					code, type = d.inputbox("New partition's type?")
				if code != DLG_OK: continue
				if (int(new_start2) < int(new_start)) or (int(new_end2) > int(new_end)):
					d.msgbox("Cannot create new partition because it is not within the bounds of the selected free space.")
					continue
				devices[drive_to_partition].add_partition(devices[drive_to_partition].get_free_minor_at(int(new_start2), int(new_end2)), int(new_start2), int(new_end2), type)
			else:
				while 1:
					tmpdevice, tmpminor = re.compile("^(/dev/[a-zA-Z]+)(\d+):").search(part_to_edit).groups()
					tmppart = partitions[int(tmpminor)]
					tmptitle = tmpdevice + tmpminor + ": " + str(tmppart.get_start()) + "-" + str(tmppart.get_end())
					menulist = ["Delete", "Mount Point", "Mount Options"]
					code, part_action = d.menu(tmptitle, choices=dmenu_list_to_choices(menulist), cancel="Back")
					if code != DLG_OK: break
					part_action = menulist[int(part_action)-1]
					if part_action == "Delete":
						answer = (d.yesno("Are you sure you want to delete the partition " + tmpdevice + tmpminor + "?") == DLG_YES)
						if answer == True:
							tmpdev = tmppart.get_device()
							tmpdev.remove_partition(int(tmpminor))
							break
					elif part_action == "Mount Point":
						code, answer = d.inputbox("Enter a type for partition" + str(tmpminor), init=tmppart.get_mountopts())
						if code == DLG_OK: tmppart.set_mountpoint(answer)
					elif part_action == "Mount Options":
						code, answer = d.inputbox("Enter a type for partition" + str(tmpminor), init=tmppart.get_mountopts())
						if code == DLG_OK: tmppart.set_mountopts(answer)
	if d.yesno("Would you like to save changes?") == DLG_YES:
		parts_tmp = {}
		for part in devices.keys():
			parts_tmp[part] = devices[part].get_install_profile_structure()
		install_profile.set_partition_tables(parts_tmp)

def set_network_mounts():
# This is where any NFS mounts will be specified
	network_mounts = copy.deepcopy(install_profile.get_network_mounts())
	while 1:
		menulist = []
		for mount in network_mounts:
			menulist.append(mount['host'] + ":" + mount['export'])
		menulist.append("Add new network mount")
		choices = dmenu_list_to_choices(menulist)
		code, menuitemidx = d.menu("Select a network mount", choices=choices, cancel="Done")
		if code:
			if d.yesno("Do you want to save changes?") == DLG_YES:
				install_profile.set_network_mounts(network_mounts)
			break
		menuitem = menulist[int(menuitemidx)-1]
		if menuitem == "Add new network mount":
			code, nfsmount = d.inputbox("Enter NFS mount or just enter the IP/hostname to search for available mounts")
			if code != DLG_OK: continue
			if not GLIUtility.is_nfs(nfsmount):
				if GLIUtility.is_ip(nfsmount) or GLIUtility.is_hostname(nfsmount):
					remotemounts = run("/usr/sbin/showmount -e " + nfsmount + " 2>&1 | egrep '^/' | cut -d ' ' -f 1 && echo")
					if not len(remotemounts):
						d.msgbox("No NFS exports detected on " + nfsmount)
						continue
					for i in range(0, len(remotemounts)):
						remotemounts[i] = string.strip(remotemounts[i])
					code, nfsmount2 = d.menu("Select a NFS export", choices=dmenu_list_to_choices(remotemounts), cancel="Back")
					if code != DLG_OK: continue
					nfsmount2 = remotemounts[int(nfsmount2)-1]
				else:
					d.msgbox("Enter '" + nfsmount + "' is not a valid IP or hostname")
			else:
				colon_location = nfsmount.find(':')
				menuitem = nfsmount
				nfsmount = menuitem[:colon_location]
				nfsmount2 = menuitem[colon_location+1:]
			for mount in network_mounts:
				if nfsmount == mount['host'] and nfsmount2 == mount['export']:
					d.msgbox("There is already an entry for " + nfsmount + ":" + nfsmount2 + ".")
					nfsmount = None
					break
			if nfsmount == None: continue
			network_mounts.append({'export': nfsmount2, 'host': nfsmount, 'mountopts': '', 'mountpoint': '', 'type': 'nfs'})
			menuitem = nfsmount + ":" + nfsmount2
			menuitemidx = len(network_mounts)

		if menuitem.find(':') != -1:
			colon_location = menuitem.find(':')
			tmpmount = network_mounts[int(menuitemidx)-1]
			code, mountpoint = d.inputbox("Enter a mountpoint", init=tmpmount['mountpoint'])
			if code == DLG_OK: tmpmount['mountpoint'] = mountpoint
			code, mountopts = d.inputbox("Enter mount options", init=tmpmount['mountopts'])
			if code == DLG_OK: tmpmount['mountopts'] = mountopts
			network_mounts[int(menuitemidx)-1] = tmpmount

def set_install_stage():
# The install stage and stage tarball will be selected here
	install_stages = ("1","2","3","3 + GRP (use binary packages)")
	code, install_stage = d.menu("Which stage do you want to start at?", choices=dmenu_list_to_choices(install_stages), cancel="Back")
	if code == DLG_OK:
		install_stage = install_stages[int(install_stage)-1]
		if install_stage == "3 + GRP (use binary packages)":
			install_stage = "3"
			install_profile.set_grp_install(None, True, None)
		install_profile.set_install_stage(None, install_stage, None)
	tarball_options = ("Use Local", "Specify URI")
	code, tarball_option = d.menu("Select a local stage " + install_stage + " tarball or manually specify a URI:", choices=dmenu_list_to_choices(tarball_options))
	if code == DLG_OK:
		tarball_option = tarball_options[int(tarball_option)-1]
		if tarball_option == "Use Local":
			stages_dir = "/mnt/cdrom/stages"
			if os.path.isdir(stages_dir) and os.listdir(stages_dir):
				local_tarballs = glob.glob(stages_dir + "/stage" + install_stage + "*.bz2")
				local_tarballs.sort()
				code, stage_tarball = d.menu("Select a local tarball:", choices=dmenu_list_to_choices(local_tarballs))
				if code != DLG_OK: return
				stage_tarball = local_tarballs[int(stage_tarball)-1]
			else:
				d.msgbox("There don't seem to be any local tarballs available.  Hit OK to manually specify a URI.")
				tarball_option = "Specify URI"
		if tarball_option != "Use Local": 
			code, stage_tarball = d.inputbox("Specify the stage tarball URI or local file:", init=install_profile.get_stage_tarball_uri())
	#If Doing a local install, check for valid file:/// uri
	if code == DLG_OK:
		if stage_tarball:
			if not GLIUtility.is_uri(stage_tarball, checklocal=local_install):
				d.msgbox("The specified URI is invalid.  It was not saved.  Please go back and try again.");
			else install_profile.set_stage_tarball_uri(None, stage_tarball, None)
		else: d.msgbox("No URI was specified!")
		#if d.yesno("The specified URI is invalid. Use it anyway?") == DLG_YES: install_profile.set_stage_tarball_uri(None, stage_tarball, None)

def set_portage_tree():
# This section will ask whether to sync the tree, whether to use a snapshot, etc.
	menulist = ["Normal 'emerge sync'", "Webrsync (rsync is firewalled)", "None (local snapshot or NFS mount)"]
	code, portage_tree_sync = d.menu("How do you want to sync the portage tree?", choices=dmenu_list_to_choices(menulist))
	if code != DLG_OK: return
	portage_tree_sync = menulist[int(portage_tree_sync)-1]
	#FIX ME when python 2.4 comes out.
	if portage_tree_sync == "Normal 'emerge sync'": install_profile.set_portage_tree_sync_type(None, "sync", None)
	if portage_tree_sync == "Webrsync (rsync is firewalled)": install_profile.set_portage_tree_sync_type(None, "webrsync", None)
	if portage_tree_sync == "None (local snapshot or NFS mount)":
		install_profile.set_portage_tree_sync_type(None, "custom", None)		
		snapshot_options = ("Use Local", "Specify URI")
		code, snapshot_option = d.menu("Select a local portage snapshot or manually specify a location:", choices=dmenu_list_to_choices(snapshot_options))
		snapshot_option = snapshot_options[int(snapshot_option)-1]
		if snapshot_option == "Use Local":
			snapshot_dir = "/mnt/cdrom/snapshots"
			if os.path.isdir(snapshot_dir) and os.listdir(stages_dir):
				local_snapshots = glob.glob(snapshot_dir + "/portage*.bz2")
				if len(local_snapshots) == 1:
					snapshot = local_snapshots[0]
				else:
					local_snapshots.sort()
					code, snapshot = d.menu("Select a local portage snapshot:", choices=dmenu_list_to_choices(local_snapshots))
					if code != DLG_OK: return
					snapshot = local_snapshots[int(snapshot)-1]
			else:
				d.msgbox("There don't seem to be any local portage snapshots available.  Hit OK to manually specify a URI.")
				snapshot_option = "Specify URI"
		if snapshot_option != "Use Local":
			code, snapshot = d.inputbox("Enter portage tree snapshot URI", init=install_profile.get_portage_tree_snapshot_uri())
		if code == DLG_OK:
			if snapshot: 
				if not GLIUtility.is_uri(snapshot, checklocal=local_install):
					d.msgbox("The specified URI is invalid.  It was not saved.  Please go back and try again.");
				else install_profile.set_portage_tree_snapshot_uri(None, snapshot, None)
			
			else: d.msgbox("No URI was specified!")
		#if d.yesno("The specified URI is invalid. Use it anyway?") == DLG_YES: install_profile.set_stage_tarball_uri(None, stage_tarball, None)

def set_make_conf():
# This section will be for setting things like CFLAGS, ACCEPT_KEYWORDS, and USE
	make_conf = install_profile.get_make_conf()
	while 1:
		menulist = ["ACCEPT_KEYWORDS", "CFLAGS", "CHOST", "MAKEOPTS", "FEATURES", "USE"]
		code, menuitem = d.menu("Choose a variable to edit", choices=dmenu_list_to_choices(menulist), cancel="Done")
		if code != DLG_OK: break
		menuitem = menulist[int(menuitem)-1]
		oldval = ""
		if make_conf.has_key(menuitem): oldval = make_conf[menuitem]
		code, newval = d.inputbox("Enter new value for " + menuitem, init=oldval)
		if code == DLG_OK:
			make_conf[menuitem] = newval
			install_profile.set_make_conf(make_conf)

def set_kernel():
# This section will be for choosing kernel sources, choosing (and specifying) a custom config or genkernel, modules to load at startup, etc.
	kernel_sources = ("vanilla-sources", "gentoo-sources", "development-sources", "gentoo-dev-sources", "hardened-sources")
	code, menuitem = d.menu("Choose a kernel sources package", choices=dmenu_list_to_choices(kernel_sources))
	if code != DLG_OK: return
	menuitem = kernel_sources[int(menuitem)-1]
	install_profile.set_kernel_source_pkg(None, menuitem, None)
	if d.yesno("Do you want to use genkernel to automatically generate your kernel?") == DLG_NO:
		code, custom_kernel_uri = d.inputbox("Enter the custom kernel uri")
		if code == DLG_OK: install_profile.set_kernel_config_uri(None, custom_kernel_uri, None)
	else: 
		if d.yesno("Do you want the bootsplash?") == DLG_YES:
			install_profile.set_kernel_bootsplash(None, True, None)
		else:
			install_profile.set_kernel_bootsplash(None, False, None)

def set_boot_loader():
	boot_loaders = ("grub", "lilo")
	code, menuitem = d.menu("Choose a boot loader", choices=dmenu_list_to_choices(boot_loaders))
	if code != DLG_OK: return
	menuitem = boot_loaders[int(menuitem)-1]
	install_profile.set_boot_loader_pkg(None, menuitem, None)
	if d.yesno("Do you want the boot loader installed in the MBR?") == DLG_YES:
		install_profile.set_boot_loader_mbr(None, True, None)
	else:
		install_profile.set_boot_loader_mbr(None, False, None)

def set_timezone():
# This section will be for setting the timezone. It pulls from /usr/share/zoneinfo/zone.tab.
	tzlist = []
	file = open("/usr/share/zoneinfo/zone.tab")
	for line in file.readlines():
		if not line.startswith('#') and len(line) > 0:
			tzlist.append("%s" % line.split("\t")[2].strip())
	tzlist.sort()
	code, tznum = d.menu("Enter a timezone", choices=dmenu_list_to_choices(tzlist), cancel="Back")
	if code == DLG_OK: install_profile.set_time_zone(None, tzlist[int(tznum)-1], None)

def set_networking():
# This section will be for setting up network interfaces, defining DNS servers, default routes/gateways, etc.
	while 1:
		menulist = ["Edit Interfaces", "DNS Servers", "Default Gateway", "Hostname", "Domain Name", "NIS Domain Name"]
		code, menuitem = d.menu("Choose an option", choices=dmenu_list_to_choices(menulist), cancel="Done")
		if code != DLG_OK: break
		menuitem = menulist[int(menuitem)-1]
		if menuitem == "Edit Interfaces":
			while 1:
				interfaces = install_profile.get_network_interfaces()
				menu_list = interfaces.keys()
				menu_list.sort()
				menu_list.append("Add new interface")
				code, menuitem = d.menu("Select an interface", choices=dmenu_list_to_choices(menu_list), cancel="Back")
				if code != DLG_OK: break
				menuitem = menu_list[int(menuitem)-1]
				newnic = None
				if menuitem == "Add new interface":
					code, newnic = d.inputbox("Enter name for new interface (eth0, ppp0, etc.)")
					if code != DLG_OK: continue
					if newnic in interfaces:
						d.msgbox("An interface with the name is already defined.")
						continue
					interfaces[newnic] = ("", "", "")
					menuitem = newnic
				menuitem2 = ""
				menulist = ["Edit", "Rename", "Delete"]
				if newnic == None:
					menuitem2 = d.menu("What do you want to do with interface " + menuitem + "?", choices=dmenu_list_to_choices(menulist), cancel="Back")
					if code != DLG_OK: continue
				else:
					menuitem2 = "1"
				menuitem2 = menulist[int(menuitem2)-1]
				if menuitem2 == "Edit":
					tmpnic = [interfaces[menuitem][0], interfaces[menuitem][1], interfaces[menuitem][2]]
					code, ip = d.inputbox("Enter an IP address for " + menuitem + " or 'dhcp' for DHCP", init=tmpnic[0])
					if code != DLG_OK: continue
					tmpnic[0] = ip
					if ip == "dhcp" or ip == "DHCP":
						tmpnic[1] = ""
						tmpnic[2] = ""
					else:
						code, netmask = d.inputbox("Enter the netmask", init=tmpnic[2])
						if code == DLG_OK: tmpnic[2] = netmask
						code, broadcast = d.inputbox("Enter a broadcast", init=tmpnic[1])
						if code == DLG_OK: tmpnic[1] = broadcast
					interfaces[menuitem] = (tmpnic[0], tmpnic[1], tmpnic[2])
				elif menuitem2 == "Rename":
					d.msgbox("Not implimented yet")
				elif menuitem2 == "Delete":
					if d.yesno("Are you sure you want to remove the interface " + menuitem + "?") == DLG_YES:
						del interfaces[menuitem]
				install_profile.set_network_interfaces(interfaces)
		elif menuitem == "DNS Servers":
			code, dnsservers = d.inputbox("Enter a space-separated list of DNS servers")
			if code == DLG_OK: install_profile.set_dns_servers(None, dnsservers, None)
			
		elif menuitem == "Default Gateway":
			while 1:
				interfaces = install_profile.get_network_interfaces()
				if not interfaces: break
				menu_list = interfaces.keys()
				menu_list.sort()
				code, menuitem = d.menu("Which interface is the default gateway?", choices=dmenu_list_to_choices(menu_list), cancel="Back")
				if code != DLG_OK: break
				menuitem = menu_list[int(menuitem)-1]
				code, ip = d.inputbox("Enter an IP address for " + menuitem , init=interfaces[menuitem][0])
				if code != DLG_OK: continue
				install_profile.set_default_gateway(None, ip,{'interface': menuitem})
				break		
		elif menuitem == "Hostname":
			code, hostname = d.inputbox("Enter the desired hostname")
			if type(hostname) != str:
				d.msgbox("Incorrect hostname!  It must be a string.  Not saved.")
			if code == DLG_OK: install_profile.set_hostname(None, hostname, None)
		elif menuitem == "Domain Name":
			code, domain = d.inputbox("Enter the desired domain name")
			if type(domain) != str:
				d.msgbox("Incorrect domain name!  It must be a string.  Not saved.")
			if code == DLG_OK: install_profile.set_domainname(None, domain, None)
		elif menuitem == "NIS Domain Name":
			code, nisdomain = d.inputbox("Enter the desired NIS domain name (if you don't know what this is, don't enter one.)")
			if type(nisdomain) != str:
				d.msgbox("Incorrect NIS domain name!  It must be a string.  Not saved.")
			if code == DLG_OK: install_profile.set_nisdomainname(None, nisdomain, None)

def set_cron_daemon():
	cron_daemons = ("vixie-cron", "fcron", "dcron", "None")
	code, menuitem = d.menu("Choose a cron daemon", choices=dmenu_list_to_choices(cron_daemons))
	if code == DLG_OK:
		menuitem = cron_daemons[int(menuitem)-1]
		if menuitem == "None": menuitem == ""
		install_profile.set_cron_daemon_pkg(None, menuitem, None)

def set_logger():
	loggers = ("syslog-ng", "metalog", "syslogkd")
	code, menuitem = d.menu("Choose a system logger", choices=dmenu_list_to_choices(loggers))
	if code == DLG_OK:
		menuitem = loggers[int(menuitem)-1]
		install_profile.set_logging_daemon_pkg(None, menuitem, None)

def set_extra_packages():
	#d.msgbox("This section is for selecting extra packages (pcmcia-cs, rp-pppoe, xorg-x11, etc.) and setting them up")
	code, install_packages = d.inputbox("Enter a space-separated list of extra packages to install on the system")
	if code == DLG_OK: install_profile.set_install_packages(None, install_packages, None)
	
def set_rc_conf():
# This section is for editing /etc/rc.conf
	rc_conf = install_profile.get_rc_conf()
	menulist = ["KEYMAP", "SET_WINDOWSKEYS", "EXTENDED_KEYMAPS", "CONSOLEFONT", "CONSOLETRANSLATION", "CLOCK", "EDITOR", "PROTOCOLS", "DISPLAYMANAGER", "XSESSION"]
	while 1:
		code, menuitem = d.menu("Choose a variable to edit", choices=dmenu_list_to_choices(menulist), cancel="Done")
		if code != DLG_OK: break
		menuitem = menulist[int(menuitem)-1]
		oldval = ""
		if rc_conf.has_key(menuitem): oldval = rc_conf[menuitem]
		code, newval = d.inputbox("Enter new value for " + menuitem, init=oldval)
		if code == DLG_OK:
			rc_conf[menuitem] = newval
			install_profile.set_rc_conf(rc_conf)

def set_root_password():
# The root password will be set here
	code, passwd1 = d.passwordbox("Enter the new root password")
	if code != DLG_OK: return
	code, passwd2 = d.passwordbox("Enter the new root password again")
	if code != DLG_OK: return
	if passwd1 != passwd2:
		d.msgbox("The passwords do not match")
		return
	install_profile.set_root_pass_hash(None, GLIUtility.hash_password(passwd1), None)

def set_additional_users():
# This section will be for adding non-root users
	users = {}
	for user in install_profile.get_users():
		users[user[0]] = (user[0], user[1], user[2], user[3], user[4], user[5], user[6])
	while 1:
		menu_list = []
		for user in users:
			menu_list.append(user)
		menu_list.sort()
		menu_list.append("Add user")
		code, menuitem = d.menu("Choose a user to edit", choices=dmenu_list_to_choices(menu_list), cancel="Done")
		if code != DLG_OK:
			if d.yesno("Do you want to save changes?") == DLG_YES:
				tmpusers = []
				for user in users:
					tmpusers.append(users[user])
				install_profile.set_users(tmpusers)
			break
		menuitem = menu_list[int(menuitem)-1]
		if menuitem == "Add user":
			code, newuser = d.inputbox("Enter the username for the new user")
			if code != DLG_OK: continue
			if newuser in users:
				d.msgbox("A user with that name already exists")
				continue
			new_user = [newuser, '', ('users'), '/bin/bash', '/home/' + newuser, '', '']
			users[newuser] = new_user
			menuitem = newuser
		while 1:
			menulist = ["Password", "Group Membership", "Shell", "Home Directory", "UID", "Comment", "Delete"]
			code, menuitem2 = d.menu("Choose an option for user " + menuitem, choices=dmenu_list_to_choices(menulist), cancel="Back")
			if code != DLG_OK: break
			menuitem2 = menulist[int(menuitem2)-1]
			if menuitem2 == "Password":
				code, passwd1 = d.passwordbox("Enter the new password")
				if code != DLG_OK: continue
				code, passwd2 = d.passwordbox("Enter the new password again")
				if code != DLG_OK: continue
				if passwd1 != passwd2:
					d.msgbox("The passwords do not match")
					continue
				users[menuitem][1] = GLIUtility.hash_password(passwd1)
			elif menuitem2 == "Group Membership":
				code, groups = d.inputbox("Enter a space-separated list of groups the user is to be in", init=",".join(users[menuitem][2]))
				if code != DLG_OK: continue
#				new_groups = []
#				groups = string.split(groups)
#				for group in groups:
#					new_groups.append(group)
				users[menuitem][2] = string.split(groups, ",")
			elif menuitem2 == "Shell":
				code, shell = d.inputbox("Enter the shell you want the user to use.  default is /bin/bash.  Get it right b/c there's no error checking!", init=users[menuitem][3])
				if code != DLG_OK: continue
				users[menuitem][3] = shell
			elif menuitem2 == "Home Directory":
				code, homedir = d.inputbox("Enter the user's home directory. default is /home/username.  Get it right b/c there's no error checking!", init=users[menuitem][4])
				if code != DLG_OK: continue
				users[menuitem][4] = homedir
			elif menuitem2 == "UID":
				code, uid = d.inputbox("Enter the user's UID. ", init=users[menuitem][5])
				if code != DLG_OK: continue
				if type(uid) != int: continue
				users[menuitem][5] = uid
			elif menuitem2 == "Comment":
				code, comment = d.inputbox("Enter the user's comment.", init=users[menuitem][6])
				if code != DLG_OK: continue
				users[menuitem][6] = comment
			elif menuitem2 == "Delete":
				if d.yesno("Are you sure you want to delete the user " + menuitem + "?") == DLG_YES:
					del users[menuitem]
					break

def set_services():
	code, services = d.inputbox("Enter a space-separated list of services to start on boot")
	if code == DLG_OK: install_profile.set_services(None, services, None)
def save_install_profile(xmlfilename="", askforfilename=True):
	code = 0
	filename = xmlfilename
	if askforfilename:
		code, filename = d.inputbox("Enter a filename for the XML file", init=xmlfilename)
		if code != DLG_OK: return None
	if GLIUtility.is_file(filename):
		if not d.yesno("The file " + filename + " already exists. Do you want to overwrite it?") == DLG_YES:
			return None
	configuration = open(filename ,"w")
	configuration.write(install_profile.serialize())
	configuration.close()
	return filename


#----------------------------Now for the client_config functions
def set_arch_template():
	template_choices = ("x86", "amd64","sparc", "alpha", "hppa", "ppc")
	code, menuitem = d.menu("Please Select Architecture Template:",choices=dmenu_list_to_choices(template_choices))
	if code == DLG_OK:
		menuitem = template_choices[int(menuitem)-1]
		client_profile.set_architecture_template(None, menuitem, None)
def set_logfile():
	code, logfile = d.inputbox("Enter the desired path for the install log:", init="/var/log/install.log")
	if code == DLG_OK: client_profile.set_log_file(None, logfile, None)
def set_root_mount_point():
	code, rootmountpoint = d.inputbox("Enter the mount point for the chroot enviornment:", init="/mnt/gentoo")
	if code == DLG_OK: client_profile.set_root_mount_point(None, rootmountpoint, None)
def set_client_networking():
	network_data = None

	code, interface = d.inputbox("Enter the interface (NIC) you would like to use for installation (e.g. eth0):")
	if code != DLG_OK: return

	network_choices = ('DHCP', 'Static IP');
	code, menuitem = d.menu("Please select networking configuration:", choices=dmenu_list_to_choices(network_choices))
	
	if code != DLG_OK:
		return

	menuitem = network_choices[int(menuitem)-1]
	if menuitem == 'Static IP':
		code, ip_address = d.inputbox("Enter your IP address:")
		if code != DLG_OK: return
		code, broadcast = d.inputbox("Enter your Broadcast address:")
		if code != DLG_OK: return
		code, netmask = d.inputbox("Enter your Netmask:")
		if code != DLG_OK: return
		code, gateway = d.inputbox("Enter your default gateway:")
		if code != DLG_OK: return
		network_data = (interface, ip_address, broadcast, netmask, gateway)
		network_type = 'static'
	else:
		network_data = (interface, None, None, None, None)
		network_type = 'dhcp'

	try:
		client_profile.set_network_type(None, network_type, network_data)
	except GLIException, e:
		d.msgbox(e)


def set_livecd_password():
# The root password will be set here
	code, passwd1 = d.passwordbox("Enter the new LIVECD root password")
	if code != DLG_OK: return
	code, passwd2 = d.passwordbox("Enter the new LIVECD root password again")
	if code != DLG_OK: return
	if passwd1 != passwd2:
		d.msgbox("The passwords do not match")
		return
	client_profile.set_root_passwd(None, GLIUtility.hash_password(passwd1), None)

def set_enable_ssh():
	if d.yesno("Do you want SSH enabled during the install?") == DLG_YES:
		client_profile.set_enable_ssh(None, True, None)
	else:
		client_profile.set_enable_ssh(None, False, None)
def set_client_kernel_modules():
	code, kernel_modules_list = d.inputbox("Enter a list of kernel modules you want loaded before installation:", init="")
	if code == DLG_OK: client_profile.set_kernel_modules(None, kernel_modules_list, None)
def save_client_profile(xmlfilename="", askforfilename=True):
	code = 0
	filename = xmlfilename
	if askforfilename:
		code, filename = d.inputbox("Enter a filename for the XML file", init=xmlfilename)
		if code != DLG_OK: return None
	if GLIUtility.is_file(filename):
		if not d.yesno("The file " + filename + " already exists. Do you want to overwrite it?") == DLG_YES:
			return None
	configuration = open(filename ,"w")
	configuration.write(client_profile.serialize())
	configuration.close()
	return filename
# ------------------------------------------------------------------
d.setBackgroundTitle("Gentoo Linux Installer")
d.msgbox("Welcome to The Gentoo Linux Installer. This is a TESTING release. If your system dies a horrible, horrible death, don't come crying to us (okay, you can cry to klieber).", height=10, width=50, title="Welcome")

if d.yesno("Are we running in Pretend mode? Yes means safe, No means actually install!") == DLG_NO:
	cc._pretend = False
else:
	cc._pretend = True
	
if d.yesno("Are the profiles being generated to be used for an install on the current computer?") == DLG_NO:
	local_install = False
	

if d.yesno("Do you want to use the ClientController? (if doing an install, say YES)") == DLG_YES:
	client_config_xml_file = None
	while 1:
		if d.yesno("Do you have a previously generated XML file for the ClientConfiguration?") == DLG_YES:
			code, client_config_xml_file = d.inputbox("Enter the filename of the XML file")
			if code != DLG_OK: break
			if GLIUtility.is_file(client_config_xml_file): break
			d.msgbox("Cannot open file " + client_config_xml_file, height=7, width=50)
			client_config_xml_file = None
			continue
		break
	if client_config_xml_file != None:
		client_profile.parse(client_config_xml_file)
	# code to actually run the client_controller functions
	else:
		set_arch_template()
		set_logfile()
		set_root_mount_point()
		set_client_networking()
		set_livecd_password()
		set_enable_ssh()
		set_client_kernel_modules()
		if d.yesno("Do you want to save the ClientConfiguration XML file?") == DLG_YES:
			if client_config_xml_file == None: client_config_xml_file = ""
			client_config_xml_file = save_client_profile(xmlfilename=client_config_xml_file)

	d.msgbox("ClientController done")

client_profile.set_interactive(None, True, None)
cc.set_configuration(client_profile)

cc.start_pre_install()

install_profile_xml_file = None
fn = (
	{ 'text': "Partitioning", 'fn': set_partitions },
	{ 'text': "Network mounts", 'fn': set_network_mounts },
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
	{ 'text': "Services", 'fn': set_services },
	{ 'text': "rc.conf", 'fn': set_rc_conf },
	{ 'text': "Root password", 'fn': set_root_password },
	{ 'text': "Additional Users", 'fn': set_additional_users },
     )
while 1:
	if d.yesno("Do you have a previously generated InstallProfile XML file?") == DLG_YES:
		code, install_profile_xml_file = d.inputbox("Enter the filename of the XML file")
		if code != DLG_OK: break
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
	code, menuitem = d.menu("Choose an option", choices=dmenu_list_to_choices(menu_list), height=25, menu_height=18, cancel="Exit")
	if code != DLG_OK:
		if d.yesno("Do you really want to exit before the install is complete?") == DLG_YES:
			if d.yesno("Do you want to save the InstallProfile XML file?") == DLG_YES:
				if install_profile_xml_file == None: install_profile_xml_file = ""
				install_profile_xml_file = save_install_profile(xmlfilename=install_profile_xml_file)
			sys.exit()
		continue
	menuitem = menu_list[int(menuitem)-1]
	for item in fn:
		if menuitem == item['text']:
			item['fn']()
			continue
	if menuitem == "Install!":
		if install_profile_xml_file == None or install_profile_xml_file == "":
			install_profile_xml_file = "tmp_install_profile.xml"
		save_install_profile(xmlfilename=install_profile_xml_file, askforfilename=False)
		cc.set_install_profile(install_profile)
		cc.start_install()
		d.gauge_start("Installation Started!", title="Installation progress")
		num_steps_completed = 1
		while 1:
			notification = cc.getNotification()
			if notification == None:
				time.sleep(1)
				continue
			type = notification.get_type()
			data = notification.get_data()
			if type == "exception":
				print "Exception received:"
				print data
			elif type == "int":
				if data == GLIClientController.NEXT_STEP_READY:
					next_step_waiting = False
					next_step = cc.get_next_step_info()
					num_steps = cc.get_num_steps()
					i = (num_steps_completed*100)/num_steps
					d.gauge_update(i, "On step %d of %d. Current step: %s" % (num_steps_completed, num_steps, next_step), update_text=1)
					num_steps_completed += 1
					#print "Next step: " + next_step
					if cc.has_more_steps():
						cc.next_step()
					continue
				if data == GLIClientController.INSTALL_DONE:
					d.gauge_update(100, "Install completed!", update_text=1)
					d.gauge_stop()
					print "Install done!"
					sys.exit(0)
