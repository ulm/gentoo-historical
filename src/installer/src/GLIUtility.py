"""
Gentoo Linux Installer

Copyright 2004 Gentoo Technologies Inc.

The GLIUtility module contians all utility functions used throughout GLI.
"""

import string, os, re, signal, time, shutil, sys, random, commands
from GLIException import *

def is_realstring(string_a):
	"Check to see if a string is actually a string, and if it is not null. Returns bool."
	# Make sure it is a string
	if type(string_a) != str:
		return False
		
	# Make sure it isn't null
	if type(string_a) == '':
		return False
	
	return True

def is_ip(ip):
	"Check to see if a string is a valid ip. Returns bool."
	
	# Make sure it is a string
	if not is_realstring(ip):
		return False

	# Compile the regular expression that validates an IP. It will also check for valid ranges.
	expr = re.compile('(([0-9]|[01]?[0-9]{2}|2([0-4][0-9]|5[0-5]))\.){3}([0-9]|[01]?[0-9]{2}|2([0-4][0-9]|5[0-5]))$')

	# Run the test.
	res = expr.match(ip)

	# Return True only if there are results.
	return(res != None)
		
def trim_ip(ip):
        # Remove leading zero's on the first octet
	ip = re.sub('^0{1,2}','',ip)

	# Remove leading zero's from the other octets
	res = re.sub('((?<=\.)(00|0)(?P<num>\d))','\g<num>',ip)

	return(res)

def is_device(device):
	"Check to see if the string passed is a valid device. Returns bool."

	# Make sure it is a string
	if not is_realstring(device):
		return False
			
	# Make sure the string starts with /dev/
	if device[0:5] != '/dev/':
		return False
			
	# Check to make sure the device exists
	return os.access(device, os.F_OK)
		
def is_hostname(hostname):
	"Check to see if the string is a valid hostname. Returns bool."

	# Make sure it is a string
	if not is_realstring(hostname):
		return False
			
	expr = re.compile('^([a-zA-Z0-9-_\.])+\.[a-zA-Z]{2,4}$')
	res = expr.match(hostname)

	return(res != None)
		
def is_path(path):
	"Check to see if the string is a valid path. Returns bool."
	
	# Make sure it is a string
	if not is_realstring(path):
		return False

	# Create a regular expression that matches all words and the symbols '-_./' _ is included in the \w
	expr = re.compile('^[\w\.\-\/~]+$')

	# Run the match
	res = expr.match(path)

	# Return True only if there are results
	return(res != None)
		
def is_file(file):
	"Check to see if the string is a valid file. Returns bool."

	# Make sure it is a string
	if not is_realstring(file):
		return False
			
	# Check to make sure the device exists
	return os.access(file, os.F_OK)
		
def is_uri(uri):
	"Check to see if the string is a valid URI. Returns bool."
	
	# Make sure it is a string
	if not is_realstring(uri):
		return False
			
	# Set the valid uri types
	valid_uri_types = ( 'ftp:', 'rsync:', 'http:', 'file:', 'https:')
		
	# Check colon and double slash location
	colon_location = uri.find(':')
	if not ( 6 > colon_location > 2):
		return False
	if uri[colon_location + 1:colon_location + 3] != "//":
		return False
		
	# Check for valid uri type
	if not uri.split('/')[0] in valid_uri_types:
		return False
		
	# If we are dealing with a network uri...
	if uri.split('/')[0] in ('ftp:', 'rsync:', 'http:', 'https:' ):
		
		# Check for hostname or ip address
		if (not is_hostname(uri.split('/')[2])) and (not is_ip(uri.split('/')[2])):
			return False
		
		# Check to make sure the rest is a propper path
		if not is_path(string.join(uri.split('/')[3:], '/')):
			return False

	# If we are dealing with a local uri
	else:
		# Check for file validity
		if not is_file(uri[colon_location + 3:]):
			return False
				
		
	return True

def strtobool(input):
	if type(input) != str:
		raise InputError('fatal','strtobool',"The input must be a string!")

	if string.lower(input) == 'true':
		return True
	else:
		return False

def is_eth_device(device):
	"Check to see if device is a valid ethernet device. Returns bool."
	
	# Make sure it is a string
	if not is_realstring(device):
		return False

	# Create a regular expression to test the specified device.
	expr = re.compile('^(eth|wlan|ppp)([0-9]{1,2})(:[0-9]{1,2})?$')

	# Run the match
	res = expr.match(device)

	# Return True only if there are results
	return(res != None)

def is_nfs(device):
	" Checks to see if device is a valid NFS device "

	if not is_realstring(device):
		return False

	colon_location = device.find(':')

	if colon_location == -1:
		return False

	host = device[:colon_location]
	path = device[colon_location+1:]

	return((is_ip(host) or is_hostname(host)) and is_path(path))

