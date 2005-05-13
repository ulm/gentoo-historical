"""
Gentoo Linux Installer
Copyright 2005 Gentoo Technologies Inc.

The GLIUtility module contians all utility functions used throughout GLI.
"""

import string, os, re, shutil, sys, random, commands, crypt
from GLIException import *

##
# Check to see if a string is actually a string, and if it is not null. Returns bool.
# @param string_a    string to be checked.
def is_realstring(string):
	# Make sure it is a string
	if not isinstance(string, (str, unicode)):
		return False
		
	return True

##
# Checks to see if x is a numeral by doing a type conversion.
# @param x   value to be checked
def is_numeric(x):
	try:
		float(x)
	except ValueError:
		return False
	else:
		return True

##
# Check to see if a string is a valid ip. Returns bool.
# @param ip 	ip to be checked.
def is_ip(ip):
	# Make sure it is a string
	if not is_realstring(ip):
		return False

	# Compile the regular expression that validates an IP. It will also check for valid ranges.
	expr = re.compile('(([0-9]|[01]?[0-9]{2}|2([0-4][0-9]|5[0-5]))\.){3}([0-9]|[01]?[0-9]{2}|2([0-4][0-9]|5[0-5]))$')

	# Run the test.
	res = expr.match(ip)

	# Return True only if there are results.
	return(res != None)

##
# Check to see if mac is a valid MAC address. Make sure use format_mac
# before using this function. Returns bool.
# @param mac   mac address to be checked.
def is_mac(mac):
        expr = re.compile('([0-9A-F]{2}:){5}[0-9A-F]{2}')
        res = expr.match(mac)
        return(res != None)

##
# Format's a mac address properly. Returns the correctly formatted MAC. (a string)
# @param mac   mac address to be formatted
def format_mac(mac):
	mac = string.replace(mac, '-', ':')
	mac = string.upper(mac)

	mac = string.split(mac, ':')
	for i in range(0, len(mac)):
		if len(mac[i]) < 2:
			mac[i] = "0" + mac[i]
	return string.join(mac, ":")

##
# FIXME: UNKNOWN
# @param ip Parameter description
def trim_ip(ip):
    # Remove leading zero's on the first octet
	ip = re.sub('^0{1,2}','',ip)

	# Remove leading zero's from the other octets
	res = re.sub('((?<=\.)(00|0)(?P<num>\d))','\g<num>',ip)

	return(res)

##
# Check to see if the string passed is a valid device. Returns bool.
# @param device    device to be checked
def is_device(device):
	# Make sure it is a string
	if not is_realstring(device):
		return False
			
	# Make sure the string starts with /dev/
	if device[0:5] != '/dev/':
		return False
			
	# Check to make sure the device exists
	return os.access(device, os.F_OK)
		
##
# Check to see if the string is a valid hostname. Returns bool.
# @param hostname   host to be checked
def is_hostname(hostname):
	# Make sure it is a string
	if not is_realstring(hostname):
		return False
			
	expr = re.compile('^([a-zA-Z0-9-_\.])+\.[a-zA-Z]{2,4}$')
	res = expr.match(hostname)

	return(res != None)
		
##
# Check to see if the string is a valid path. Returns bool.
# @param path 	Path to be checked.
def is_path(path):
	# Make sure it is a string
	if not is_realstring(path):
		return False

	# Create a regular expression that matches all words and the symbols '-_./' _ is included in the \w
	expr = re.compile('^[\w\.\-\/~]+$')

	# Run the match
	res = expr.match(path)

	# Return True only if there are results
	return(res != None)
		
##
# Check to see if the string is a valid file. Returns bool.
# @param file  file to be checked for validity.
def is_file(file):
	# Make sure it is a string
	if not is_realstring(file):
		return False
			
	# Check to make sure the device exists
	return os.access(file, os.F_OK)
		
