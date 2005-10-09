#<?
def show_client_config():

	import GLIUtility
	import platform
	data = ""
	data += "<h2>Client Config</h2>\n"
	data += '<form name="CConfig" action="webgli.php?page=Partitioning" method="post">\n'
	
	data += '<table border="2"><tr><td>\n'
	#Choose the architecture for the Install.
	subarches = { 'i386': 'x86', 'i486': 'x86', 'i586': 'x86', 'i686': 'x86', 'x86_64': 'amd64', 'parisc': 'hppa' }
	arch = platform.machine()
	if arch in subarches: 
		arch = subarches[arch]
		
	data += "Arch selection string here.<br>\n"
	#checked=\"checked\" if arch=found_arch
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
		#device_list = GLIUtility.get_eth_devices()
		data += "DEVICE SELECTION OR DETECTION HERE!! <br>"
		data += '<select name="Network Type" size="3">'
		data += '<option value="dhcp">DHCP</option>'
		data += '<option value="static">Manual Config</option>'
		data += '<option value="None">None (Networkless)</option>'
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
	data += 'Additional Modules to Load (space-separated list): <input type="text" length="80" maxlength="80" value=""><br>'
	
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
	return data
#?>
