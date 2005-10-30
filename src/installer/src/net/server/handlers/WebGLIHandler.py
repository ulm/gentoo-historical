import GLIServerProfile
import GLIInstallProfile
import GLIClientConfiguration
import GLIUtility
import handler
import sys
import copy
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
		
		#Set root password  THIS MAY NOT BE NECESSARY - SEE REMOTE SCRIPT
		data += "<hr>Root password selection string here. <br>"
		data += 'Enter Password:<input name="RootPass1" type="password" length="80" maxlength="80" value=""><br>'
		data += 'Re-enter Password to verify:<input name="RootPass2" type="password" length="80" maxlength="80" value=""><br>'
		
		#Modules to load now.
		#status, output = GLIUtility.spawn("lsmod", return_output=True)
		data += "<hr>Loaded modules list here. <br>"
		data += 'Additional Modules to Load (space-separated list): <input name="Modules" type="text" length="80" maxlength="80" value=""><br>'
		
		#Save Client Configuration File.  THIS SHOULD BE A POPUP
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
				data += "Profile saved successfully.  Here it is <BR><pre>" + self.shared_info.client_profile.serialize() + "</pre><br>\n"
			except:
				data += "ERROR: Could not save the profile!<BR>\n"
		return self.wrap_in_webgli_template(data)
	def loadprofile2(self):
		content = "<h2>Load Profile</h2>"
		xmlfile = ""
		if 'localfile' in self.post_params and self.post_params['localfile']:
			xmlfile = self.post_params['localfile']
		elif 'uploadfile' in self.post_params and self.post_params['uploadfile']:
			try:
				tmpfile = open("/tmp/serverprofile.xml", "w")
				tmpfile.write(self.post_params['uploadfile'])
				tmpfile.close()
				xmlfile = "/tmp/serverprofile.xml"
			except:
				content += "There was a problem writing the temp file for the file you uploaded" + self.get_exception()
				return self.wrap_in_template(content)
		else:
			content += "You did not specify a file to load"
			return self.wrap_in_template(content)
		cp = GLIServerProfile.ServerProfile()
		try:
			cp.parse(xmlfile)
		except:
			content += "There was an error parsing the XML file" + self.get_exception()
			return self.wrap_in_template(content)
		self.shared_info.clients = cp.get_clients()
		self.shared_info.profiles = cp.get_profiles()
		content += "Profile loaded successfully"
		return self.wrap_in_webgli_template(content)

	def saveprofile(self):
		content = """
		<h2>Save Profile</h2>
		<br>
		<form action="/saveprofile2" method="POST" enctype="multipart/form-data">
		Save to local (to server) file: <input type="text" name="localfile"> <input type="submit" value="Save"><br>
		or<br>
		Download the file: <input type="submit" name="download" value="Download">
		</form>
		"""
		return self.wrap_in_template(content)

	def saveprofile2(self):
		content = "<h2>Save Profile</h2>"
		cp = GLIServerProfile.ServerProfile()
		cp.set_clients(None, self.shared_info.clients, None)
		cp.set_profiles(None, self.shared_info.profiles, None)
		if not 'download' in self.post_params and self.post_params['localfile']:
			try:
				tmpfile = open(self.post_params['localfile'], "w")
				tmpfile.write(cp.serialize())
				tmpfile.close()
			except:
				content += "There was a problem writing the file" + self.get_exception()
				return self.wrap_in_template(content)
			return self.wrap_in_template(content + "Profile saved successfully")
		elif 'download' in self.post_params:
			self.headers_out.append(("Content-type", "text/xml"))
			self.headers_out.append(('Content-disposition', "attatchment;filename=serverprofile.xml"))
			return cp.serialize()
		else:
			return self.wrap_in_template(content + "You didn't specify a filename to save to")
	def showwelcome(self):
		data = "Welcoming string here.<BR>LOCAL INSTALL ASSUMED FOR THIS FRONT END<br>\n"
		return self.wrap_in_webgli_template(data)
	def partitioning(self):
		data = ""
		return self.wrap_in_webgli_template(data)
	def savepartitions(self):
		data = ""
		return self.wrap_in_webgli_template(data)
	def networkmounts(self):
		data = "Network Mounts page."
		network_mounts = copy.deepcopy(self.shared_info.install_profile.get_network_mounts())
		
		#	data += "Network Mount found: " + netmount['host'] + ":" + netmount['export'] + "<br>\n"
		data += "If you have any network shares you would like to mount during the install and for your new system, define them here. Select a network mount to edit or add a new mount.  Currently GLI only supports NFS mounts."
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
		data += '>1</td><td>Stage1 is used when you want to bootstrap&amp;build from scratch.</td></tr><tr>      <td><input name="stage" type="radio" value="2"'
		if stage == 2:
			data += ' checked'
		data += '>2</td><td>Stage2 is used for building from a bootstrapped semi-compiled state.</td></tr><tr>      <td><input name="stage" type="radio" value="3"'
		if (stage == 3) and not grp_install:
			data += ' checked'
		data += '>3</td><td>Stage3 is a basic system that has been built for you (no compiling).</td></tr><tr>      <td><input name="stage" type="radio" value="3+GRP"'
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
		data += '>Webrsync</td><td>HTTP daily snapshot. Use when rsync is firewalled.</td></tr><tr>     <td><input name="portagetype" type="radio" value="snapshot"'
		if synctype == "snapshot":
			data += "checked"
		data += '>Snapshot</td><td>Use a portage snapshot, either a local file or a URL</td></tr><tr>      <td><input name="portagetype" type="radio" value="none"'
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
		data += '<h3>Global USE Flags:</h3><table width="100%"  border="1"><tr><th scope="col">Active</th><th scope="col">Flag</th><th scope="col">Description</th></tr>'+"\n"
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
		data += ">Gentoo</td><td>Gentoo's optimized 2.6+ kernel. (less safe) </td>    </tr>\n"+'<tr><td><input name="sources" type="radio" value="hardened-sources" '
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
<table width="507"  border="1">
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
		boot_loaders.append(("none", (u"Do not install a bootloader.  (System may be unbootable!)")))
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
		data = ""
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
			#The CC has a network config that's not already there.  Preload it.
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
		  location.replace('/webgli/Networking?editiface=' + document.Networking.EditIface.value);
		}
		</script>
		 <p>Devices:</p>
		 <form name="Networking" method="post" action="/webgli/savenetworking" enctype="multipart/form-data">
		   <table width="100%"  border="1">
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
			data += '<input type="submit" value="Add Network Device" name="AddIfaceSubmit">'
		
		data += 'Enter your default gateway: <input name="gateway" type="text" length="50" maxlength="15" value=".1"><br>'
		data += 'Enter a DNS server: <input name="dnsserver" type="text" length="50" maxlength="15" value="128.118.25.3">'
		data += """   <p>Wireless stuff here. ESSID: Key:  </p>
		   <p>Hostname:
			 <input name="hostname" type="text" id="hostname">
		   </p>
		   <p>Domainname:
			 <input name="domainname" type="text" id="domainname">
		   </p>
		   <p>NIS Domainname: 
			 <input name="nisdomainname" type="text" id="nisdomainname"> 
		   </p>
		   <p>more</p>
		   <p>DNS Servers (separate by space): 
			 <input name="dnsservers" type="text" id="dnsservers">
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
				except:
					data += "ERROR: Could not delete the interface.<BR>\n"	
			else:
				data += "ERROR: No device selected to delete!<br>\n"
			
		if 'dnsserver' in self.post_params:
			data += "Found an DNS server: you submitted " + self.post_params['dnsserver'] + "<BR>\n"
			try:
				self.shared_info.client_profile.set_dns_servers(None, self.post_params['dnsserver'], None)
			except:
				data += "ERROR: Could not set the DNS Server<BR>\n"
				
		return self.wrap_in_webgli_template(data)
	def daemons(self):
		data = ""
		return self.wrap_in_webgli_template(data)
	def savedaemons(self):
		data = ""
		return self.wrap_in_webgli_template(data)
	def extrapackages(self):
		data = ""
		return self.wrap_in_webgli_template(data)
	def savepackages(self):
		data = ""
		return self.wrap_in_webgli_template(data)
	def users(self):
		data = ""
		return self.wrap_in_webgli_template(data)
	def saveusers(self):
		data = ""
		return self.wrap_in_webgli_template(data)
	def review(self):
		data = ""
		return self.wrap_in_webgli_template(data)
	def savereview(self):
		data = ""
		return self.wrap_in_webgli_template(data)

	def uribrowser(self):
		formfields = {  'portage': "opener.document.portage.snapshoturi", 
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
			content += "  <tr>\n    <td>"
			if listing.endswith('/'):
				content += '<img src="../folder.gif">'
			else:
				content += '&nbsp;'
			content += '</td>\n    <td><a href="#" onclick="'
			if listing.endswith('/'):
				listing = listing[:-1]
				if listing == "..":
					tmpuri = uri[:uri[:-1].rfind("/")+1]
				else:
					tmpuri = uri + listing + "/"
				content += "browse_uri('%s')" % tmpuri
			else:
				content += "select_uri('%s')" % listing
			content += "; return false\">%s</a></td>\n  </tr>\n" % listing

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
				  '/webgli/savepartitions': self.savepartitions,
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
				  '/webgli/Users': self.users,
				  '/webgli/saveusers': self.saveusers,
				  '/webgli/Review': self.review,
				  '/webgli/savereview': self.savereview,
				  '/webgli/URIBrowser': self.uribrowser,
				  
		          '/loadprofile2': self.loadprofile2,
		          '/saveprofile': self.saveprofile,
		          '/saveprofile2': self.saveprofile2
		        }
		return_content = paths[path]()
		return self.headers_out, return_content