def set_ip(dev, ip, broadcast, netmask):
	if not is_ip(ip) or not is_ip(netmask) or not is_ip(broadcast):
		raise IPAddressError('fatal','set_ip', "ip, netmask and broadcast must be a valid IP's!")

	if not is_eth_device(dev):
		raise EthDeviceError('fatal','set_ip',"dev must be a valid ethernet device!")

	options = "%s inet %s broadcast %s netmask %s" % (dev, ip, broadcast, netmask)

	status = spawn("ifconfig " + options, quiet=True)

	if not exitsuccess(status):
		return False

	return True

def set_default_route(route):
	if not is_ip(route):
		raise IPAddressError('fatal', 'set_default_route', "The default route must be an IP address!")

	status = spawn("route add default gw " + route, quiet=True)

	if not exitsuccess(status):
		return False

	return True

def spawn(cmd, quiet=False, logfile=None, display_on_tty8=False, chroot=None, append_log=False, return_output=False):
	pid = os.fork()
	cmd_output = None
	if pid == 0:
		if chroot != None:
			cmd = "chroot " + chroot + " " + cmd

		if quiet and logfile != None:
			cmd += " >> " + logfile + " 2>&1"
		elif quiet and logfile == None:
			cmd += " >/dev/null 2>&1"
		elif logfile != None:
			if append_log:
				cmd += " | tee " + logfile
			else:
				cmd += " | tee -a " + logfile
		if return_output:
			cmd += " | tee /tmp/toreturn.log"

		if display_on_tty8:
			try:
				tty = os.open("/dev/vc/8", os.O_RDWR)
				oldstdout = sys.stdout
				oldstderr = sys.stderr
				os.dup2(tty,sys.stdout.fileno())
				os.dup2(tty,sys.stderr.fileno())
			except OSError:
				print "Could not open on tty8. Are you running as root?"
				tty = None

		os.execv('/bin/bash',['/bin/bash', '-c', cmd])
		sys.exit(1) # Should never be reached.

	ret = os.waitpid(pid,0)[1]
	if return_output:
		cmd_output = commands.getoutput("cat /tmp/toreturn.log")
		commands.system("rm /tmp/toreturn.log")
		return ret, cmd_output
	else:
		return ret

def exitsuccess(status):
	if os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0:
		return True

	return False

def spawn_bash():
	os.putenv("PROMPT_COMMAND","echo \"Type 'exit' to return to the installer.\"")
	return spawn("bash")

def get_uri(uri, path):
	uri = uri.strip()
	status = 1

	if re.match('^(ftp|http(s)?)://',uri):
		status = spawn("wget --quiet " + uri + " -O " + path)

	elif re.match('^rsync://', uri):
		status = spawn("rsync --quiet " + uri + " " + path)

	elif re.match('^file://', uri):
		file = uri[7:]
		if os.path.isfile(file):
			shutil.copy(file, path)
			if os.path.isfile(path):
				status = 0
			else:
				status = 1
	else:
		# Just in case a person forgets file://
		if os.path.isfile(uri):
			shutil.copy(uri, path)
			if os.path.isfile(path):
				status = 0
			else:
				status = 1
		else:
			print "I don't know how to download/copy that profile!"

	if exitsuccess(status):
		return True
	
	return False

def test_network(host):
	status = spawn("ping -c 3 " + host,quiet=True)

	if not exitsuccess(status):
		return False

	return True

def fetch_and_unpack_tarball(tarball_uri, target_directory, temp_directory="/tmp", keep_permissions=False):
	"Fetches a tarball from tarball_uri and extracts it into target_directory"

	# Get tarball info
	tarball_filename = tarball_uri.split("/")[-1]

	# Get the tarball
	get_uri(tarball_uri, temp_directory + "/" + tarball_filename)

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
	exitstatus = spawn("tar -" + tar_options + " -f " + temp_directory + "/" + tarball_filename + " -C " + target_directory, display_on_tty8=True)

	if not exitsuccess(exitstatus):
		raise UnpackTarballError('fatal', 'fetch_and_unpack_tarball',"Could not unpack tarball!")

def emerge(package, binary=False, binary_only=False):
	if binary_only:
		return spawn("emerge -K " + package, display_on_tty8=True)
	elif binary:
		return spawn("emerge -k " + package, display_on_tty8=True)
	else:
		return spawn("emerge " + package, display_on_tty8=True)

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

def edit_config(filename, newvalues, delimeter='=', quotes_around_value=True):
	"""
	filename = file to be editted
	newvlaues = a dictionary of VARIABLE:VALUE pairs
	"""
	if not os.path.isfile(filename):
		raise NoSuchFileError('notice','edit_config',filename + ' does not exist!')

	f = open(filename)
	file = f.readlines()
	f.close()

	for key in newvalues.keys():
		regexpr = '^\s*#?\s*' + key + '\s*' + delimeter + '.*$'
		regexpr = re.compile(regexpr)

		for i in range(0, len(file)):
			if regexpr.match(file[i]):
				if not file[i][0] == '#':
					file[i] = '#' + file[i]

		file.append('\n# Added by GLI\n')
		if quotes_around_value:
			file.append(key + delimeter + '"' + newvalues[key] + '"\n')
		else:
			file.append(key + delimeter + newvalues[key]+'\n')

	f = open(filename,'w')
	f.writelines(file)
	f.flush()
	f.close()
