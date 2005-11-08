import GLIServerProfile
import GLIInstallProfile
import GLIClientConfiguration
import GLIStorageDevice
import GLIUtility
from GLIException import GLIException
import handler
import traceback
import sys, os
import copy
import string
import gettext
_ = gettext.gettext
sys.path.append("../..")
class WebGLIHandler(handler.Handler):

	def clientconfig(self):
		import platform
		data = ""
		data += "<h2>Client Config</h2>\n"
		data += '<form name="CConfig" action="/webgli/saveclientconfig" method="POST" enctype="multipart/form-data">\n'
		
		data += '<table border="2"><tr><td>\n'
		#Choose the architecture for the Install.
		subarches = { 'i386': 'x86', 'i486': 'x86', 'i586': 'x86', 'i686': 'x86', 'x86_64': 'amd64', 'parisc': 'hppa' }
		arch = platform.machine()
		if arch in subarches: 
			arch = subarches[arch]
			
		data += "Arch selection string here.<br>\n"
		data += '<input type="radio" '
		if arch == "x86":
			data += 'checked="checked" '
		data += 'name="ArchType" value="x86">x86 (Pentium and Athlon Series)<br>\n'
		data += '<input type="radio" '
		if arch == "amd64":
			data += 'checked="checked" '
		data += 'name="ArchType" value="amd64">AMD Athlon 64 and Opteron<br>\n'
		data += '<input type="radio" '
		if arch == "ppc":
			data += 'checked="checked" '
		data += 'name="ArchType" value="ppc">PPC (New World) Macs<br>\n'
		data += '<input type="radio" '
		if arch == "sparc":
			data += 'checked="checked" '
		data += 'name="ArchType" value="sparc">Sparc<br>\n'
		data += '<input type="radio" '
		if arch == "alpha":
			data += 'checked="checked" '
		data += 'name="ArchType" value="alpha">Alpha<br>\n'
		data += '<input type="radio" '
		if arch == "hppa":
			data += 'checked="checked" '
		data += 'name="ArchType" value="hppa">HPPA<br>\n'
		data += '</td><td width="15"></td><td>'
		#Choose the logfile location
		data += "Logfile selection string here. <br>\n"
		data += '<input name="Logfile" type="text" length="80" maxlength="80" value="/var/log/installer.log">\n'
		
		#Choose the root mountpoint location
		data += "<hr>Root mountpoint selection string here. <br>\n"
		data += '<input name="RootMountPoint" type="text" length="80" maxlength="80" value="/mnt/gentoo">'
		data += " </td></tr></table>\n"
		
		if 1:#not GLIUtility.ping("www.gentoo.org"): # and local_install:
			data += '<hr><table><tr><td>'
			data += "LiveCD Network Configuration string here. <br>"
			device_list = GLIUtility.get_eth_devices()
			data += '<select name="Network_Iface" size="4">'
			for device in device_list:
				data += '<option value="'+device+'">' 
				data += device + ": " + GLIUtility.get_interface_realname(device)
				data += '</option>\n'
			data += '</select>'
			
			data += '<select name="Network_Type" size="3">'
			data += '<option value="dhcp">DHCP</option>'
			data += '<option value="static">Manual Config</option>'
			data += '<option value="None">None (Networkless)</option>'
			data += '</select>'
			data += '</td><td>'
			data += 'Networking Info for Manual Configurations:<br>'
			data += 'Enter your IP address: <input name="ip" type="text" length="50" maxlength="15" value="192.168."><br>'
			data += 'Enter your Broadcast address: <input name="broadcast" type="text" length="50" maxlength="15" value=".255"><br>'
			data += 'Enter your Netmask: <input name="netmask" type="text" length="50" maxlength="15" value="255.255.255.0"><br>'
			data += 'Enter your default gateway: <input name="gateway" type="text" length="50" maxlength="15" value=".1"><br>'
			data += 'Enter a DNS server: <input name="dnsserver" type="text" length="50" maxlength="15" value="128.118.25.3"></td></tr></table>'
		
		#Enable SSH?
		data += "<hr>Enable SSH  string here. <br>"
		data += 'Enable SSH?: <input name="EnableSSH" type="radio" value="True">Yes'
		data += '<input name="EnableSSH" type="radio" value="False" checked="checked">No'
		
		#Set root password	THIS MAY NOT BE NECESSARY - SEE REMOTE SCRIPT
		data += "<hr>Root password selection string here. <br>"
		data += 'Enter Password:<input name="RootPass1" type="password" length="80" maxlength="80" value=""><br>'
		data += 'Re-enter Password to verify:<input name="RootPass2" type="password" length="80" maxlength="80" value=""><br>'
		
		#Modules to load now.
		#status, output = GLIUtility.spawn("lsmod", return_output=True)
		data += "<hr>Loaded modules list here. <br>"
		data += 'Additional Modules to Load (space-separated list): <input name="Modules" type="text" length="80" maxlength="80" value=""><br>'
		
		#Save Client Configuration File.	THIS SHOULD BE A POPUP
		data += "<hr><br>Save Client Configuration File string here. <br>";
		data += 'Filename: <input name="SaveCCFile" type="text" value="clientconfig.xml">';
		data += '<input name="SaveCC" type="submit" value="Save Client Configuration">'; #Javascript for on_click
		
		#Print buttons for Next/Previous/Help/Save
		data += "<hr><table><tr>"
		data += '<td><input name="LoadCC" type="button" value="Load"></td>'
		data += '<td><input name="SaveCC" type="button" value="Save"></td>'
		data += '<td><input name="Help" type="button" value="Help"></td>'
		data += '<td><input name="Previous" type="button" value="Previous"></td>'
		data += '<td><input name="Next" type="button" value="Next"></td></tr></table>'
		data += '</form>'
		return self.wrap_in_webgli_template(data)
		
	def saveclientconfig(self):
		data = ""
				
		if 'ArchType' in self.post_params:
			data += "Found an architecture:  you submitted " + self.post_params['ArchType']+ "<BR>\n"
			try:
				self.shared_info.client_profile.set_architecture_template(None, self.post_params['ArchType'], None)
			except:
				data += "ERROR: Could not set the Architecture Template<br>\n"
		if 'Logfile' in self.post_params:
			data += "Found a logfile: you submitted " + self.post_params['Logfile'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_log_file(None, self.post_params['Logfile'], None)
			except:
				data += "ERROR: Could not set the Logfile <BR>\n"
		if 'RootMountPoint' in self.post_params:
			data += "Found a root mount point: you submitted " + self.post_params['RootMountPoint'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_root_mount_point(None, self.post_params['RootMountPoint'], None)
			except:
				data += "ERROR: Could not set the Root Mount Point<BR>\n"
		if 'Network_Iface' in self.post_params:
			data += "Found a network interface: you submitted " + self.post_params['Network_Iface'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_network_interface(None, self.post_params['Network_Iface'], None)
			except:
				data += "ERROR: Could not set the Network Interface<BR>\n"
		if 'Network_Type' in self.post_params:
			data += "Found a Network Type: you submitted " + self.post_params['Network_Type'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_network_type(None, self.post_params['Network_Type'], None)
			except:
				data += "ERROR: Could not set the Network Type<BR>\n"
		if 'ip' in self.post_params:
			data += "Found an IP: you submitted " + self.post_params['ip'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_network_ip(None, self.post_params['ip'], None)
			except:
				data += "ERROR: Could not set the IP<BR>\n"
		if 'broadcast' in self.post_params:
			data += "Found an broadcast IP: you submitted " + self.post_params['broadcast'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_network_broadcast(None, self.post_params['broadcast'], None)
			except:
				data += "ERROR: Could not set the broadcast IP<BR>\n"
		if 'netmask' in self.post_params:
			data += "Found an netmask IP: you submitted " + self.post_params['netmask'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_network_netmask(None, self.post_params['netmask'], None)
			except:
				data += "ERROR: Could not set the netmask IP<BR>\n"
		if 'gateway' in self.post_params:
			data += "Found an gateway IP: you submitted " + self.post_params['gateway'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_network_gateway(None, self.post_params['gateway'], None)
			except:
				data += "ERROR: Could not set the gateway IP<BR>\n"
		if 'dnsserver' in self.post_params:
			data += "Found an DNS server: you submitted " + self.post_params['dnsserver'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_dns_servers(None, self.post_params['dnsserver'], None)
			except:
				data += "ERROR: Could not set the DNS Server<BR>\n"
		if 'EnableSSH' in self.post_params:
			data += "Found an Enable SSH Flag: you set it to " + self.post_params['EnableSSH'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_enable_ssh(None, self.post_params['EnableSSH'], None)
			except:
				data += "ERROR: Could not set the SSH flag<BR>\n"
		if ('RootPass1' in self.post_params) and ('RootPass2' in self.post_params):
			data += "Found a root password1: you submitted " + self.post_params['RootPass1'] + "<BR>\n"
			data += "Found a root password2: you submitted " + self.post_params['RootPass2'] + "<BR>\n"
			if self.post_params['RootPass1'] == self.post_params['RootPass2']:
				try:
					self.shared_info.client_profile.set_root_passwd(None, GLIUtility.hash_password(self.post_params['RootPass1']), None)
				except:
					data += "ERROR: Could not set the root password<BR>\n"
			else:
				data += "ERROR: Passwords DO NOT MATCH!<BR>\n"
		if 'Modules' in self.post_params:
			data += "Found an Additional Module: you submitted " + self.post_params['Modules'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_kernel_modules(None, self.post_params['Modules'], None)
			except:
				data += "ERROR: Could not set the Kernel Modules<BR>\n"
		if 'SaveCCFile' in self.post_params:
			data += "Found a filename to save the Client Profile:" + self.post_params['SaveCCFile'] + "<BR>\n"
			try:
				configuration = open(self.post_params['SaveCCFile'] ,"w")
				configuration.write(self.shared_info.client_profile.serialize())
				configuration.close()
				data += "Profile saved successfully.	Here it is <BR><pre>" + self.shared_info.client_profile.serialize() + "</pre><br>\n"
			except:
				data += "ERROR: Could not save the profile!<BR>\n"
		return self.wrap_in_webgli_template(data)
		
	def loadprofile(self):
		content = """
		<h2>Load Client Profile</h2>
		<br>
		<form action="/webgli/loadprofile2" method="POST" enctype="multipart/form-data">
		Use local (to server) file: <input type="text" name="clientfile"><br>
		or<br>
		Upload file: <input type="file" name="uploadclientfile"><br>
		<input type="submit" value="Load">
		</form><hr>
		<h2>Load Install Profile</h2>
		<br>
		<form action="/webgli/loadprofile2" method="POST" enctype="multipart/form-data">
		Use local (to server) file: <input type="text" name="installfile"><br>
		or<br>
		Upload file: <input type="file" name="uploadipfile"><br>
		<input type="submit" value="Load">
		</form>
		"""
		return self.wrap_in_webgli_template(content)
	def loadprofile2(self):
		content = "<h2>Load Profile</h2>"
		xmlfile = ""
		if self.post_params['clientfile']:
			xmlfile = self.post_params['clientfile']
		elif self.post_params['uploadclientfile']:
			try:
				tmpfile = open("/tmp/clientprofile.xml", "w")
				tmpfile.write(self.post_params['uploadclientfile'])
				tmpfile.close()
				xmlfile = "/tmp/clientprofile.xml"
			except:
				content += "There was a problem writing the temp file for the file you uploaded" + self.get_exception()
				return self.wrap_in_webgli_template(content)
		if self.post_params['clientfile'] or self.post_params['uploadclientfile']:
			try:
				self.shared_info.client_profile = GLIClientConfiguration.ClientConfiguration()
				self.shared_info.client_profile.parse(xmlfile)
				content += "Profile loaded successfully"
			except:
				content += "There was an error parsing the XML file" + self.get_exception()
				
		#INSTALL PROFILE LOADING
		if self.post_params['installfile']:
			xmlfile = self.post_params['installfile']
		elif self.post_params['uploadipfile']:
			try:
				tmpfile = open("/tmp/installprofile.xml", "w")
				tmpfile.write(self.post_params['uploadipfile'])
				tmpfile.close()
				xmlfile = "/tmp/installprofile.xml"
			except:
				content += "There was a problem writing the temp file for the file you uploaded" + self.get_exception()
				return self.wrap_in_webgli_template(content)
		if self.post_params['installfile'] or self.post_params['uploadipfile']:
			try:
				self.shared_info.install_profile = GLIInstallProfile.InstallProfile()
				self.shared_info.install_profile.parse(xmlfile)
				content += "Profile loaded successfully"
			except:
				content += "There was an error parsing the XML file" + self.get_exception()
		
		return self.wrap_in_webgli_template(content)

	def saveprofile(self):
		content = """
		<h2>Save Client Profile</h2>
		<br>
		<form action="/webgli/saveprofile2" method="POST" enctype="multipart/form-data">
		Save to local (to server) file: <input type="text" name="clientfile"> <input type="submit" value="Save"><br>
		or<br>
		Download the file: <input type="submit" name="downloadclient" value="Download">
		</form><hr>
		<h2>Save Install Profile</h2>
		<br>
		<form action="/webgli/saveprofile2" method="POST" enctype="multipart/form-data">
		Save to local (to server) file: <input type="text" name="ipfile"> <input type="submit" value="Save"><br>
		or<br>
		Download the file: <input type="submit" name="downloadip" value="Download">
		</form>
		"""
		return self.wrap_in_webgli_template(content)

	def saveprofile2(self):
		content = "<h2>Save Profile</h2>"
		if not 'downloadclient' in self.post_params and self.post_params['clientfile']:
			try:
				tmpfile = open(self.post_params['clientfile'], "w")
				tmpfile.write(self.shared_info.client_profile.serialize())
				tmpfile.close()
			except:
				content += "There was a problem writing the file" + self.get_exception()
				return self.wrap_in_webgli_template(content)
			return self.wrap_in_webgli_template(content + "Client Profile saved successfully")
		elif 'downloadclient' in self.post_params:
			self.headers_out.append(("Content-type", "text/xml"))
			self.headers_out.append(('Content-disposition', "attatchment;filename=clientprofile.xml"))
			return self.shared_info.client_profile.serialize()
		if not 'downloadip' in self.post_params and self.post_params['ipfile']:
			try:
				tmpfile = open(self.post_params['ipfile'], "w")
				tmpfile.write(self.shared_info.install_profile.serialize())
				tmpfile.close()
			except:
				content += "There was a problem writing the file" + self.get_exception()
				return self.wrap_in_webgli_template(content)
			return self.wrap_in_webgli_template(content + "Client Profile saved successfully")
		elif 'downloadip' in self.post_params:
			self.headers_out.append(("Content-type", "text/xml"))
			self.headers_out.append(('Content-disposition', "attatchment;filename=installprofile.xml"))
			return self.shared_info.install_profile.serialize()
	def showwelcome(self):
		data = "Welcoming string here.<BR>LOCAL INSTALL ASSUMED FOR THIS FRONT END<br>\n"
		return self.wrap_in_webgli_template(data)
	def partitioning(self):
		if 'add_device' in self.post_params:
			self.shared_info.devices[self.post_params['add_device']] = GLIStorageDevice.Device(self.post_params['add_device'], set_geometry=False, local_device=False)
		data = '<form name="part" action="/webgli/Partitioning2" method="POST" enctype="multipart/form-data">'
		partitions_string1 = """The first thing on the new system to setup is the partitoning.
You will first select a drive and then edit its partitions.
No changes will be saved until the end of the step.
No changes to your disk will be made until the installation.
NOTE: YOU MUST AT LEAST SELECT ONE PARTITION AS YOUR ROOT PARTITION "/"
If your drive is pre-partitioned, just select the mountpoints and make 
sure that the format option is set to FALSE or it will erase your data.
The installer does not yet support resizing of partitions (its not safe).
Please refer to the Gentoo Installation Handbook for more information
on partitioning and the various filesystem types available in Linux.<br><br>
Which drive would you like to partition?<br>"""
		data += partitions_string1
		self.shared_info.devices = self.shared_info.install_profile.get_partition_tables()
		drives = self.shared_info.devices.keys()
		drives.sort()
		choice_list = []
		if not self.shared_info.devices:
			tmp_drives = GLIStorageDevice.detect_devices()
			tmp_drives.sort()
			for drive in tmp_drives:
				self.shared_info.devices[drive] = GLIStorageDevice.Device(drive)
				#if self.local_install:  #when uncommenting please indent the next line.
				self.shared_info.devices[drive].set_partitions_from_disk()
				drives.append(drive)
				choice_list.append((drive, self.shared_info.devices[drive].get_model()))
		else:
			for drive in drives:
				choice_list.append((drive, self.shared_info.devices[drive].get_model()))
		data += "<table>\n"
		data += "<tr><td>EDIT</td><td>Drive</td><td>Drive Information</td></tr>\n"
		for i,choice in enumerate(choice_list):
			data += '<tr><td><input type="radio" name="editdrive" value="'+choice_list[i][0]+'"></td><td>'+choice_list[i][0]+'</td><td>'+choice_list[i][1]+"</td></tr>\n"
		data += '</table><input type="submit" name="SubmitEditDrive" value="Edit Drive"></form>'
		data += """
		<form name="genericdisk" action="/webgli/Partitioning" method="POST">
		Add generic disk: <input type="text" name="add_device" size="14"> <input type="submit" value="Add">
		</form>"""
		return self.wrap_in_webgli_template(data)

	def partitioning2(self):
		if self.get_params['editdrive']:
			self.post_params['editdrive'] = self.get_params['editdrive']
		colors = { 'ext2': '#0af2fe', 'ext3': '#0af2fe', 'unalloc': '#a2a2a2', 'unknown': '#ed03e0', 'free': '#ffffff', 'ntfs': '#f20600', 'fat16': '#3d07f9', 'fat32': '#3d07f9', 'reiserfs': '#f0ff00', 'linux-swap': '#12ff09', 'xfs': '#006600', 'jfs': '#ffb400' }
		data = "<h4>Select a partition or unallocated space to edit</h4>\n"
		#MOVE THIS TO PART2
		#if int(new_mb) > free_mb:
		#	self._d.msgbox(_(u"The size you entered (%s MB) is larger than the maximum of %s MB") % (new_mb, str(free_mb)))
		#	continue
		# now add it to the data structure
			#self.shared_info.devices[drive_to_partition].add_partition(part_to_edit, int(new_mb), 0, 0, type)

		if not self.post_params['editdrive']:
			data = "ERROR: You must select a drive to be editing!<br>\n"
			return self.wrap_in_webgli_template(data)
		
		drive_to_partition = self.post_params['editdrive']
		self.shared_info.drive_to_partition = drive_to_partition
		partitions = self.shared_info.devices[drive_to_partition].get_partitions()
		partlist = self.shared_info.devices[drive_to_partition].get_ordered_partition_list()
		tmpparts = self.shared_info.devices[drive_to_partition].get_partitions()

		data += '<form name="part2" action="/webgli/Partitioning3" method="POST" enctype="multipart/form-data">'
		data += '<input type="hidden" name="editdrive" value="'+drive_to_partition+"\">\n"
		data += '<input type="hidden" name="editpart2" value="">' + "\n"
		data += "<script>\nfunction partition_selected(minor) {\n  document.part2.editpart2.value = minor;\n  document.part2.submit();\n}\n</script>\n"

		if self.shared_info.error_message:
			data += '<span style="color: red;">' + self.shared_info.error_message + '</span><br><br>'
			self.shared_info.error_message = ""

		total_mb = self.shared_info.devices[drive_to_partition].get_total_mb()
		extended_total_mb = 0
		last_percent = 0
		last_log_percent = 0
		if len(partlist):
			data += '<table width="100%" cellspacing="0" cellpadding="0" border="1">' + "\n  <tr>\n"
		for part in partlist:
			tmppart = tmpparts[part]
			if tmppart.get_type() == "free":
				partsize = tmppart.get_mb()
				percent = (float(partsize) / float(total_mb)) * 100
				if percent < 1: percent = 1
				percent = int(percent)
				if tmppart.is_logical():
					ext_percent = (float(partsize) / float(extended_total_mb)) * 100
					if ext_percent < 1: ext_percent = 1
					ext_percent = int(ext_percent)
					data += '    <td height="40" width="' + str(ext_percent) + '%" align="center" style="background-color: ' + colors['unalloc'] + ';" onclick="partition_selected(' + str(part) + ');">' + "&nbsp;</td>\n"
					last_log_percent = last_log_percent + percent
				else:
					data += '    <td height="40" width="' + str(percent) + '%" align="center" style="background-color: ' + colors['unalloc'] + ';" onclick="partition_selected(' + str(part) + ');">' + "&nbsp;</td>\n"
					last_percent = last_percent + percent
			else:
				partsize = tmppart.get_mb()
				percent = (float(partsize) / float(total_mb)) * 100
				if percent < 1: percent = 1
				percent = int(percent)
				tmpminor = int(tmppart.get_minor())
				tmpdevice = drive_to_partition
				if tmppart.is_extended():
					data += '    <td height="40" width="' + str(percent) + '%" align="center" style="background-color: #ffffff;">' + "\n" + '      <table width="100%" cellspacing="0" cellpadding="0" border="1" style="margin: 2px;">' + "\n        <tr>\n"
					extended_total_mb = tmppart.get_mb()
					last_percent = last_percent + percent
				elif tmppart.is_logical():
					ext_percent = (float(partsize) / float(extended_total_mb)) * 100
					if ext_percent < 1: ext_percent = 1
					ext_percent = int(ext_percent)
					data += '    <td height="40" width="' + str(ext_percent) + '%" align="center" style="background-color: ' + colors[tmppart.get_type()] + ';" onclick="partition_selected(' + str(tmpminor) + ');">'
					if percent >= 15:
						data += tmpdevice + str(tmpminor)
					data += "</td>\n"
					last_log_percent = last_log_percent + percent
				else:
					if extended_total_mb:
						data += "        </tr>\n      </table>\n    </td>\n"
						extended_total_mb = 0
					data += '    <td height="40" width="' + str(percent) + '%" align="center" style="background-color: ' + colors[tmppart.get_type()] + ';" onclick="partition_selected(' + str(tmpminor) + ');">'
					if percent >= 15:
						data += tmpdevice + str(tmpminor)
					data += "</td>\n"
					last_percent = last_percent + percent
		if extended_total_mb:
			data += "        </tr>\n      </table>\n    </td>\n"
			extended_total_mb = 0
		if len(partlist):
			data += "  </tr>\n</table>\n<br>\n"
		if self.shared_info.devices[drive_to_partition].get_model() == "Generic disk":
			data += '<input type="button" value="Add new at end" onclick="partition_selected(-1);"> &nbsp; '
		else:
			data += '<input type="submit" name="recommended" value="Recommended layout"> &nbsp; '
		data += '<input type="submit" name="cleardrive" value="Clear drive"><br>'

		data += "<table style=\"display: none;\"><tr><td>EDIT</td><td>INFO: Key: Minor, Pri/Ext, Filesystem, MkfsOpts, Mountpoint, MountOpts, Size.</td></tr>"
		
		for i, part in enumerate(partlist):
			tmppart = tmpparts[part]
			minor = tmppart.get_minor()
			if not tmppart.get_type() == "free":
				minor = int(minor)
			data += '<tr><td><input type="radio" name="editpart" value="' + str(minor) + '"></td>'
			if tmppart.get_type() == "free":
				#partschoice = "New"
				entry = _(u" - Unallocated space (")
				if tmppart.is_logical():
					entry += _(u"logical, ")
				entry += str(tmppart.get_mb()) + "MB)"
			elif tmppart.get_type() == "extended":
				entry = str(int(tmppart.get_minor()))
				entry += _(u" - Extended Partition (") + str(tmppart.get_mb()) + "MB)"
			else:
				entry = str(int(tmppart.get_minor())) + " - "
				# Type: " + tmppart.get_type() + ", Mountpoint: " + tmppart.get_mountpoint() + ", Mountopts: " + tmppart.get_mountopts() + "("
				if tmppart.is_logical():
					entry += _(u"Logical (")
				else:
					entry += _(u"Primary (")
				entry += tmppart.get_type() + ", "
				entry += (tmppart.get_mkfsopts() or "none") + ", "
				entry += (tmppart.get_mountpoint() or "none") + ", "
				entry += (tmppart.get_mountopts() or "none") + ", "
				entry += str(tmppart.get_mb()) + "MB)"
			data += '<td>'+entry + "</td></tr>\n"
		if self.shared_info.devices[drive_to_partition].get_model() == "Generic disk":
			data += '<tr><td><input type="radio" name="editpart" value="-1"></td><td>Add new at end</td></tr>'
		data += '<tr><td colspan="2"><br><input type="submit" name="SubmitEditPart" value="Edit Partition"></td></tr>'
		data += "</table>\n</form>\n"
		return self.wrap_in_webgli_template(data)

	def partitioning3(self):
		if 'recommended' in self.post_params:
			try:
				self.shared_info.devices[self.shared_info.drive_to_partition].do_recommended()
			except GLIException, error:
				self.shared_info.error_message = error.get_error_msg()
			return self.return_redirect("/webgli/Partitioning2?editdrive=" + self.shared_info.drive_to_partition)
		if 'cleardrive' in self.post_params:
			self.shared_info.devices[self.shared_info.drive_to_partition].clear_partitions()
			self.shared_info.error_message = "Partition table cleared successfully"
			return self.return_redirect("/webgli/Partitioning2?editdrive=" + self.shared_info.drive_to_partition)
		if self.post_params['editpart2']:
			self.post_params['editpart'] = self.post_params['editpart2']
		if self.get_params['editpart']:
			self.post_params['editpart'] = self.get_params['editpart']
		data = ""
		data += '<form name="part3" action="/webgli/Partitioning4" method="POST" enctype="multipart/form-data">'
		data += '<input type="hidden" name="editpart" value="' + self.post_params['editpart'] + '">'
		drive_to_partition = self.shared_info.drive_to_partition
		partlist = self.shared_info.devices[drive_to_partition].get_ordered_partition_list()
		tmpparts = self.shared_info.devices[drive_to_partition].get_partitions()
		if not self.post_params['editpart']:
			data = "ERROR: You must select a partition to edit!<br>\n"
			return self.wrap_in_webgli_template(data)
		editpart = float(self.post_params['editpart'])
#		part_to_edit = partlist[editpart]
#		tmppart = tmpparts[part_to_edit]
		part_types = [("ext2", _(u"Old, stable, but no journaling")),
			("ext3", _(u"ext2 with journaling and b-tree indexing (RECOMMENDED)")),
			("linux-swap", _(u"Swap partition for memory overhead")),
			("fat32", _(u"Windows filesystem format used in Win9X and XP")),
			("ntfs", _(u"Windows filesystem format used in Win2K and NT")),
			("jfs", _(u"IBM's journaling filesystem.  stability unknown.")),
			("xfs", _(u"Don't use this unless you know you need it.")),
			("reiserfs", _(u"B*-tree based filesystem. great performance. Only V3 supported.")),
			("extended", _(u"Create an extended partition containing other logical partitions"))]
		mountpoints = ["","/","/boot","/etc","/home","/lib","/mnt","/mnt/windows","/opt","/root","/usr","/usr/local","/usr/portage","/var"]
		if not editpart == -1:
			tmppart = tmpparts[float(editpart)]
		if editpart == -1 or tmppart.get_type() == "free":
			# partition size first
			if editpart == -1:
				free_mb = 0
			else:
				free_mb = tmppart.get_mb()
			data += 'Enter the size of the new partition in MB (max '+str(free_mb)+' MB).  If creating an extended partition input its entire size (not just the first logical size): <input type="text" name="size" value="'+str(free_mb)+"\"><br>\n"
			#code, new_mb = self._d.inputbox(_(u"Enter the size of the new partition in MB (max %s MB).  If creating an extended partition input its entire size (not just the first logical size):") % str(free_mb), init=str(free_mb))
			#if code != self._DLG_OK: continue

			# partition type
			data += "Choose the filesystem type for this new partition:<br>\n"
			data += "<table><tr><td>Filesystem</td><td>Description</td></tr>\n"
			for part_type in part_types:
				data += '<tr><td><input type="radio" name="filesystem" value="' + part_type[0] + '"> ' + part_type[0] + '</td><td>' + part_type[1] + "</td></tr>\n"
			data += "</table><br>\n" 
			data += '<input type="submit" value="Create"> &nbsp; <input type="button" value="Cancel" onclick="location.go(-1)">'
			#code, type = self._d.menu(_(u"Choose the filesystem type for this new partition."), height=20, width=77, choices=part_types)
		else:
#			tmppart = tmpparts[part_to_edit]
			editpart = int(editpart)
			data += "<h2>Partition Information:</h2>\n"
			data += "<b>Minor:</b> "+drive_to_partition + str(editpart) + "<br> -\n "
			if tmppart.is_logical():
				data += _(u"Logical Partition<br> - ")
			else:
				data += _(u"Primary Partition<br> - ")
			data += "<b>Filesystem type:</b><select name=\"filesystem\" size=\"1\">\n "
			for i,part_type in enumerate(part_types):
				data += '<option value="'+part_types[i][0]+'" '
				if part_types[i][0] == tmppart.get_type():
					data += "selected"
				data += '>'+part_types[i][0]+" - "+ part_types[i][1]+"</option>\n"
			data += "</select><br> - \n"
			data += "<b>Options:</b> <input type=\"text\" name=\"fsopts\" value=\""+ (tmppart.get_mkfsopts() or "") + "\"><br> - \n"
			data += "<b>MountPoint:</b> <select name=\"mountpoint\" size=\"1\">\n "
			for mtpnt in mountpoints:
				data += '<option value="'+mtpnt+'" '
				if mtpnt == tmppart.get_mountpoint():
					data += "selected"
				data += '>'+mtpnt+"</option>\n"
			data += "</select><br> - \n"
			data += "<b>Mount Options:</b> <input type=\"text\" name=\"mountopts\" value=\""+ (tmppart.get_mountopts() or "") + "\"><br> - \n"
			data += "<b>Size (MB)</b> "+ str(tmppart.get_mb()) + "MB <br>"
			data += 'Format this partition? <br><input type="radio" name="format" value="True" '
			if tmppart.get_format():
				data += "checked"
			data += '>True<br><input type="radio" name="format" value="False" '
			if not tmppart.get_format():
				data += "checked"
			data += ">False<br>\n"
			data += '<hr><table border="0"><tr><td><input type="submit" name="DelPartition" value="DELETE PARTITION"></td><td><input type="submit" name="SavePartition" value="Save Changes"></td><td><input type="submit" name="Cancel" value="Cancel"></td></tr></table></form>'
			#menulist = [_(u"Delete"), _(u"Mount Point"), _(u"Mount Options"), _(u"Format"), _(u"Extra mkfs.* Parameters")]
			#	code, part_action = self._d.menu(tmptitle, choices=self._dmenu_list_to_choices(menulist), cancel=_(u"Back"))
			dumbstring = """
				part_action = menulist[int(part_action)-1]
				if part_action == _(u"Delete"):
					answer = (self._d.yesno(_(u"Are you sure you want to delete the partition ") + drive_to_partition + str(editpart) + "?") == self._DLG_YES)
					if answer == True:
						tmpdev = tmppart.get_device()
						tmpdev.remove_partition(editpart)
						break
				elif part_action == _(u"Mount Point"):
					mountpoint_menu = ["/","/boot","/etc","/home","/lib","/mnt","/mnt/windows","/opt","/root","/usr","/usr/local","/usr/portage","/var",_(u"Other")]
					code, mountpt = self._d.menu(_(u"Choose a mountpoint from the list or choose Other to type your own for partition ")+str(editpart)+_(u".  It is currently set to:")+tmppart.get_mountpoint(), choices=self._dmenu_list_to_choices(mountpoint_menu)) #may have to make that an integer
					if code == self._DLG_OK:
						mountpt = mountpoint_menu[int(mountpt)-1]
						if mountpt == _(u"Other"):
							code, mountpt = self._d.inputbox(_(u"Enter a mountpoint for partition ") + str(editpart), init=tmppart.get_mountpoint())
					try: tmppart.set_mountpoint(mountpt)
					except: self._d.msgbox(_(u"ERROR! Could not set mountpoint!"))
				elif part_action == _(u"Mount Options"):
					code, answer = self._d.inputbox(_(u"Enter your mount options for partition ") + str(editpart), init=(tmppart.get_mountopts() or "defaults"))
					if code == self._DLG_OK: tmppart.set_mountopts(answer)
				elif part_action == _(u"Format"):
					#Change the Yes/No buttons back.
					self._d.add_persistent_args(["--yes-label", _(u"Yes")])
					self._d.add_persistent_args(["--no-label", _(u"No")])
					code = self._d.yesno(_(u"Do you want to format this partition?"))
					if code == self._DLG_YES: 
						tmppart.set_format(True)
					else:
						tmppart.set_format(False)
				elif part_action == _(u"Extra mkfs.* Parameters"):
					new_mkfsopts = tmppart.get_mkfsopts()
					# extra mkfs options
					if tmppart.get_type() != "extended":
						code, new_mkfsopts = self._d.inputbox(_(u"Extra mkfs.* Parameters"), init=new_mkfsopts)
						if code == self._DLG_OK: tmppart.set_mkfsopts(new_mkfsopts)"""
		return self.wrap_in_webgli_template(data)

	def partitioning4(self):
		data = ""
		drive_to_partition = self.shared_info.drive_to_partition
		partlist = self.shared_info.devices[drive_to_partition].get_ordered_partition_list()
		tmpparts = self.shared_info.devices[drive_to_partition].get_partitions()
		if not self.post_params['editpart']:
			data = "ERROR: You must select a partition to edit!<br>\n"
			return self.wrap_in_webgli_template(data)
		editpart = float(self.post_params['editpart'])
		if not editpart == -1:
			tmppart = tmpparts[float(editpart)]
		if self.post_params["DelPartition"] == "DELETE PARTITION" or self.post_params["Cancel"] == "Cancel":
			if self.post_params["DelPartition"] == "DELETE PARTITION":
				self.shared_info.devices[drive_to_partition].remove_partition(editpart)
			return self.return_redirect("/webgli/Partitioning2?editdrive=" + drive_to_partition)
#			data = '<form name="redirect" action="/webgli/Partitioning2" method="POST"><input type="hidden" name="editdrive" value="' + drive_to_partition + '"></form><script>document.redirect.submit();</script>'
		elif editpart == -1 or tmppart.get_type() == "free":
			if not int(self.post_params['size']):
				data = "ERROR: you must specify a size in MB"
				return self.wrap_in_webgli_template(data)
			new_minor = self.shared_info.devices[drive_to_partition].add_partition(editpart, int(self.post_params['size']), 0, 0, self.post_params['filesystem'])
			return self.return_redirect("/webgli/Partitioning3?editpart=" + str(int(new_minor)))
#			data = '<form name="redirect" action="/webgli/Partitioning3" method="POST"><input type="hidden" name="editpart" value="' + str(int(new_minor)) + '"></form><script>document.redirect.submit();</script>'
		else:
			tmppart = tmpparts[editpart]
			tmppart.set_format(self.post_params['format'])
			tmppart.set_mkfsopts(self.post_params['fsopts'])
			tmppart.set_mountopts(self.post_params['mountopts'])
			tmppart.set_mountpoint(self.post_params['mountpoint'])
			return self.return_redirect("/webgli/Partitioning2?editdrive=" + drive_to_partition)
#			data = '<form name="redirect" action="/webgli/Partitioning2" method="POST"><input type="hidden" name="editdrive" value="' + drive_to_partition + '"></form><script>document.redirect.submit();</script>'

		if not data:
			data = "Work in progress<pre>" + str(self.post_params) + "</pre>"
		return self.wrap_in_webgli_template(data)

	def networkmounts(self):
		data = "Network Mounts page."
		network_mounts = copy.deepcopy(self.shared_info.install_profile.get_network_mounts())
		
		#	data += "Network Mount found: " + netmount['host'] + ":" + netmount['export'] + "<br>\n"
		data += "If you have any network shares you would like to mount during the install and for your new system, define them here. Select a network mount to edit or add a new mount.	Currently GLI only supports NFS mounts."
		data += """
		<form name="netmount" action="/webgli/savenetmounts" method="POST" enctype="multipart/form-data">
		<p>If you have any network shares you would like to mount during the install and for your new system, define them here. Select a network mount to edit or add a new mount. Currently GLI only supports NFS mounts.</p>
		<table width="511" border="1">
		<tr>
			<td width="31">Edit</td>
			<td width="31">Type</td>
			<td width="79">Hostname/IP</td>
			<td width="79">Export</td>
			<td width="70">Mountpoint</td>
			<td width="103">Mount Options </td>
		</tr>"""
		for i,netmount in enumerate(network_mounts):
			data += '<tr><td><input name="edit_nfs" type="radio" id="edit_nfs" value="'+str(i)+"\">Edit</td>\n"
			data += '<td>'+network_mounts[i]['type']+"</td>\n"
			data += '<td>'+network_mounts[i]['host']+"</td>\n"
			data += '<td>'+network_mounts[i]['export']+"</td>\n"
			data += '<td>'+network_mounts[i]['mountpoint']+"</td>\n"
			data += '<td>'+network_mounts[i]['mountopts']+"</td></tr>\n"
		data += """
		</table>
	
	<hr>
		<p>&nbsp;  </p>
		<table width="100%"  border="1">
		<tr>
			<td><p>Enter the IP/hostname:
				<input name="hostname" type="text" id="hostname">
				<input type="Submit" name="Search" value="Search">
			</p>
			<p>Enter the export name:
				<input name="export" type="text" id="export">
			</p>
			<p>OR</p>
			<p>Choose the export from the list of found exports:
				<select name="exports" size="1" id="exports">
				</select>
			</p></td>
			<td><p>Enter the mountpoint:
				<input name="mountpoint" type="text" id="mountpoint">
			</p>
			<p>Enter any special mount options: 
			<input name="mountopts" type="text" id="mountopts">
			</p></td>
		</tr>
		<tr>
			<td>&nbsp;</td>
			<td><input name="addnfs" type="submit" id="addnfs" value="Add New NFS Mount"></td>
		</tr>
		</table>
		<p>&nbsp;</p>
		<p>&nbsp;</p>
		<p>&nbsp;  </p>
	</form>
		"""
		
		return self.wrap_in_webgli_template(data)
		
	def savenetmounts(self):
		data = ""
		network_mounts = copy.deepcopy(self.shared_info.install_profile.get_network_mounts())
		if 'addnfs' in self.post_params:
			if not 'hostname' in self.post_params or not self.post_params['hostname']:
				data += "ERROR: Hostname not found.<br>\n"
			elif not 'export' in self.post_params or not self.post_params['export']:
				data += "ERROR: Export not found.<br>\n"
			elif not 'mountpoint' in self.post_params or not self.post_params['mountpoint']:
				data += "ERROR: Mountpoint not found.<br>\n"
			else:	
				network_mounts.append({'export': self.post_params['export'], 'host': self.post_params['hostname'], 'mountopts': self.post_params['mountopts'], 'mountpoint': self.post_params['mountpoint'], 'type': 'nfs'})
				try:
					self.shared_info.install_profile.set_network_mounts(network_mounts)
					data += "Network mount added successfully.<br>\n"
				except:
					data += "ERROR: Could not add network mount.<br>\n"
		return self.wrap_in_webgli_template(data)
		
	def stageselection(self):
		data = "<h4>Stage selection:</h4>"
		stage = self.shared_info.install_profile.get_install_stage()
		if stage:
			data += "FOUND A STAGE" + str(stage)
		grp_install = self.shared_info.install_profile.get_grp_install()
		dynamic = self.shared_info.install_profile.get_dynamic_stage3()
		tarball = self.shared_info.install_profile.get_stage_tarball_uri()
		
		data += '<form name="stage" action="/webgli/savestage" method="POST" enctype="multipart/form-data">'
		data += '<p>Which stage do you want to start at?</p><table width="100%"  border="1"><tr><td><input name="stage" type="radio" value="1"'
		if stage == 1:
			data += ' checked'
		data += '>1</td><td>Stage1 is used when you want to bootstrap&amp;build from scratch.</td></tr><tr>			 <td><input name="stage" type="radio" value="2"'
		if stage == 2:
			data += ' checked'
		data += '>2</td><td>Stage2 is used for building from a bootstrapped semi-compiled state.</td></tr><tr>			<td><input name="stage" type="radio" value="3"'
		if (stage == 3) and not grp_install:
			data += ' checked'
		data += '>3</td><td>Stage3 is a basic system that has been built for you (no compiling).</td></tr><tr>			<td><input name="stage" type="radio" value="3+GRP"'
		if (stage == 3) and grp_install:
			data += ' checked'
		data += """>
			3 + GRP </td>
			<td>A Stage3 install but using binaries from the LiveCD when able.</td>
		</tr>
	</table>
	<p>  
		<input name="dynamic" type="checkbox" id="dynamic" value="true" """
		if dynamic:
			data += " checked"
		data += """>
Generate a dynamic stage3 on the fly using the files on the LiveCD? (faster for slow Internet connections, slower for fast connections and slow drives) </p>
	<p>Stage Tarball URI : 
		<input name="tarballuri" type="text" id="tarballuri" size="90" """
		if tarball:
			data += 'value="'+tarball+'"> '
		data += """
		or 
		<input type="button" value="Browse the mirrors for the URL" onClick="window.open('/webgli/URIBrowser?screen=stage&baseuri=' + document.stage.tarballuri.value, 'uribrowser', 'width=500,height=500,toolbars=no,statusbar=no,menubar=no,scrollbars=yes')">
(requires net connectivity)</p>
<p> <input type="submit" name="savestage" value="Save Stage Selection">
</form> """
		return self.wrap_in_webgli_template(data)
	def savestage(self):
		data = ""
		if 'savestage' in self.post_params:
			data += "YES I CLICKED SAVE<br>"
			if 'stage' in self.post_params:
				data += "YES THERE IS A STAGE<br>"
				if self.post_params['stage'] == "3+GRP":
					self.post_params['stage'] = "3"
					try:
						self.shared_info.install_profile.set_grp_install(None, True,None)
					except:
						data += "ERROR COULD NOT SET GRP INSTALL"
				try:
					self.shared_info.install_profile.set_install_stage(None, self.post_params['stage'], None)
					data += "Stage set<br>"
				except:
					data += "ERROR: could not set the install stage<br>\n"
			if 'tarballuri' in self.post_params and self.post_params['tarballuri']:
				try:
					self.shared_info.install_profile.set_stage_tarball_uri(None, self.post_params['tarballuri'], None)
					data += "Set the tarball uri<br>"
				except:
					data += "ERROR: Could not set the tarball URI<br>\n"
			if 'dynamic' in self.post_params:
				try:
					self.shared_info.install_profile.set_dynamic_stage3(None, True, None)
				except:
					data += "ERROR: Could not set dynamic stage 3.<br>\n"
		elif 'browseuri' in self.post_params:
			data = "REDIRECT OR POP UP THINGI"
			
			
		return self.wrap_in_webgli_template(data)
		
	def portagetree(self):
		data = "<p>Portage Tree Sync Type:</p>"
		synctype = self.shared_info.install_profile.get_portage_tree_sync_type()
		snapshoturi = self.shared_info.install_profile.get_portage_tree_snapshot_uri()
		
		data += '<form name="portage" action="/webgli/saveportage" method="POST" enctype="multipart/form-data">'
		data += """<p>Which method do you want to use to sync the portage tree for the installation? If choosing a snapshot you will need to provide the URI for the snapshot if it is not on the livecd.</p>
	<table width="100%"  border="1">
		<tr>
			<td><input name="portagetype" type="radio" value="sync" """
		if synctype == "sync":
			data += "checked"
		data += '>Sync</td><td>Normal. Use emerge sync RECOMMENDED!</td></tr><tr><td><input name="portagetype" type="radio" value="webrsync"'
		if synctype == "webrsync":
			data += "checked"
		data += '>Webrsync</td><td>HTTP daily snapshot. Use when rsync is firewalled.</td></tr><tr>			<td><input name="portagetype" type="radio" value="snapshot"'
		if synctype == "snapshot":
			data += "checked"
		data += '>Snapshot</td><td>Use a portage snapshot, either a local file or a URL</td></tr><tr>			 <td><input name="portagetype" type="radio" value="none"'
		if synctype == "none" or not synctype:
			data += "checked"
		data += """>
			None</td>
			<td>Extra cases such as if /usr/portage is an NFS mount</td>
		</tr>
	</table>
	<p>Snapshot URI (if doing shapshot): 
		<input name="snapshoturi" type="text" id="snapshoturi" size="90" """
		if snapshoturi:
			data += ' value="'+snapshoturi+'">'
		data += """or </p><input type="button" value="Browse the mirrors for the URL" onClick="window.open('/webgli/URIBrowser?screen=portage&baseuri=' + document.portage.tarballuri.value, 'uribrowser', 'width=500,height=500,toolbars=no,statusbar=no,menubar=no,scrollbars=yes')"><p><input type="submit" name="saveportage" value="Save Portage Settings"></form>"""
		return self.wrap_in_webgli_template(data)
	def saveportage(self):
		data = ""
		if 'saveportage' in self.post_params:
			if 'portagetype' in self.post_params:
				try:
					self.shared_info.install_profile.set_portage_tree_sync_type(None,self.post_params['portagetype'],None)
				except:
					data += "ERROR: Could not set the portage tree sync type<br>\n"
			if 'snapshoturi' in self.post_params and self.post_params['snapshoturi']:
				try:
					self.shared_info.install_profile.set_portage_tree_snapshot_uri(None,self.post_params['snapshoturi'],None)
				except:
					data += "ERROR: Could not set the portage snapshot URI"
		elif 'browsesnap' in self.post_params:
			data += "REDIRECT OR POP UP THINGI"		
		return self.wrap_in_webgli_template(data)

	def globaluse(self):
		data = "<h2>Configuration Files Settings</h2><p>Make.conf Settings:</p>"
		etc_files = self.shared_info.install_profile.get_etc_files()
		if etc_files.has_key("make.conf"):
			make_conf = etc_files['make.conf']
		else:
			make_conf = {}
		data += """The installer will now gather information regarding the contents of /etc/make.conf
One of the unique (and best) features of Gentoo is the ability to
define flags (called USE flags) that define what components are 
compiled into applications.  For example, you can enable the alsa
flag and programs that have alsa capability will use it.	
The result is a finely tuned OS with no unnecessary components to
slow you down.
The installer divides USE flag selection into two screens, one for
global USE flags and one for local flags specific to each program.
Please be patient while the screens load. It may take awhile.
<form action="/webgli/saveglobaluse" method="POST" enctype="multipart/form-data">
"""
#First set the USE flags, this is a biggie.
		if make_conf.has_key("USE"): 
			system_use_flags = make_conf["USE"]
		else:  #not a preloaded config.  this is the NORMAL case.
			system_use_flags = GLIUtility.spawn("portageq envvar USE", return_output=True)[1].strip().split()
		use_flags = []
		use_desc = GLIUtility.get_global_use_flags()
		#populate the choices list
		sorted_use = use_desc.keys()
		sorted_use.sort()
		#present the GLOBAL checkbox list
		data += '<h3>Global USE Flags:</h3><table width="100%"	border="1"><tr><th scope="col">Active</th><th scope="col">Flag</th><th scope="col">Description</th></tr>'+"\n"
		for flagname in sorted_use:
			data += '<tr><td><input name="flags" type="checkbox" id="flags" value="'+flagname+'" '
			if flagname in system_use_flags:
				data += "checked"
			data += "></td><td>"+flagname+"</td><td>"+use_desc[flagname]+"</td></tr>\n"
		data += "</table><br>"
		data += '<input name="saveglobaluse" type="submit" id="saveglobaluse" value="Save Global USE Settings">'
		data += "</form>\n"
		return self.wrap_in_webgli_template(data)
	def saveglobaluse(self):
		data = ""
		temp_use = "-* "
		if self.post_params['flags']:
			use_flags = self.post_params['flags'];
			for flag in use_flags:
				temp_use += flag + " "
			self.shared_info.temp_use = temp_use
		return self.wrap_in_webgli_template(data)
	def localuse(self):
		data = "<h2>Configuration Files Settings</h2><p>Make.conf Settings:</p>"
		etc_files = self.shared_info.install_profile.get_etc_files()
		if etc_files.has_key("make.conf"):
			make_conf = etc_files['make.conf']
		else:
			make_conf = {}
		data += """The installer will now gather information regarding the contents of /etc/make.conf
One of the unique (and best) features of Gentoo is the ability to
define flags (called USE flags) that define what components are 
compiled into applications.  For example, you can enable the alsa
flag and programs that have alsa capability will use it.	
The result is a finely tuned OS with no unnecessary components to
slow you down.
The installer divides USE flag selection into two screens, one for
global USE flags and one for local flags specific to each program.
Please be patient while the screens load. It may take awhile.
<form action="/webgli/savelocaluse" method="POST" enctype="multipart/form-data">
"""
#First set the USE flags, this is a biggie.

		if make_conf.has_key("USE"): 
			system_use_flags = make_conf["USE"]
		else:  #not a preloaded config.  this is the NORMAL case.
			system_use_flags = GLIUtility.spawn("portageq envvar USE", return_output=True)[1].strip().split()
		use_local_flags = []
		use_local_desc = GLIUtility.get_local_use_flags()
		#re-populate the chocies list
		sorted_use = use_local_desc.keys()
		sorted_use.sort()
		#present the LOCALcheckbox list
		data += '<h3>Local USE Flags:</h3><table width="100%"  border="1"><tr><th scope="col">Active</th><th scope="col">Flag</th><th scope="col">Description</th></tr>'+"\n"
		for flagname in sorted_use:
			data += '<tr><td><input name="flags" type="checkbox" id="flags" value="'+flagname+'" '
			if flagname in system_use_flags:
				data += "checked"
			data += "></td><td>"+flagname+"</td><td>"+use_local_desc[flagname]+"</td></tr>\n"
		data += "</table><br>"
		data += '<input name="savelocaluse" type="submit" id="savelocaluse" value="Save Local USE Settings">'
		data += "</form>\n"
		return self.wrap_in_webgli_template(data)
	def savelocaluse(self):
		data = ""
		temp_use = " "
		if self.post_params['flags']:
			use_local_flags = self.post_params['flags']
			for flag in use_local_flags:
				temp_use += flag + " "
		#get the make.conf
		etc_files = self.shared_info.install_profile.get_etc_files()
		if etc_files.has_key("make.conf"):
			make_conf = etc_files['make.conf']
		else:
			make_conf = {}
		make_conf["USE"] = self.shared_info.temp_use + temp_use
		etc_files['make.conf'] = make_conf
		self.shared_info.install_profile.set_etc_files(etc_files)
		return self.wrap_in_webgli_template(data)
	def configfiles(self):
		data = "<h2>Configuration Files Settings</h2><p>Make.conf Settings:</p>"
		data += '<form action="/webgli/saveconfigfiles" method="POST" enctype="multipart/form-data">'
		arch_procs = { 'x86': ("i386", "i486", "i586", "pentium", "pentium-mmx", "i686", "pentiumpro", "pentium2", "pentium3", "pentium3m", "pentium-m", "pentium4", "pentium4m", "prescott", "nocona", "k6", "k6-2", "k6-3", "athlon", "athlon-tbird", "athlon-4", "athlon-xp", "athlon-mp", "k8", "opteron", "athlon64", "athlon-fx", "winchip-c6", "winchip2", "c3", "c3-2") }
		etc_files = self.shared_info.install_profile.get_etc_files()
		if etc_files.has_key("make.conf"):
			make_conf = etc_files['make.conf']
		else:
			make_conf = {}
		
		data += '<h3>CFLAGS Settings: </h3>(only show these if not dynamic):<table width="100%"  border="1"><tr><td scope="col"><div align="left">Processor:<select name="proc" id="proc">'
		procs = arch_procs[self.shared_info.client_profile.get_architecture_template()]
		for proc in procs:
			data += "<option value=\""+proc+"\">"+proc+"</option>\n"
		data += """
					</select>
			</div></td>
			<td scope="col">Optimizations: 
				<select name="optim1" id="optim1">
					<option value="-O1">-O1</option>
					<option value="-O2" selected>-O2 (Recommended)</option>
					<option value="-O3">-O3</option>
					<option value="-O4">-O4</option>
					<option value="-O5">-O5</option>
					<option value="-O6">-O6</option>
					<option value="-O7">-O7</option>
					<option value="-O8">-O8</option>
					<option value="-O9">-O9 (You crazy fool!)</option>
						</select> </td>
		</tr>
		<tr>
			<td>Common CFLAGS:<br> 
				<input name="optim2" type="checkbox" id="optim2" value="-pipe">
-pipe<br>
<input name="optim2" type="checkbox" id="optim2" value="-fomit-frame-pointer">-fomit-frame-pointer</td>
			<td>Additional CFLAGS:
			<input name="optim3" type="text" id="optim3" size="60"></td>
		</tr>
	</table><hr>
	<h3>CHOST Setting:</h3>
		<select name="chost" size="4" id="chost">"""

		if self.shared_info.client_profile.get_architecture_template() == "x86":
			data += "<option value=\"i386-pc-linux-gnu\">i386-pc-linux-gnu</option>\n"
			data += "<option value=\"i486-pc-linux-gnu\">i486-pc-linux-gnu</option>\n"
			data += "<option value=\"i586-pc-linux-gnu\">i586-pc-linux-gnu</option>\n"
			data += "<option value=\"i686-pc-linux-gnu\">i686-pc-linux-gnu</option>\n"
		if self.shared_info.client_profile.get_architecture_template() == "amd64":
			data += "<option value=\"x86_64-pc-linux-gnu\">x86_64-pc-linux-gnu</option>\n"
		if self.shared_info.client_profile.get_architecture_template() == "alpha":
			data += "<option value=\"alpha-unknown-linux-gnu\">alpha-unknown-linux-gnu</option>\n"
		if self.shared_info.client_profile.get_architecture_template() == "ppc":
			data += "<option value=\"powerpc-unknown-linux-gnu\">powerpc-unknown-linux-gnu</option>\n"		
		if self.shared_info.client_profile.get_architecture_template() == "ppc64":
			data += "<option value=\"powerpc64-unknown-linux-gnu\">powerpc64-unknown-linux-gnu</option>\n"		
		if self.shared_info.client_profile.get_architecture_template() in ["sparc", "sparc64"]:
			data += "<option value=\"sparc-unknown-linux-gnu\">sparc-unknown-linux-gnu</option>\n"		
		if self.shared_info.client_profile.get_architecture_template() == "hppa":
			data += "<option value=\"hppa-unknown-linux-gnu\">hppa-unknown-linux-gnu</option>\n"
			data += "<option value=\"hppa1.1-unknown-linux-gnu\">hppa1.1-unknown-linux-gnu</option>\n"
			data += "<option value=\"hppa2.0-unknown-linux-gnu\">hppa2.0-unknown-linux-gnu</option>\n"
		if self.shared_info.client_profile.get_architecture_template() == "mips":
			data += "<option value=\"mips-unknown-linux-gnu\">mips-unknown-linux-gnu</option>\n"
		data += """</select>
<hr>
	<table width="100%"  border="1">
		<tr>
			<td scope="col"><input name="unstable" type="checkbox" id="unstable" value="~arch">
			Use unstable (~arch) </td>
			<td scope="col"><input name="binary" type="checkbox" id="binary" value="binary">
			Build binary packages </td>
			<td scope="col"><input name="distcc" type="checkbox" id="distcc" value="distcc">
			Distcc</td>
			<td scope="col"><input name="ccache" type="checkbox" id="ccache" value="ccache">
			ccache</td>
			<td scope="col">MAKEOPTS:			 
			<input name="makeopts" type="text" id="makeopts" value="-j2" size="10" maxlength="5"></td>
		</tr>
	</table>
	<p>
		<input name="savemakeconf" type="submit" id="savemakeconf" value="Save Make.Conf Settings">
</p>
</form>"""
		return self.wrap_in_webgli_template(data)
	def saveconfigfiles(self):
		data = ""
		temp_use = "-* "
		#for flag in use_flags:
		#	temp_use += flag + " "
		#for flag in use_local_flags:
		#	temp_use += flag + " "
		#make_conf["USE"] = temp_use
		return self.wrap_in_webgli_template(data)
	def configfiles2(self):
		data = ""
		data += """
		<table cellspacing="0" cellpadding="0" width="650" height="500" border="1">
  <tr height="33%">
    <td>
      <table width="100%" height="100%" border="1">
        <tr>
          <td width="50%">
            <table width="100%" height="100%" border="1">
              <tr>

                <td>clock - UTC/local</td>
              </tr>
              <tr>
                <td>default editor</td>
              </tr>
            </table>
          </td>
          <td width="50%">display manager</td>

        </tr>
      </table>
    </td>
  </tr>
  <tr height="66%">
    <td>
      <table width="100%" height="100%" border="1">
        <tr>
          <td width="33%">Keymap<br><br>Windowkeys<br><br>Extended</td>

          <td width="33%">
            <table width="100%" height="100%" border="1">
              <tr>
                <td>console font</td>
              </tr>
              <tr>
                <td>xsession</td>
              </tr>

            </table>
          </td>
          <td width="33%">protocols</td>
        </tr>
      </table>
    </td>
  </tr>
</table>"""
		return self.wrap_in_webgli_template(data)
	def kernel(self):
		data = "<p>Kernel Settings:</p>\n";
		sources = self.shared_info.install_profile.get_kernel_source_pkg()
		build_method = self.shared_info.install_profile.get_kernel_build_method()
		bootsplash = self.shared_info.install_profile.get_kernel_bootsplash()
		configuri= self.shared_info.install_profile.get_kernel_config_uri()
		data += '<form name="kernel" method="post" action="/webgli/savekernel" enctype="multipart/form-data">'
		data += """  <p>Choose which kernel sources to use for your system. If using a previously-made kernel configuration, make sure the sources match the kernel used to create the configuration.</p>
<table width="100%"  border="1">
<tr><td><input name="sources" type="radio" value="livecd-kernel" """
		if sources == "livecd-kernel":
			data += "checked"
		data += '>Livecd Kernel </td><td>Use the running kernel (fastest)</td></tr><tr><td>'+"\n"+'<input name="sources" type="radio" value="vanilla-sources" '
		if sources == "vanilla-sources":
			data += "checked"
		data += '>Vanilla (normal) </td><td>Normal. The Unaltered Linux Kernel ver 2.6+ (safest) (recommended) </td></tr>'+"\n"+'<tr><td><input name="sources" type="radio" value="gentoo-sources" '
		if sources == "gentoo-sources":
			data += "checked"
		data += ">Gentoo</td><td>Gentoo's optimized 2.6+ kernel. (less safe) </td>		</tr>\n"+'<tr><td><input name="sources" type="radio" value="hardened-sources" '
		if sources == "hardened-sources":
			data += "checked"
		data += ">Hardened</td><td>Hardened sources for the 2.6 kernel tree</td></tr>\n"+'<tr><td><input name="sources" type="radio" value="grsec-sources" '
		if sources == "grsec-sources":
			data += "checked"
		data += ">grsec</td><td>Vanilla sources with grsecurity patches </td></tr>\n"
		if sources not in ["livecd-kernel", "vanilla-sources", "gentoo-sources", "hardened-sources", "grsec-sources"]:
			data += '<tr><td><input name="sources" type="radio" value="Other" checked>Other</td><td>Specify your own here: <input name="manualsouces" type="text" id="manualsouces" value="'+sources+'"></td></tr></table>'+"\n"
		else:
			data += '<tr><td><input name="sources" type="radio" value="Other">Other</td><td>Specify your own here: <input name="manualsouces" type="text" id="manualsouces" value=""></td></tr></table>'+"\n"
		data += """<hr>
<table width="507"	border="1">
	<tr>
		<td colspan="2" scope="col"><p>There are currently two ways the installer can compile a kernel for your new system. You can either provide a previously-made kernel configuration file and use the traditional kernel-compiling procedure (no initrd) or have genkernel automatically create your kernel for you (with initrd).</p>
		<p>If you do not have a previously-made kernel configuration, YOU MUST CHOOSE Genkernel. Choose which method you want to use:</p></td>
	</tr>
	<tr>
		<td width="143" scope="col"><input name="build_method" type="radio" value="genkernel" """
		if build_method == "genkernel":
			data += "checked"
		data += '>Genkernel</td><td width="348" scope="col"><input name="build_method" type="radio" value="custom" '
		if build_method == "custom":
			data += "checked"
		data += ">Traditional (requires a config!)</td></tr></table>\n"
		data += '<p><input name="bootsplash" type="checkbox" id="bootsplash" value="True" '
		if bootsplash:
			data += "checked"
		data += ">Display the bootsplash screen on startup </p><p>If you have a custom kernel configuration, enter its location (otherwise just leave blank):\n"
		data += '<input name="configuri" type="text" id="configuri" '
		if configuri:
			data += 'value="'+configuri+'">'
		data += """<input name="browseuri" type="button" id="browseuri" value="Browse" onClick="window.open('/webgli/URIBrowser?screen=kernel&baseuri=' + document.kernel.configuri.value, 'uribrowser', 'width=500,height=500,toolbars=no,statusbar=no,menubar=no,scrollbars=yes')"> 
		</p><p><input name="setkernel" type="submit" id="setkernel" value="Save Kernel Settings"></p></form>"""
		
		return self.wrap_in_webgli_template(data)
	def savekernel(self):
		data = ""
		if self.post_params['setkernel']:
			if self.post_params['manualsouces']:
				try:
					self.shared_info.install_profile.set_kernel_source_pkg(None,self.post_params['manualsouces'],None)
				except:
					data += "ERROR: Could not set the kernel sources!" + self.post_params['manualsouces']
			elif self.post_params['sources']:
				try:
					self.shared_info.install_profile.set_kernel_source_pkg(None,self.post_params['sources'],None)
				except:
					data += "ERROR: Could not set the kernel sources!" + self.post_params['sources']
			if self.post_params['build_method']:
				try:
					self.shared_info.install_profile.set_kernel_build_method(None,self.post_params['build_method'],None)
				except:
					data += "ERROR: Could not set the kernel build method!"
				if self.post_params['configuri']:
					try:
						self.shared_info.install_profile.set_kernel_config_uri(None,self.post_params['configuri'],None)
					except:
						data += "ERROR: Could not set the kernel config URI!"
			if self.post_params['bootsplash']:
				try:
					self.shared_info.install_profile.set_kernel_bootsplash(None,self.post_params['bootsplash'],None)
				except:
					data += "ERROR: Could not set the kernel bootsplash!" + self.post_params['bootsplash']
		
		return self.wrap_in_webgli_template(data)
	def bootloader(self):
		arch = self.shared_info.client_profile.get_architecture_template()
		bootloader = self.shared_info.install_profile.get_boot_loader_pkg()
		arch_loaders = { 'x86': [
				("grub",(u"GRand Unified Bootloader, newer, RECOMMENDED")),
				("lilo",(u"LInux LOader, older, traditional.(detects windows partitions)"))],
			'amd64': [
				("grub",(u"GRand Unified Bootloader, newer, RECOMMENDED"))]} #FIXME ADD OTHER ARCHS
		data = "<p>Bootloader Settings:</p>"
		data += '<form name="Bloader" method="post" action="/webgli/savebootloader" enctype="multipart/form-data">'
		data += """  <p>To boot successfully into your new Linux system, a bootloader will be needed. If you already have a bootloader you want to use you can select None here. The bootloader choices available are dependent on what GLI supports and what architecture your system is. Choose a bootloader:</p>
		<table width="100%"  border="1">"""
		boot_loaders = arch_loaders[arch]
		boot_loaders.append(("none", (u"Do not install a bootloader.	(System may be unbootable!)")))
		for i,bloader in enumerate(boot_loaders):
			data += '<tr><td><input name="bootloader" type="radio" value="'+boot_loaders[i][0]+'" '
			if bootloader == boot_loaders[i][0]:
				data += "checked"
			data += '>'+boot_loaders[i][0]+'</td><td>'+boot_loaders[i][1]+"</td></tr>\n"
		data += """
		</table>
		<hr>
		Most bootloaders have the ability to install to either the Master Boot Record (MBR) or some other partition. Most people will want their bootloader installed on the MBR for successful boots, but if you have special circumstances, you can have the bootloader installed to the /boot partition instead. Do you want the boot loader installed in the MBR? (YES is RECOMMENDED)
		<p>"""
		bootmbr = self.shared_info.install_profile.get_boot_loader_mbr()
		data += '<input name="bootmbr" type="checkbox" id="bootmbr" value="True"'
		if bootmbr:
			data += " checked"
		data += """>Install to MBR</p>
		<p>If you have any additional optional arguments you want to pass to the kernel at boot, type them here: 
		<input name="bootargs" type="text" id="bootargs" """
		bootargs = self.shared_info.install_profile.get_bootloader_kernel_args()
		if bootargs:
			data += ' value="'+bootargs+'"'
		data += """>
	</p>
		<p>
		<input name="setbootloader" type="submit" id="setbootloader" value="Save Bootloader Settings">
		</p>
	</form>"""

		return self.wrap_in_webgli_template(data)
	def savebootloader(self):
		data = ""
		if self.post_params['setbootloader']:
			if self.post_params['bootloader']:
				try:
					self.shared_info.install_profile.set_boot_loader_pkg(None,self.post_params['bootloader'],None)
				except:
					data += "ERROR: Could not set the bootloader pkg!"
			if self.post_params['bootmbr']:
				try:
					self.shared_info.install_profile.set_boot_loader_mbr(None,self.post_params['bootmbr'],None)
				except:
					data += "ERROR: Could not set the bootloader MBR flag!"
			else:
				try:
					self.shared_info.install_profile.set_boot_loader_mbr(None,False,None)
				except:
					data += "ERROR: Could not set the bootloader MBR flag!"
			if self.post_params['bootargs']:
				try:
					self.shared_info.install_profile.set_bootloader_kernel_args(None,self.post_params['bootargs'],None)
				except:
					data += "ERROR: Could not set the bootloader kernel arguments!"
		return self.wrap_in_webgli_template(data)
	def timezone(self):
		data = "<h2>Timezone Setup </h2>"
		if self.post_params['back']:
			zonepath = self.post_params['tzback']
		if self.get_params['zonepath']:
			zonepath = self.get_params['zonepath']
			if zonepath[-1] != "/":
				try:
					self.shared_info.install_profile.set_time_zone(None, zonepath[20:], None)
					return self.wrap_in_webgli_template("Timezone Set")
				except:
					return self.wrap_in_webgli_template("ERROR: Could not set that timezone!")	
		else:
			zonepath = "/usr/share/zoneinfo/"
		skiplist = ["zone.tab","iso3166.tab","posixrules"]
		tzlist = []
		for entry in os.listdir(zonepath):
			if entry not in skiplist:
				if os.path.isdir(zonepath + "/" + entry): entry += "/"
				tzlist.append(entry)
		tzlist.sort()
		
		data += "Timezones:<br>\n"
		data += '<form name="Timezone" method="post" action="/webgli/Timezone" enctype="multipart/form-data">'
		data += '<input type="hidden" name="tzback" value="'+zonepath+'"><br>'
		for timezone in tzlist:
			data += '<a href="/webgli/Timezone?zonepath='+zonepath+timezone+'">'+timezone+"</a><br>\n"
		data += '<br><input type="submit" name="back" value="Back">'
		data += "</form>"
		return self.wrap_in_webgli_template(data)
	def savetimezone(self):
		data = ""
		return self.wrap_in_webgli_template(data)
	def networking(self):
		data = ""
		#interfaces = self.shared_info.interfaces
		#if not interfaces:
		interfaces = self.shared_info.install_profile.get_network_interfaces()
		CC_iface = self.shared_info.client_profile.get_network_interface()
		if CC_iface and (CC_iface not in interfaces):
			#The CC has a network config that's not already there.	Preload it.
			CC_net_type = self.shared_info.client_profile.get_network_type()
			if CC_net_type == 'dhcp':
				try:
					interfaces[CC_iface] = ('dhcp', self.shared_info.client_profile.get_network_dhcp_options(), None)
				except:
					pass
			else:
				try:
					interfaces[CC_iface] = (self.shared_info.client_profile.get_network_ip(), self.shared_info.client_profile.get_network_broadcast(), self.shared_info.client_profile.get_network_netmask())
				except:
					pass
		data += """
		<script>
		function change_editiface() {
			for(i=0;i<document.Networking.elements.length;i++) {
			if(document.Networking.elements[i].name == "EditIface" && document.Networking.elements[i].checked) {
				location.replace('/webgli/Networking?editiface='+ document.Networking.elements[i].value);
						}
					}
		}
		</script>
		 <p>Devices:</p>
		 <form name="Networking" method="post" action="/webgli/savenetworking" enctype="multipart/form-data">
			 <table width="100%"	border="1">
			 <tr>
				 <th scope="col">Device</th>
				 <th scope="col">IP Address </th>
				 <th scope="col">Broadcast</th>
				 <th scope="col">Netmask</th>
				 <th scope="col">Gateway</th>
				 <th scope="col">DHCP Options </th>
			 </tr>"""
			 
		for iface in interfaces:
			data += '<tr><td><input type="radio" name="EditIface" value="'+str(iface)+'">'+iface+"</td>\n"
			if interfaces[iface][0] == 'dhcp':
				data += '<td>DHCP</td><td>x</td><td>x</td><td>x</td><td>'+interfaces[iface][1]+"</td></tr>\n"
			else:
				data += '<td>'+interfaces[iface][0]+'</td><td>'+interfaces[iface][1]+'</td><td>'+interfaces[iface][2]+"</td><td></td></tr>\n"
		data += "</table>\n"
		data += """
			<input name="EditIfaceSubmit" type="button" id="EditIfaceSubmit" value="EDIT" onclick="change_editiface()">
			<input name="DelIfaceSubmit" type="submit" id="DelIfaceSubmit" value="DELETE">"""
		if self.get_params['editiface']:
			iface = self.get_params['editiface']
			data += '<input type="hidden" name="ifacemanual" value="'+iface+'">'
			data += "<h3>Edit Interface "+iface+"</h3>\n"
			data += "<table><tr><td>\n"
			data += '<select name="Network_Type" size="3">'
			data += '<option value="dhcp" '
			if interfaces[iface][0] == "dhcp":
				data += "selected" 
			data += ' >DHCP</option>'
			data += '<option value="static" '
			if interfaces[iface][0] != "dhcp":
				data += "selected"
			data += ' >Manual Config</option>'
			data += '</select>'
			data += '</td><td>'
			data += 'Networking Info for Manual Configurations:<br>'
			data += 'Enter your IP address: <input name="ip" type="text" length="50" maxlength="15" value="'
			if interfaces[iface][0] != "dhcp":
				data += interfaces[iface][0]
			data += '"><br>'
			data += 'Enter your Broadcast address: <input name="broadcast" type="text" length="50" maxlength="15" value="'
			if interfaces[iface][0] != "dhcp":
				data += interfaces[iface][1]
			data += '"><br>'
			data += 'Enter your Netmask: <input name="netmask" type="text" length="50" maxlength="15" value="'
			if interfaces[iface][0] != "dhcp":
				data += interfaces[iface][2]
			data += '"><br></td></tr></table>'
			data += '<input type="submit" value="Edit Network Device" name="AddIfaceSubmit">'
		else:
			data += """
			 <h3>Add a new Interface:</h3>
			 <p>
			 <select name="ifacelist" id="ifacelist">"""
			device_list = GLIUtility.get_eth_devices()
			for device in device_list:
				if device not in interfaces:
					data += '<option value="'+device+'">'+device+': '+GLIUtility.get_interface_realname(device)+"</option>\n"
			data += """</select> 
				 or type your own: 
				 <input name="ifacemanual" type="text" id="ifacemanual" size="10">
			</p><hr><table><tr><td>"""
			data += '<select name="Network_Type" size="3">'
			data += '<option value="dhcp">DHCP</option>'
			data += '<option value="static">Manual Config</option>'
			data += '</select>'
			data += '</td><td>'
			data += 'Networking Info for Manual Configurations:<br>'
			data += 'Enter your IP address: <input name="ip" type="text" length="50" maxlength="15" value="192.168."><br>'
			data += 'Enter your Broadcast address: <input name="broadcast" type="text" length="50" maxlength="15" value=".255"><br>'
			data += 'Enter your Netmask: <input name="netmask" type="text" length="50" maxlength="15" value="255.255.255.0"><br></td></tr></table>'
			data += '<input type="submit" value="Add Network Device" name="AddIfaceSubmit"><hr>'
		
		data += 'Enter your default gateway: <table>'
		default_gateway = self.shared_info.install_profile.get_default_gateway()
		if default_gateway:
			gway_ip = default_gateway[1]
			gway_iface = default_gateway[0]
		else:
			gway_iface = None
			gway_ip = ""
		for iface in interfaces:
			data += '<tr><td><input type="radio" name="GatewayIface" value="'+iface+'" '
			if iface == gway_iface:
				data += "checked"
			data += ' >'+iface+"</td></tr>\n"
		data += '<tr><td>Address:<input name="gateway" type="text" length="50" maxlength="15" value="'+gway_ip+'"><br>'
		dnsservers = " ".join(self.shared_info.install_profile.get_dns_servers())
		data += 'Enter your DNS servers (space-separated): <input name="dnsserver" type="text" length="70" value="'+dnsservers+'">'
		data += """		<p>Wireless stuff here. ESSID: Key:  </p>
			 <p>Hostname:
			 <input name="hostname" type="text" id="hostname">
			 </p>
			 <p>Domainname:
			 <input name="domainname" type="text" id="domainname">
			 </p>
			 <p>NIS Domainname: 
			 <input name="nisdomainname" type="text" id="nisdomainname"> 
			 </p>
			 <p>
			 <input name="savenetwork" type="submit" id="savenetwork" value="Save Network Information">
		</p>
		 </form>"""
		return self.wrap_in_webgli_template(data)
	def savenetworking(self):
		data = ""
		#interfaces = self.shared_info.interfaces
		interfaces = self.shared_info.install_profile.get_network_interfaces()
		if self.post_params['savenetwork']:
			try:
				self.shared_info.install_profile.set_network_interfaces(interfaces)
				data += "Network Interfaces saved.<br>\n"
			except:
				data += "ERROR: Could not set the network interfaces!<br>\n"
		elif self.post_params['AddIfaceSubmit']:
			#network interface
			if self.post_params['ifacemanual']:
				newnic = self.post_params['ifacemanual']
			elif self.post_params['ifacelist']:
				newnic = self.post_params['ifacelist']
			else:
				data += "ERROR: No Network device selected<br>\n"
			#network type
			if self.post_params['Network_Type'] == "dhcp":
				#if self.post_params[' FIXME DHCP OPTIONS
				try:
					interfaces[newnic] = ('dhcp', "",None)
					self.shared_info.install_profile.set_network_interfaces(interfaces)
					data += "Network Interfaces saved.<br>\n"
				except:
					data += "ERROR: Could not set interface DHCP<br>\n"
			elif self.post_params['Network_Type'] == "static":
				if 'ip' in self.post_params:
					data += "Found an IP: you submitted " + self.post_params['ip'] + "<BR>\n"
					newip = self.post_params['ip']
				if 'broadcast' in self.post_params:
					data += "Found an broadcast IP: you submitted " + self.post_params['broadcast'] + "<BR>\n"
					newbroadcast = self.post_params['broadcast']
				if 'netmask' in self.post_params:
					data += "Found an netmask IP: you submitted " + self.post_params['netmask'] + "<BR>\n"
					newnetmask = self.post_params['netmask']
				if 'gateway' in self.post_params:
					data += "Found an gateway IP: you submitted " + self.post_params['gateway'] + "<BR>\n"
					newgateway = self.post_params['gateway']
				try:
					interfaces[newnic] = (newip, newbroadcast, newnetmask)
					self.shared_info.install_profile.set_network_interfaces(interfaces)
					data += "Network Interfaces saved.<br>\n"
				except:
					data += "ERROR: Could not add the new interface.<BR>\n"
		
		elif self.post_params['DelIfaceSubmit']:
			data += "Deleting Interface"
			if self.post_params['EditIface']:
				try:
					iface = self.post_params['EditIface']
					del interfaces[iface]
					self.shared_info.install_profile.set_network_interfaces(interfaces)
					data += "Network Interfaces saved.<br>\n"
					return self.return_redirect("/webgli/Networking")
				except:
					data += "ERROR: Could not delete the interface.<BR>\n"	
			else:
				data += "ERROR: No device selected to delete!<br>\n"
			
		#elif self.post_params['EditIfaceSubmit']:
		
		if 'dnsserver' in self.post_params:
			data += "Found an DNS server: you submitted " + self.post_params['dnsserver'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_dns_servers(None, self.post_params['dnsserver'], None)
			except:
				data += "ERROR: Could not set the DNS Server<BR>\n"
				
		return self.wrap_in_webgli_template(data)
	def daemons(self):
		data = "<h2>Cron and Logging Daemons:</h2>\n";
		cron = self.shared_info.install_profile.get_cron_daemon_pkg()
		logger = self.shared_info.install_profile.get_logging_daemon_pkg()
		data += '<form name="daemons" method="post" action="/webgli/savedaemons" enctype="multipart/form-data">'
		data += """  <p>Choose which cron daemon to use for your system. While it is possible to not choose a cron daemon and still have a working system, this is NOT recommended and is considered a VERY BAD THING.<br>Choose your cron daemon:</p>
			<table width="100%"  border="1">
			<tr><td><input name="cron" type="radio" value="vixie-cron" """
		if cron == "vixie-cron":
			data += "checked"
		data += ">Vixie-cron </td><td>Paul Vixie's cron daemon, fully featured, RECOMMENDED.</td></tr>\n"
		data += '<tr><td><input name="cron" type="radio" value="dcron" '
		if cron == "dcron":
			data += "checked"
		data += ">Dcron </td><td>A cute little cron from Matt Dillon.</td></tr>\n"
		data += '<tr><td><input name="cron" type="radio" value="fcron" '
		if cron == "fcron":
			data += "checked"
		data += ">Fcron </td><td>A scheduler with extended capabilities over cron & anacron.</td></tr>\n"
		data += '<tr><td><input name="cron" type="radio" value="none" '
		if cron == "none":
			data += "checked"
		data += ">None </td><td>Don't use a cron daemon. (NOT Recommended!).</td></tr></table>\n"
		data += "<br><hr><p>Choose which logging daemon to use for your system.  A logger is required by the Gentoo Manual.<br>Choose your logging daemon:</p>\n  <table width=\"100%\" border=\"1\">\n"
		data += '<tr><td><input name="logger" type="radio" value="syslog-ng" '
		if logger == "syslog-ng":
			data += "checked"
		data += "> syslog-ng </td><td>An advanced system logger. (default)</td></tr>\n"
		data += '<tr><td><input name="logger" type="radio" value="metalog" '
		if logger == "metalog":
			data += "checked"
		data += "> metalog </td><td>A Highly-configurable system logger.</td></tr>\n"
		data += '<tr><td><input name="logger" type="radio" value="syslogkd" '
		if logger == "syslogkd":
			data += "checked"
		data += "> syslogkd </td><td>The traditional set of system logging daemons.</td></tr></table>\n"
		data += '<input type="submit" name="savedaemons" value="Save Daemons"></form>'
		
		return self.wrap_in_webgli_template(data)
	def savedaemons(self):
		data = ""
		if self.post_params['savedaemons']:
			if self.post_params['logger']:
				try:
					self.shared_info.install_profile.set_logging_daemon_pkg(None, self.post_params['logger'], None)
				except:
					data += "ERROR: Could not set logger!<br>\n"
			if self.post_params['cron']:
				try:
					self.shared_info.install_profile.set_cron_daemon_pkg(None, self.post_params['cron'], None)
				except:
					data += "ERROR: Could not set cron daemon!<br>\n"
		return self.wrap_in_webgli_template(data)
	def services(self):
		data = ""
		if self.shared_info.install_profile.get_services():
			services = self.shared_info.install_profile.get_services()
			if isinstance(services, str):
				services = services.split(',')
		else:
			services = []
		choice_list = [("alsasound", _(u"ALSA Sound Daemon"),int("alsasound" in services)),
			("apache", _(u"Common web server (version 1.x)"),int("apache" in services)),
			("apache2", _(u"Common web server (version 2.x)"),int("apache2" in services)),
			("distccd", _(u"Distributed Compiling System"),int("distccd" in services)),
			("esound", _(u"ESD Sound Daemon"),int("esound" in services)),
			("hdparm", _(u"Hard Drive Tweaking Utility"),int("hdparm" in services)),
			("local", _(u"Run scripts found in /etc/conf.d/local.start"),int("local" in services)),
			("portmap", _(u"Port Mapping Service"),int("portmap" in services)),
			("proftpd", _(u"Common FTP server"),int("proftpd" in services)),
			("sshd", _(u"SSH Daemon (allows remote logins)"),int("sshd" in services)),
			("xfs", _(u"X Font Server"),int("xfs" in services)),
			("xdm", _(u"X Daemon"),int("xdm" in services))]
		services_string = _(u"Choose the services you want started on bootup.  Note that depending on what packages are selected, some services listed will not exist.")
		data += services_string
		data += '<form name="services" method="post" action="/webgli/saveservices" enctype="multipart/form-data">'
		data += "<table border=\"1\"><tr><td>Activate</td><td>Service</td><td>Description</td></tr>"
		for i,choice in enumerate(choice_list):
			data += '<tr><td><input type="checkbox" name="services" value="'+choice_list[i][0]+'" '
			if choice_list[i][2]:
				data += "checked"
			data += "></td><td>"+choice_list[i][0]+"</td><td>"+choice_list[i][1]+"</td></tr>\n"
		data += "</table>\n"
		data += "<hr>You can also opt to enter your services in a comma-separated list (NOTE Manual list overwrites checked selections!): "
		data += '<input type="text" name="servicesmanual" value="'+string.join(services, ',')+'">'
		data += '<br><input type="submit" name="saveservices" value="Save Services"></form>'
		return self.wrap_in_webgli_template(data)
	def saveservices(self):
		data = ""
		if self.post_params['saveservices']:
			if self.post_params['servicesmanual']:
				services = self.post_params['servicesmanual']				
			elif self.post_params['services']:
				services = self.post_params['services']
				services = string.join(services, ',')
			try:
				
				print services + "\n"
				if services:
					self.shared_info.install_profile.set_services(None, services, None)
			except:
				data += "ERROR! Could not set the services list.<br>\n"
		return self.wrap_in_webgli_template(data)
	def extrapackages(self):
		data = ""
		grp_list = GLIUtility.get_grp_pkgs_from_cd()
		if self.post_params['packages']:
			try:
				packages = string.join(self.post_params['packages'], ' ')
				if packages:
					self.shared_info.install_profile.set_install_packages(None, packages, None)
			except:
				data += _(u"ERROR! Could not set the install packages! List of packages:<br>\n")
		if self.shared_info.install_profile.get_install_packages():
			install_packages = self.shared_info.install_profile.get_install_packages()
			if isinstance(install_packages, str):
				install_packages = install_packages.split()
		else:
			install_packages = []
		highlevel_menu = {"Desktop": _(u"Popular Desktop Applications"),
					"Servers": _(u"Applications often found on servers."), 
					"X11": _(u"Window managers and X selection."), 
					"Misc": _(u"Miscellaneous Applications you may want."), 
					"Recommended": _(u"Applications recommended by the GLI Team.")}
		
		data += """
		<script>
		</script>
		<form name="packages" action="/webgli/ExtraPackages" method="POST" enctype="multipart/form-data">
		"""
		for param in self.get_params:
			if "show" in param:  #this means it's a param referring to a group to show.  include it as a hidden so it'll get shown next time too.
				data += '<input type="hidden" name="'+param+'" value="'+self.get_params[param]+"\">\n"
		for param in self.post_params:
			if "show" in param:  #this means it's a param referring to a group to show.  include it as a hidden so it'll get shown next time too.
				if type(self.post_params[param]) == list:
					self.post_params[param] = self.post_params[param][-1]
				data += '<input type="hidden" name="'+param+'" value="'+self.post_params[param]+"\">\n"
		#Start the table
		data += "<h2>Extra Packages</h2>Your current package list is: "+string.join(install_packages, ',')
		data += '<table width="100%"  border="1">'
		for group in highlevel_menu:
			if group == _(u"Desktop"):
				pkgs = {"gaim": _(u"GTK Instant Messenger client"),
				"gftp": _(u"Gnome based FTP Client"),
				"evolution": _(u"A GNOME groupware application, a Microsoft Outlook workalike"),
				"mozilla": _(u"The Mozilla Web Browser"),
				"mozilla-firefox": _(u"The Mozilla Firefox Web Browser"),
				"mozilla-thunderbird": _(u"Thunderbird Mail Client"),
				"mplayer": _(u"Media Player for Linux"),
				"openoffice": _(u"OpenOffice.org, a full office productivity suite."),
				"openoffice-bin": _(u"Same as OpenOffice but a binary package (no compiling!)"),
				"realplayer": _(u"Real Media Player"),
				"xchat": _(u"Graphical IRC Client"),
				"xmms": _(u"X MultiMedia System")  }
			#Applications often found on servers.
			elif group == _(u"Servers"):
				pkgs = {"apache":_(u"Apache Web Server"),
				"iptables":_(u"Linux kernel (2.4+) firewall, NAT and packet mangling tools"),
				"proftpd":_(u"ProFTP Server"),
				"samba":_(u"SAMBA client/server programs for UNIX"),
				"traceroute":_(u"Utility to trace the route of IP packets")  }
			#Window managers and X selection.
			elif group == _(u"X11"):
				pkgs = {"xorg-x11":_(u"An X11 implementation maintained by the X.Org Foundation."),
				"gnome":_(u"The Gnome Desktop Environment"),
				"kde":_(u"The K Desktop Environment"),
				"blackbox":_(u"A small, fast, full-featured window manager for X"),
				"enlightenment":_(u"Enlightenment Window Manager"),
				"fluxbox":_(u"Fluxbox is an X11 window manager featuring tabs and an iconbar"),
				"xfce4":_(u"XFCE Desktop Environment")  }
			#Miscellaneous Applications you may want.
			elif group == _(u"Misc"):
				pkgs = {"gkrellm":_(u"Single process stack of various system monitors"),
				"logrotate":_(u"Rotates, compresses, and mails system logs"),
				"slocate":_(u"Secure way to index and quickly search for files on your system"),
				"ufed":_(u"Gentoo Linux USE flags editor")  }
			#Recommended by the Gentoo Linux Installer Team
			elif group == _(u"Recommended"):
				pkgs = {"anjuta":_(u"A versatile IDE for GNOME"),
				"chkrootkit":_(u"a tool to locally check for signs of a rootkit"),
				"crack-attack":_(u"Addictive OpenGL-based block game"),
				"netcat":_(u"the network swiss army knife"),
				"nmap":_(u"A utility for network exploration or security auditing"),
				"screen":_(u"full-screen window manager that multiplexes between several processes")  }
			#FIXME ADD x of y SELECTED TO HEADER
			if self.post_params['show_'+group] == "Expand":
				data += '<tr><th scope="col"><input type="submit" name="show_'+group+'" value="Collapse"></th><td><input type="checkbox" name="all_'+group+'" value="checkbox" '
				#CALCULATE IF ALL PACKAGES IN GROUP ARE IN INSTALL PACKAGES
				allpkgsfound = True
				for pkg in pkgs:
					if not pkg in install_packages:
						allpkgsfound = False
				if allpkgsfound:
					data += "checked"
				data += '>All</td><th scope="col">'+highlevel_menu[group]+"</th></tr>\n"
			
			else:   #show plus sign for group and no table.
				data += '<tr><th scope="col"><input type="submit" name="show_'+group+'" value="Expand"></th><td><input type="checkbox" name="all_'+group+'" value="checkbox" '
				#CALCULATE IF ALL PACKAGES IN GROUP ARE IN INSTALL PACKAGES
				allpkgsfound = True
				for pkg in pkgs:
					if not pkg in install_packages:
						allpkgsfound = False
				if allpkgsfound:
					data += "checked"
				data += '>All</td><th scope="col">'+highlevel_menu[group]+"</th></tr>\n"
			#now show the packages in the group
			if self.post_params['show_'+group] == "Expand" or self.get_params['show_'+group] == "Expand":
				for pkg in pkgs:
					data += '<tr><td></td>'
					data += '<td> <input type="checkbox" name="packages" value="'+pkg+'" '
					if pkg in install_packages:
						data += "checked"
					data += '>'+pkg+'</td><td>'+pkgs[pkg]+"</td></tr>\n"
			else:
				for pkg in pkgs:
					if pkg in install_packages:
						data += '<tr><td></td><td> <input type="checkbox" name="packages" value="'+pkg+'" checked>'+pkg+'</td><td>'+pkgs[pkg]+"</td></tr>\n"
				
		return self.wrap_in_webgli_template(data)
	def savepackages(self):
		data = ""
		return self.wrap_in_webgli_template(data)
	def users(self):
		data = """
		<script>
		function change_edituser() {
			for(i=0;i<document.Users.elements.length;i++) {
			if(document.Users.elements[i].name == "edituser" && document.Users.elements[i].checked) {
				location.replace('/webgli/Users?edituser='+ document.Users.elements[i].value);
						}
					}
		}
		function verify_pass() {
			if(document.Users.rootpass1.value != document.Users.rootpass2.value) {
				alert("Passwords DO NOT match!");
			}
			else {
				alert("Passwords match.");
			}
		}
		</script>"""
		users = {}
		for user in self.shared_info.install_profile.get_users():
			print str(user[0]) + "	 " + str(user[1]) + "		" + str(user[2]) + "	 " + str(user[3])
			users[user[0]] = (user[0], user[1], user[2], user[3], user[4], user[5], user[6])
		data += "<p>User Settings:</p>\n"
		data += '<form name="Users" method="post" action="/webgli/saveusers" enctype="multipart/form-data">'
		data += """<p>Users:</p>
			<table width="100%"  border="1">
			<tr>
				<th scope="col">Username</th>
				<th scope="col">Groups</th>
				<th scope="col">Shell</th>
				<th scope="col">Home Directory </th>
				<th scope="col">UserID</th>
				<th scope="col">Comment</th>
			</tr>"""
		for user in users:
			data += '<tr><td><input name="edituser" type="radio" value="'+users[user][0]+'">'
			data += users[user][0]+"</td><td>"
			for group in users[user][2]:
				data += group + ", "
			data += "</td><td>"+users[user][3]+"</td><td>"+users[user][4]+"</td><td>"+users[user][5]+"</td><td>"+users[user][6]+"</td></tr>\n"
		
		data += """</table><br>
				<input name="usereditsubmit" type="button" value="EDIT" onclick="change_edituser()">
				<input name="userdelsubmit" type="submit" value="DELETE">"""
		root_pass = self.shared_info.install_profile.get_root_pass_hash()
		if not root_pass:
			data += """<p>Root Password is not yet set! Please set it:<br>
				<input name="rootpass1" type="password" id="rootpass1">
			and retype to verify: 
			<input name="rootpass2" type="password" id="rootpass2">
			<input name="verifyrootpass" type="button" id="verifyrootpass" value="Verify!" onclick="verify_pass()">
			<input name="setrootpassword" type="submit" value="Set"></p>"""
		else:
			data += """<p>Root Password is set. 
				<input name="setrootpass" type="submit" id="setrootpass" value="Reset Root Password"></p>"""
		if self.get_params['edituser']:
			username = self.get_params['edituser']
			data += """
				<p>Edit user """+username+""":</p>
				<table width="100%"  border="1">
					<tr>
					<td scope="col"><p>Username:
						<input name="newusername" type="text" id="newusername" """
			data += 'value="'+username+'">'
			data += '</p><p>Password (you must retype this):<input name="newuserpass" type="password"></p>'
			data += '<p>Shell (optional): <input name="newusershell" type="text" value="'+users[username][3]+'"></p>'
			data += '<p>Home Directory (optional): <input name="newuserhomedir" type="text" value="'+users[username][4]+'"></p>'
			data += '<p>UserID Number (optional): <input name="newuserid" type="text" value="'+users[username][5]+'"></p>'
			data += '<p>Comment (optional): <input name="newusercomment" type="text" value="'+users[username][6]+"\"></p></td>\n"
			data += '<td scope="col"><p>Groups:</p>'
			groups = string.join(users[username][2], ",")
			data += '<p>Manually specify (comma-separate)<input name="newusergroupsmanual" type="text" value="'+groups+'">'
			data += """
						</p>
						<input name="addnewuser" type="submit" id="addnewuser" value="Save Changes">
					</td>
					</tr>
				</table>"""
		else:
			data += """
				<p>Add a new user:</p>
				<table width="100%"  border="1">
					<tr>
					<td scope="col"><p>Username:
						<input name="newusername" type="text" id="newusername">
					</p>
					<p>Password:
						<input name="newuserpass" type="password" id="newuserpass">
					</p>
					<p>Shell (optional): 
						<input name="newusershell" type="text" id="newusershell">
					</p>
					<p>Home Directory (optional): 
						<input name="newuserhomedir" type="text" id="newuserhomedir">
					</p>
					<p>UserID Number (optional): 
						<input name="newuserid" type="text" id="newuserid">
					</p>
					<p>Comment (optional): 
						<input name="newusercomment" type="text" id="newusercomment">
					</p></td>
					<td scope="col"><p>Groups:</p>
						<p><input name="newusergroups" type="checkbox" id="newusergroups" value="users"> users<br>
						<input name="newusergroups" type="checkbox" id="newusergroups" value="wheel"> wheel<br>
						<input name="newusergroups" type="checkbox" id="newusergroups" value="audio"> audio<br>
						Manually specify (comma-separate)<input name="newusergroupsmanual" type="text" id="newusergroupsmanual">
						</p>
						<input name="addnewuser" type="submit" id="addnewuser" value="Add New User">
					</td>
					</tr>
				</table>"""
		data += "</form>"
		return self.wrap_in_webgli_template(data)
	def saveusers(self):
		data = ""
		users = {}
		for user in self.shared_info.install_profile.get_users():
			users[user[0]] = (user[0], user[1], user[2], user[3], user[4], user[5], user[6])
		if self.post_params['addnewuser']:
			if self.post_params['newusername'] and self.post_params['newuserpass']:
				newuser = self.post_params['newusername']
				newuserpass = self.post_params['newuserpass']
				groups = ()
				if self.post_params['newusergroupsmanual']:
					groups = string.split(self.post_params['newusergroupsmanual'], ",")
				elif self.post_params['newusergroups']:
					groups = self.post_params['newusergroups']
				if self.post_params['newusercomment']:
					newusercomment = self.post_params['newusercomment']
				else:
					newusercomment = ""
				if self.post_params['newuserid']:
					newuserid = self.post_params['newuserid']
				else:
					newuserid = ""
				if self.post_params['newuserhomedir']:
					newuserhomedir = self.post_params['newuserhomedir']
				else:
					newuserhomedir = "/home/"+newuser
				if self.post_params['newusershell']:
					newusershell = self.post_params['newusershell']
				else:
					newusershell = "/bin/bash"
				try:
					new_user = [newuser, GLIUtility.hash_password(newuserpass), groups, newusershell, newuserhomedir, newuserid, newusercomment]
					users[newuser] = new_user
					tmpusers = []
					for user in users:
						tmpusers.append(users[user])
					self.shared_info.install_profile.set_users(tmpusers)	
				except:
					data += "ERROR: could not set the users.<br>\n"				
			else:
				data += "ERROR: NO USERNAME SPECIFIED<br>\n"
		if self.post_params['rootpass1'] and self.post_params['rootpass2']:
			if self.post_params['rootpass1'] == self.post_params['rootpass2']:
				try:
					self.shared_info.install_profile.set_root_pass_hash(None, GLIUtility.hash_password(self.post_params['rootpass1']), None)
				except:
					data += "ERROR: Could not set root password!<br>\n"
			else:
				data += "ERROR: Passwords do not match!<br>\n"
		if self.post_params['setrootpass']:
			try:
				self.shared_info.install_profile.set_root_pass_hash(None, "",None)
				return self.return_redirect("/webgli/Users")
			except:
				data = "ERROR: Could not reset the root password!<br>\n"
		if self.post_params['userdelsubmit']:
			if self.post_params['edituser']:
				user_to_del = self.post_params['edituser']
				try:
					data += "Deleting user: "+user_to_del
					del users[user_to_del]
					tmpusers = []
					for user in users:
						tmpusers.append(users[user])
					self.shared_info.install_profile.set_users(tmpusers)	
				except:
					data += "ERROR: could not set the users.<br>\n"		
			
		return self.wrap_in_webgli_template(data)
	def review(self):
		settings = "<pre>Look carefully at the following settings to check for mistakes.\nThese are the installation settings you have chosen:\n\n"
		#Partitioning
		settings += "Partitioning:	\n	Key: Minor, Pri/Ext, Filesystem, MkfsOpts, Mountpoint, MountOpts, Size.\n"
		devices = self.shared_info.install_profile.get_partition_tables()
		drives = devices.keys()
		drives.sort()
		for drive in drives:
			settings += "  Drive: " + drive + devices[drive].get_model() + "\n"
			partlist = devices[drive].get_ordered_partition_list()
			tmpparts = devices[drive].get_partitions()
			for part in partlist:
				tmppart = tmpparts[part]
				entry = "		 "
				if tmppart.get_type() == "free":
					#partschoice = "New"
					entry += _(u" - Unallocated space (")
					if tmppart.is_logical():
						entry += _(u"logical, ")
					entry += str(tmppart.get_mb()) + "MB)"
				elif tmppart.get_type() == "extended":
					entry += str(int(tmppart.get_minor()))
					entry += _(u" - Extended Partition (") + str(tmppart.get_mb()) + "MB)"
				else:
					entry += str(int(tmppart.get_minor())) + " - "
					if tmppart.is_logical():
						entry += _(u"Logical (")
					else:
						entry += _(u"Primary (")
					entry += tmppart.get_type() + ", "
					entry += (tmppart.get_mkfsopts() or "none") + ", "
					entry += (tmppart.get_mountpoint() or "none") + ", "
					entry += (tmppart.get_mountopts() or "none") + ", "
					entry += str(tmppart.get_mb()) + "MB)"
				settings += entry + "\n"
			
		#Network Mounts:
		network_mounts = copy.deepcopy(self.shared_info.install_profile.get_network_mounts())
		settings += "\nNetwork Mounts: \n"
		for mount in network_mounts:
			settings += "  "+mount['host']+":"+mount['export']+"\n"
			
		#Install Stage:
		settings += "\nInstall Stage: " + str(self.shared_info.install_profile.get_install_stage()) + "\n"
		if self.shared_info.install_profile.get_dynamic_stage3():
			settings += "  Tarball will be generated on the fly from the CD.\n"
		else:
			settings += "  Tarball URI: " + self.shared_info.install_profile.get_stage_tarball_uri() + "\n"
			
		#Portage Tree Sync Type:
		settings += "\nPortage Tree Sync Type: " + self.shared_info.install_profile.get_portage_tree_sync_type() + "\n"
		if self.shared_info.install_profile.get_portage_tree_sync_type() == "snapshot":
			settings += "  Portage snapshot URI: " + self.shared_info.install_profile.get_portage_tree_snapshot_uri() + "\n"
			
		#Kernel Settings:
		settings += "\nKernel Settings:\n"
		settings += "  Kernel Sources: " + self.shared_info.install_profile.get_kernel_source_pkg() + "\n"
		if self.shared_info.install_profile.get_kernel_source_pkg() != "livecd-kernel":
			settings += "  Kernel Build Method: " + self.shared_info.install_profile.get_kernel_build_method() + "\n"
			if self.shared_info.install_profile.get_kernel_build_method() == "genkernel":
				settings += "  Kernel Bootsplash Option: " + str(self.shared_info.install_profile.get_kernel_bootsplash()) + "\n"
		if self.shared_info.install_profile.get_kernel_config_uri():
			settings += "  Kernel Configuration URI: " + self.shared_info.install_profile.get_kernel_config_uri() + "\n"
				
		#Bootloader Settings:
		settings += "\nBootloader Settings:\n"
		settings += "  Bootloader package: " + self.shared_info.install_profile.get_boot_loader_pkg() + "\n"
		if self.shared_info.install_profile.get_boot_loader_pkg() != "none":
			settings += "  Install bootloader to MBR: " + str(self.shared_info.install_profile.get_boot_loader_mbr()) + "\n"
			settings += "  Bootloader kernel arguments: " +self.shared_info.install_profile.get_bootloader_kernel_args() + "\n"
			
		#Timezone:
		settings += "\nTimezone: " + self.shared_info.install_profile.get_time_zone() + "\n"
		
		#Networking Settings:
		settings += "\nNetworking Settings: \n"
		interfaces = self.shared_info.install_profile.get_network_interfaces()
		for iface in interfaces:
			if interfaces[iface][0] == 'dhcp':
				settings += "  " + iface + _(u":	Settings: DHCP. Options: ") + interfaces[iface][1] + "\n"
			else:
				settings += "  " + iface + _(u"IP: ") + interfaces[iface][0] + _(u" Broadcast: ") + interfaces[iface][1] + _(u" Netmask: ") + interfaces[iface][2] + "\n"
		default_gateway = self.shared_info.install_profile.get_default_gateway()
		if default_gateway:
			settings += "  Default Gateway: " + default_gateway[0] + "/" + default_gateway[1] + "\n"
		settings += "  Hostname: " + self.shared_info.install_profile.get_hostname() + "\n"
		if self.shared_info.install_profile.get_domainname():
			settings += "  Domainname: " +self.shared_info.install_profile.get_domainname() + "\n"
		if self.shared_info.install_profile.get_nisdomainname():
			settings += "  NIS Domainname: " +self.shared_info.install_profile.get_nisdomainname() + "\n"
		if self.shared_info.install_profile.get_dns_servers():
			for dns_server in self.shared_info.install_profile.get_dns_servers():
				settings += "  DNS Server: " +dns_server + "\n"
		if self.shared_info.install_profile.get_http_proxy():
			settings += "  HTTP Proxy: " +self.shared_info.install_profile.get_http_proxy() + "\n"
		if self.shared_info.install_profile.get_ftp_proxy():
			settings += "  FTP Proxy: " +self.shared_info.install_profile.get_ftp_proxy() + "\n"
		if self.shared_info.install_profile.get_rsync_proxy():
			settings += "  RSYNC Proxy: " +self.shared_info.install_profile.get_rsync_proxy() + "\n"
			
		#Cron Daemon:
		settings += "\nCron Daemon: " + self.shared_info.install_profile.get_cron_daemon_pkg() + "\n"
		
		#Logger:
		settings += "\nLogging Daemon: " + self.shared_info.install_profile.get_logging_daemon_pkg() + "\n"
		
		#Extra packages:
		if self.shared_info.install_profile.get_install_packages():
			install_packages = self.shared_info.install_profile.get_install_packages()
		else:
			install_packages = []
		settings += "\nExtra Packages: "
		for package in install_packages:
			settings += package + " "
		settings += "\n"
		#Services:
		if self.shared_info.install_profile.get_services():
			services = self.shared_info.install_profile.get_services()
		else:
			services = []
		settings += "\nAdditional Services: "
		for service in services:
			settings += service + " "
		settings += "\n"
		
		#Other Configuration Settings (rc.conf):
		#Make.conf Settings:
		settings += "\nConfiguration Files Settings:\n"
		etc_files = self.shared_info.install_profile.get_etc_files()
		for etc_file in etc_files:
			settings += "  File:" + etc_file + "\n"
			if isinstance(etc_files[etc_file], dict):
				for name in etc_files[etc_file]:
					settings += "		 Variable: " + name + "		Value: " + etc_files[etc_file][name] + "\n"
			else:
				for entry in etc_files[etc_file]:
					settings += "		 Value: "+ entry + "\n"
		
		#Additional Users:
		settings += "\nAdditional Users:\n"
		users = {}
		for user in self.shared_info.install_profile.get_users():
			users[user[0]] = (user[0], user[1], user[2], user[3], user[4], user[5], user[6])
		for user in users:
			settings += "  Username: " + user
			settings += "\n		 Group Membership: " + string.join(users[user][2], ",")
			settings += "\n		 Shell: " + users[user][3]
			settings += "\n		 Home Directory: " + users[user][4]
			if users[user][5]:
				settings += "\n		 User Id: " + users[user][5]
			if users[user][6]:
				settings += "\n		 User Comment: " + users[user][6]
		settings += "</pre>"
		return self.wrap_in_webgli_template(settings)
	def savereview(self):
		data = ""
		return self.wrap_in_webgli_template(data)

	def uribrowser(self):
		formfields = {	'portage': "opener.document.portage.snapshoturi", 
						'stage': "opener.document.stage.tarballuri",
						'kernel': "opener.document.kernel.configuri" }
		try:
			formfield = formfields[self.get_params['screen']]
		except:
			return "Parameter 'screen' was not passed"
		if self.get_params['uritype']:
			if self.get_params['mirror']:
				uri = self.get_params['mirror']
				if not uri.endswith('/'):
					uri += "/"
			else:
				if self.get_params['uritype'] == "file":
					uri = "file://"
				else:
					uri = self.get_params['uritype'] + "://"
					if self.get_params['username']:
						uri += self.get_params['username']
						if self.get_params['password']:
							uri += ":" + self.get_params['password']
						uri += "@"
					uri += self.get_params['host']
					if self.get_params['port']:
						uri += ":" + self.get_params['port']
				uri += (self.get_params['path'] or "/")
		else:
			uri = self.get_params['baseuri']
		if not uri:
			uri = "file:///"
		if not uri.endswith('/'):
			uri = uri[:uri.rfind('/')+1]
		uriparts = list(GLIUtility.parse_uri(uri))
		for i in range(len(uriparts)):
			if not uriparts[i]:
				uriparts[i] = ""
		uritypes = { 'file': "", 'http': "", 'ftp': "", 'scp': "" }
		uritypes[uriparts[0]] = " selected"
		if uriparts[0] == "http":
			mirrors = GLIUtility.list_mirrors(http=True, ftp=False, rsync=False)
		elif uriparts[0] == "ftp":
			mirrors = GLIUtility.list_mirrors(http=False, ftp=True, rsync=False)
		else:
			mirrors = []
		mirrorlist = ""
		for mirror in mirrors:
			mirrorlist += '<option value="%s">%s</option>' % (mirror[0], mirror[1])
		content = """
		<script>
		function select_uri(uri) {
			%s.value = document.uri.baseuri.value + uri;
			window.close();
		}

		function browse_uri(uri) {
			location.replace('/webgli/URIBrowser?screen=%s&baseuri=' + uri);
		}

		function refresh_uri() {
			//location.replace('/webgli/URIBrowser?screen=%s&uritype=' + document.uri.uritype.value + '&host=' + document.uri.host.value + '&username=' + document.uri.username.value + '&password=' + document.uri.password.value + '&port=' + document.uri.port.value + '&path=' + document.uri.path.value + '&mirror=' + document.uri.mirror.value);
			document.uri.submit();
		}

		function change_uritype() {
			location.replace('/webgli/URIBrowser?screen=%s&uritype=' + document.uri.uritype.value);
		}
		</script>
		<h3>URI Browser</h3>
		<form name="uri" action="/webgli/URIBrowser" method="GET">
		<input type="hidden" name="baseuri" value="%s">
		<input type="hidden" name="screen" value="%s">
		<table>
			<tr>
				<td width="90">URI type:</td>
				<td><select name="uritype" onchange="change_uritype()"><option%s>file</option><option%s>http</option><option%s>ftp</option><option%s>scp</option></select></td>
			</tr>
			<tr>
				<td valign="top">Host:</td>
				<td><input type="text" name="host" size="30" value="%s"><br>or choose a mirror:<br><select name="mirror" onchange="document.uri.submit()"><option value=""> - </option>%s</select></td>
			</tr>
			<tr>
				<td>Username:</td>
				<td><input type="text" name="username" size="15" value="%s"></td>
			</tr>
			<tr>
				<td>Password:</td>
				<td><input type="text" name="password" size="15" value="%s"></td>
			</tr>
			<tr>
				<td>Port:</td>
				<td><input type="text" name="port" size="5" value="%s"></td>
			</tr>
			<tr>
				<td>Path:</td>
				<td><input type="text" name="path" size="30" value="%s"></td>
			</tr>
			<tr>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
			</tr>
			<tr>
				<td colspan="2"><input type="button" value="Cancel" onclick="window.close();"> &nbsp; <input type="button" value="Refresh" onclick="refresh_uri()"></td>
			</tr>
			<tr>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
			</tr>
		</table>
		<table>""" % (formfield, self.get_params['screen'], self.get_params['screen'], self.get_params['screen'], uri, self.get_params['screen'], uritypes['file'], uritypes['http'], uritypes['ftp'], uritypes['scp'], uriparts[3], mirrorlist, uriparts[1], uriparts[2], uriparts[4], uriparts[5])
		if not uri.endswith("/"):
			uri = uri[:uri.rfind("/")+1]
		try:
			filelist = GLIUtility.get_directory_listing_from_uri(uri)
		except:
			filelist = ["There was an error loading the directory list"]
		for listing in filelist:
			content += "	<tr>\n		<td>"
			if listing.endswith('/'):
				content += '<img src="../folder.gif">'
			else:
				content += '&nbsp;'
			content += '</td>\n		 <td><a href="#" onclick="'
			if listing.endswith('/'):
				listing = listing[:-1]
				if listing == "..":
					tmpuri = uri[:uri[:-1].rfind("/")+1]
				else:
					tmpuri = uri + listing + "/"
				content += "browse_uri('%s')" % tmpuri
			else:
				content += "select_uri('%s')" % listing
			content += "; return false\">%s</a></td>\n	</tr>\n" % listing

		return content
	
	def handle(self, path):
		if not self.shared_info.install_profile:
			self.shared_info.install_profile = GLIInstallProfile.InstallProfile()
		if not self.shared_info.client_profile:
			self.shared_info.client_profile = GLIClientConfiguration.ClientConfiguration()
		paths = { '/webgli': self.showwelcome,
					'/webgli/': self.showwelcome,
					'/webgli/ClientConfig': self.clientconfig,
					'/webgli/saveclientconfig': self.saveclientconfig,
					'/webgli/NetworkMounts': self.networkmounts,
					'/webgli/savenetmounts': self.savenetmounts,
					'/webgli/StageSelection': self.stageselection,
					'/webgli/savestage': self.savestage,
					'/webgli/PortageTree': self.portagetree,
					'/webgli/Partitioning': self.partitioning,
					'/webgli/Partitioning2': self.partitioning2,
					'/webgli/Partitioning3': self.partitioning3,
					'/webgli/Partitioning4': self.partitioning4,
					'/webgli/saveportage': self.saveportage,
					'/webgli/GlobalUSE': self.globaluse,
					'/webgli/saveglobaluse': self.saveglobaluse,
					'/webgli/LocalUSE': self.localuse,
					'/webgli/savelocaluse': self.savelocaluse,
					'/webgli/ConfigFiles': self.configfiles,
					'/webgli/saveconfigfiles': self.saveconfigfiles,
					'/webgli/Kernel': self.kernel,
					'/webgli/savekernel': self.savekernel,
					'/webgli/Bootloader': self.bootloader,
					'/webgli/savebootloader': self.savebootloader,
					'/webgli/Timezone': self.timezone,
					'/webgli/savetimezone': self.savetimezone,
					'/webgli/Networking': self.networking,
					'/webgli/savenetworking': self.savenetworking,
					'/webgli/Daemons': self.daemons,
					'/webgli/savedaemons': self.savedaemons,
					'/webgli/ExtraPackages': self.extrapackages,
					'/webgli/savepackages': self.savepackages,
					'/webgli/Services': self.services,
					'/webgli/saveservices': self.saveservices,
					'/webgli/Users': self.users,
					'/webgli/saveusers': self.saveusers,
					'/webgli/Review': self.review,
					'/webgli/savereview': self.savereview,
					'/webgli/URIBrowser': self.uribrowser,
					
					'/webgli/loadprofile': self.loadprofile,
					'/webgli/loadprofile2': self.loadprofile2,
							'/webgli/saveprofile': self.saveprofile,
							'/webgli/saveprofile2': self.saveprofile2
						}
		return_content = paths[path]()
		return self.headers_out, return_content

	def get_exception(self):
		etype, value, tb = sys.exc_info()
		s = traceback.format_exception(etype, value, tb)
		content = "<pre>"
		for line in s:
			content += line
		content += "</pre>"
		return content
