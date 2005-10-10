import GLIServerProfile
import handler
import sys
import copy
sys.path.append("../..")
class WebGLIHandler(handler.Handler):

	def clientconfig(self):
		import GLIUtility
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
			
			data += "<br>DEVICE SELECTION OR DETECTION HERE!! <br>"
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
		import GLIClientConfiguration
		data = ""
		client_profile = GLIClientConfiguration.ClientConfiguration()
		
		if 'ArchType' in self.post_params:
			data += "Found an architecture:  you submitted " + self.post_params['ArchType']+ "<BR>\n"
			try:
				client_profile.set_architecture_template(None, self.post_params['ArchType'], None)
			except:
				data += "ERROR: Could not set the Architecture Template<br>\n"
		if 'Logfile' in self.post_params:
			data += "Found a logfile: you submitted " + self.post_params['Logfile'] + "<BR>\n"
			try:
				client_profile.set_log_file(None, self.post_params['Logfile'], None)
			except:
				data += "ERROR: Could not set the Logfile <BR>\n"
		if 'RootMountPoint' in self.post_params:
			data += "Found a root mount point: you submitted " + self.post_params['RootMountPoint'] + "<BR>\n"
			try:
				client_profile.set_root_mount_point(None, self.post_params['RootMountPoint'], None)
			except:
				data += "ERROR: Could not set the Root Mount Point<BR>\n"
		if 'Network_Iface' in self.post_params:
			data += "Found a network interface: you submitted " + self.post_params['Network_Iface'] + "<BR>\n"
			try:
				client_profile.set_network_interface(None, self.post_params['Network_Iface'], None)
			except:
				data += "ERROR: Could not set the Network Interface<BR>\n"
		if 'Network_Type' in self.post_params:
			data += "Found a Network Type: you submitted " + self.post_params['Network_Type'] + "<BR>\n"
			try:
				client_profile.set_network_type(None, self.post_params['Network_Type'], None)
			except:
				data += "ERROR: Could not set the Network Type<BR>\n"
		if 'ip' in self.post_params:
			data += "Found an IP: you submitted " + self.post_params['ip'] + "<BR>\n"
			try:
				client_profile.set_network_ip(None, self.post_params['ip'], None)
			except:
				data += "ERROR: Could not set the IP<BR>\n"
		if 'broadcast' in self.post_params:
			data += "Found an broadcast IP: you submitted " + self.post_params['broadcast'] + "<BR>\n"
			try:
				client_profile.set_network_broadcast(None, self.post_params['broadcast'], None)
			except:
				data += "ERROR: Could not set the broadcast IP<BR>\n"
		if 'netmask' in self.post_params:
			data += "Found an netmask IP: you submitted " + self.post_params['netmask'] + "<BR>\n"
			try:
				client_profile.set_network_netmask(None, self.post_params['netmask'], None)
			except:
				data += "ERROR: Could not set the netmask IP<BR>\n"
		if 'gateway' in self.post_params:
			data += "Found an gateway IP: you submitted " + self.post_params['gateway'] + "<BR>\n"
			try:
				client_profile.set_network_gateway(None, self.post_params['gateway'], None)
			except:
				data += "ERROR: Could not set the gateway IP<BR>\n"
		if 'dnsserver' in self.post_params:
			data += "Found an DNS server: you submitted " + self.post_params['dnsserver'] + "<BR>\n"
			try:
				client_profile.set_dns_servers(None, self.post_params['dnsserver'], None)
			except:
				data += "ERROR: Could not set the DNS Server<BR>\n"
		if 'EnableSSH' in self.post_params:
			data += "Found an Enable SSH Flag: you set it to " + self.post_params['EnableSSH'] + "<BR>\n"
			try:
				client_profile.set_enable_ssh(None, self.post_params['EnableSSH'], None)
			except:
				data += "ERROR: Could not set the SSH flag<BR>\n"
		if ('RootPass1' in self.post_params) and ('RootPass2' in self.post_params):
			data += "Found a root password1: you submitted " + self.post_params['RootPass1'] + "<BR>\n"
			data += "Found a root password2: you submitted " + self.post_params['RootPass2'] + "<BR>\n"
			if self.post_params['RootPass1'] == self.post_params['RootPass2']:
				try:
					client_profile.set_root_passwd(None, GLIUtility.hash_password(self.post_params['RootPass1']), None)
				except:
					data += "ERROR: Could not set the root password<BR>\n"
			else:
				data += "ERROR: Passwords DO NOT MATCH!<BR>\n"
		if 'Modules' in self.post_params:
			data += "Found an Additional Module: you submitted " + self.post_params['Modules'] + "<BR>\n"
			try:
				client_profile.set_kernel_modules(None, self.post_params['Modules'], None)
			except:
				data += "ERROR: Could not set the Kernel Modules<BR>\n"
		if 'SaveCCFile' in self.post_params:
			data += "Found a filename to save the Client Profile:" + self.post_params['SaveCCFile'] + "<BR>\n"
			try:
				configuration = open(self.post_params['SaveCCFile'] ,"w")
				configuration.write(client_profile.serialize())
				configuration.close()
				data += "Profile saved successfully.  Here it is <BR><pre>" + client_profile.serialize() + "</pre><br>\n"
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
	def networkmounts(self):
		data = "Network Mounts page."
		network_mounts = copy.deepcopy(self.shared_info.install_profile.get_network_mounts())
		for netmount in network_mounts:
			data += "Network Mount found: " + netmount['host'] + ":" + netmount['export'] + "<br>\n"
		data += "If you have any network shares you would like to mount during the install and for your new system, define them here. Select a network mount to edit or add a new mount.  Currently GLI only supports NFS mounts."
		data += """
		<form name="netmount" action="/webgli/savenetmounts" method="POST" enctype="multipart/form-data">
		
		"""
		
		return self.wrap_in_webgli_template(data)
		
	def handle(self, path):
		if not self.shared_info.install_profile:
			self.shared_info.install_profile = GLIInstallProfile.InstallProfile()
		paths = { '/webgli': self.showwelcome,
				  '/webgli/ClientConfig': self.clientconfig,
				  '/webgli/saveclientconfig': self.saveclientconfig,
				  '/webgli/NetworkMounts': self.networkmounts,
		          '/loadprofile2': self.loadprofile2,
		          '/saveprofile': self.saveprofile,
		          '/saveprofile2': self.saveprofile2
		        }
		return_content = paths[path]()
		return self.headers_out, return_content