##
# Check to see if the string is a valid URI. Returns bool.
# @param uri 				URI to be validated
# @param checklocal=True	Whether to look for a local uri.
def is_uri(uri, checklocal=True):
	# Make sure it is a string
	if not is_realstring(uri):
		return False
			
	# Set the valid uri types
	valid_uri_types = ('ftp', 'rsync', 'http', 'file', 'https')
		
	# Compile the regex
	expr = re.compile('(\w+)://(?:(\w+)(?::(\w+))?@)?(?:([\w.]+)(?::(\d+))?)?(/.+)')

	# Run it against the URI
	res = expr.match(uri)

	if not res:
		# URI doesn't match regex and therefore is invalid
		return False

	# Get tuple of matches
	# 0 - Protocol
	# 1 - Username
	# 2 - Password
	# 3 - Host
	# 4 - Port
	# 5 - Path
	uriparts = res.groups()
    
	# Check for valid uri type
	if not uriparts[0] in valid_uri_types:
		return False
		
	# If checklocal and the URI is a local file, check to see if the file exists
	if uriparts[0] == "file" and checklocal:
		if not is_file(uriparts[5]):
			return False
		
	return True

##
# Converts a string to a boolean value. anything not "True" is deemed false.
# @param input  must be a string so it can be converted to boolean.
def strtobool(input):
	if type(input) != str:
		raise GLIException("GLIUtilityError", 'fatal','strtobool',"The input must be a string!")

	if string.lower(input) == 'true':
		return True
	else:
		return False

##
# Check to see if device is a valid ethernet device. Returns bool.
# @param device  device to be checked
def is_eth_device(device):
	# Make sure it is a string
	if not is_realstring(device):
		return False

	# Old way w/ reg ex here:
	# Create a regular expression to test the specified device.
	#expr = re.compile('^(eth|wlan|ppp)([0-9]{1,2})(:[0-9]{1,2})?$')
	# Run the match
	#res = expr.match(device)
	# Return True only if there are results
	#return(res != None)

	status, output = spawn("/sbin/ifconfig -a | grep -e '^[A-Za-z]'| cut -d ' ' -f 1 | grep '"+ device + "'", return_output=True)
	if output:
		return True
	return False
	
##
# Checks to see if device is a valid NFS device
# @param device 	device to be checked
def is_nfs(device):
	if not is_realstring(device):
		return False

	colon_location = device.find(':')

	if colon_location == -1:
		return False

	host = device[:colon_location]
	path = device[colon_location+1:]

	return((is_ip(host) or is_hostname(host)) and is_path(path))

##
# Sets the network ip (used for the livecd environment)
# @param dev 		device to be configured
# @param ip 		ip address of device
# @param broadcast 	broadcast address of device
# @param netmask 	netmask address of device
def set_ip(dev, ip, broadcast, netmask):
	if not is_ip(ip) or not is_ip(netmask) or not is_ip(broadcast):
		raise GLIException("GLIUtilityError", 'fatal','set_ip', ip + ", " + netmask + "and, " + broadcast + "must be a valid IP's!")
	if not is_eth_device(dev):
		raise GLIException("GLIUtilityError", 'fatal','set_ip', dev + "is not a valid ethernet device!")

	options = "%s inet %s broadcast %s netmask %s" % (dev, ip, broadcast, netmask)

	status = spawn("ifconfig " + options)

	if not exitsuccess(status):
		return False

	return True

##
# Sets the default route (used for the livecd environment)
# @param route  	ip addresss of gateway.
def set_default_route(route):
	if not is_ip(route):
		raise GLIException("GLIUtilityError", 'fatal', 'set_default_route', route + " is not an ip address!")
	status = spawn("route add default gw " + route)

	if not exitsuccess(status):
		return False

	return True

##
# Will run a command with various flags for the style of output and logging.
# 
# @param cmd 					The command to be run
# @param quiet=False 			Whether or not to filter output to /dev/null
# @param logfile=None 			if provied will log output to the given filename
# @param display_on_tty8=False 	will output to tty8 instead of the screen.
# @param chroot=None 			will run the command inside the new chroot env.
# @param append_log=False 		whether to start over on the logfile or append.
# @param return_output=False 	Returns the output along with the exit status
def spawn(cmd, quiet=False, logfile=None, display_on_tty8=False, chroot=None, append_log=False, return_output=False):
	# quiet and return_output really do the same thing. One of them need to be removed.
	if chroot != None:
		wrapper = open(chroot+"/tmp/spawn.sh", "w")
		wrapper.write("#!/bin/bash\n\nsource /etc/profile\n" + cmd)
		wrapper.close()
#		print "running '" + cmd + "' in chroot " + chroot
		cmd = "chmod a+x " + chroot + "/tmp/spawn.sh && chroot " + chroot + " /tmp/spawn.sh 2>&1"
	else:
		cmd += " 2>&1 "
	if logfile != None:
		if append_log:
			cmd += " | tee -a " + logfile
		else:
			cmd += " | tee " + logfile

	if display_on_tty8:
		cmd += " | tee /dev/tty8"

#	print "Running command: " + cmd
	ret, output = commands.getstatusoutput(cmd)
	
	if return_output:
		return ret, output
	else:
		return ret

##
# Will check the status of a spawn result to see if it did indeed return successfully.
# @param status Parameter description
def exitsuccess(status):
	if os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0:
		return True
	#print "WIFEXITED = " + str(os.WIFEXITED(status)) + ", WEXITSTATUS = " + str(os.WEXITSTATUS(status))
	return False

##
# Will produce a bash shell with a special prompt for the installer.
def spawn_bash():
	os.putenv("PROMPT_COMMAND","echo \"Type 'exit' to return to the installer.\"")
	status = spawn("bash")
	return status

##
# Will download or copy a file/uri to a location
# @param uri 	uri to be fetched.
# @param path 	destination for the file.
def get_uri(uri, path):
	uri = uri.strip()
	status = 0

	if re.match('^(ftp|http(s)?)://',uri):
		status = spawn("wget --quiet " + uri + " -O " + path)
		
	elif re.match('^rsync://', uri):
		status = spawn("rsync --quiet " + uri + " " + path)

	elif re.match('^file://', uri):
		r_file = uri[7:]
		if os.path.isfile(r_file):
			shutil.copy(r_file, path)
			if not os.path.isfile(path):
				raise GLIException("GLIUtilityError", 'fatal', 'get_uri', "Cannot copy " + r_file + " to " + path)
	else:
		# Just in case a person forgets file://
		if os.path.isfile(uri):
			shutil.copy(uri, path)
			if not os.path.isfile(path):
				raise GLIException("GLIUtilityError", 'fatal', 'get_uri', "Cannot copy " + r_file + " to " + path)
		else:
			raise GLIException("GLIUtilityError", 'fatal', 'get_uri', "File does not exist or URI is invalid!")

	if exitsuccess(status):
		return True
	
	return False

##
# Pings a host.  Used to test network connectivity.
# @param host 	host to be pinged.
def ping(host):
	host = str(host)
	if not (is_hostname(host) or is_ip(host)):
		return False    #invalid IP or hostname
	status = spawn("ping -n -c 3 " + host)
	if not exitsuccess(status):
		return False
	return True

##
# Pass in the eth device's number (0, 1, 2, etc).
# Returns network information in a tuple.
# Order is hw_addr, ip_addr, mask, bcast, route, and
# whether it's up (True or False).
# @param device 	device to gather info from.
def get_eth_info(device):
	"""Pass in the eth device's number (0, 1, 2, etc).
	Returns network information in a tuple.
	Order is hw_addr, ip_addr, mask, bcast, route, and
	whether it's up (True or False).
	"""
	
	hw_addr = 'None'
	ip_addr = 'None'
	mask    = 'None'
	bcast	= 'None'
	gw      = 'None'
	up      =  False
	
	if not is_eth_device("eth" + str(device)):
		raise GLIException("GLIUtilityError", 'fatal', "get_eth_info", "eth" + str(device) +" is not a valid ethernet device!")
		
	status, device_info = spawn("/sbin/ifconfig eth" + str(device), return_output=True)
	if exitsuccess(status):
		for line in device_info.splitlines():
			line = line.strip()
			if 'HWaddr' in line: 
				hw_addr = line.split('HWaddr',1)[1].strip()
			if 'inet addr' in line:
				ip_addr = line.split('  ')[0].split(':')[1]
			if 'Bcast' in line:
				bcast = line.split('  ')[1].split(':')[1]
			if 'Mask' in line:
				mask = line.split('  ')[2].split(':')[1]
			if line.startswith('UP'):
				up = True
	else:
		raise GLIException("GLIUtilityError", 'fatal', "get_eth_info", device_info)
	status, route_info = spawn("netstat -nr", return_output=True)
	for line in route_info[1].splitlines():
		if line.startswith('0.0.0.0'):
			gw = line.split('0.0.0.0')[1].strip()
	
	return (hw_addr, ip_addr, mask, bcast, gw, up)
	
##
# Will take a uri and get and unpack a tarball into the destination.
# @param tarball_uri 			URI of tarball
# @param target_directory 		destination
# @param temp_directory="/tmp" 	a temporary location (used for dealing with the 
#								ramdisk size limitations of the livecd env.
# @param keep_permissions=False Whether or not to keep permissions (-p)
def fetch_and_unpack_tarball(tarball_uri, target_directory, temp_directory="/tmp", keep_permissions=False):
	"Fetches a tarball from tarball_uri and extracts it into target_directory"

	# Get tarball info
	tarball_filename = tarball_uri.split("/")[-1]

	# Get the tarball
	if not get_uri(tarball_uri, temp_directory + "/" + tarball_filename):
		return False

	# Reset tar options
	tar_options = "xv"

	# If the tarball is bzip'd
	if tarball_filename.split(".")[-1] == "tbz" or  tarball_filename.split(".")[-1] == "bz2":
		tar_options = tar_options + "j"

	# If the tarball is gzip'd
	elif tarball_filename.split(".")[-1] == "tgz" or  tarball_filename.split(".")[-1] == "gz":
		tar_options = tar_options + "z"

	# If we want to keep permissions
	if keep_permissions:
		tar_options = tar_options + "p"

	# Unpack the tarball
	exitstatus = spawn("tar -" + tar_options + " -f " + temp_directory + "/" + tarball_filename + " -C " + target_directory, display_on_tty8=True, logfile="/tmp/compile_output.log", append_log=True) # change this to the logfile variable

	if not exitsuccess(exitstatus):
		raise GLIException("GLIUtilityError", 'fatal', 'fetch_and_unpack_tarball',"Could not unpack " + tarball_uri + " to " + target_directory)

##
# OLD Will generate a random password.  Used when the livecd didn't auto-scramble the root password.
# can probably be removed but is good to keep around.
def generate_random_password():
	s = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890$%^&*[]{}-=+_,|'\"<>:/"
	s = list(s)

	for i in range(0,len(s)/2):
		x = random.randint(0,len(s)-1)
		y = random.randint(0,len(s)-1)
		tmp = s[x]
		s[x] = s[y]
		s[y] = tmp

	passwd = ""
	for i in range(0,random.randint(8,12)):
		passwd += s[i]

	return passwd

##
# Will grab a value from a specified file after sourcing it
# @param filename 		file to get the value from
# @param value			value to look for
def get_value_from_config(filename, value):
	#OLD WAY: return string.strip(commands.getoutput("source " + filename + " && echo $" + value))
	status, output = spawn("source " + filename + " && echo $" + value, return_output=True)
	return string.strip(output)


##
# Will take a password and return it hashed in md5 format
# @param password 		the password to be hashed
def hash_password(password):
	salt = "$1$"
        chars = "./abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	for i in range(0, 8):
		salt += chars[random.randint(0, len(chars)-1)]
	salt += "$"
	passwd_hash = crypt.crypt(password, salt)

	return passwd_hash
