"""
Gentoo Linux Installer

Copyright 2004 Gentoo Technologies Inc.

The GLIUtility module contians all utility functions used throughout GLI.
"""

import string, os, re, signal, time, shutil

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
		raise "InputError", "The input must be a string!"

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
	expr = re.compile('^eth([0-9]{1,2})(:[0-9]{1,2})?$')

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
		raise "IPAddressError", "ip, netmask and broadcast must be a valid IP!"

	if not is_eth_device(dev):
		raise "EthDeviceError", "dev must be a valid ethernet device!"

	options = "%s inet %s broadcast %s netmask %s" % (dev, ip, broadcast, netmask)

	res = run_cmd("ifconfig",options)

	if res[0] == 'exit' and res[1] == 0:
		return(0)
	else:
		return(1)

def set_default_route(route):
	pass

def run_cmd(cmd, timeout=-1):
	if type(cmd) != str:
		raise "InputError", "cmd must be a string!"

	cmdline = []

	if len(cmd.split()) > 1:
		tmp = cmd.split()
		cmd = tmp[0]
		cmdline = tmp[1:]

	if len(cmdline) == 0 or cmdline[0] != cmd:
		cmdline = [cmd] + cmdline

	pid = os.fork()
	if pid == 0:
		os.execvp(cmd, cmdline)
	else:
		if timeout != -1:
			for i in range(0, timeout):
				status = os.waitpid(pid, os.WNOHANG)
				if status[0] != 0:
					break
				time.sleep(1)

			if status[0] == 0:
				os.kill(pid, signal.SIGTERM)

				for i in range(0, 5):
					status = os.waitpid(pid, os.WNOHANG)
					if status[0] != 0:
						break
					time.sleep(1)

				if status[0] == 0:
					os.kill(pid, signal.SIGKILL)
					status = os.waitpid(pid,0)


		else:
			status = os.waitpid(pid,0)

		# We're big kids, we can use os.W* when we need to see what happened.
		return(status[1])

def exitsuccess(status):
	if os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0:
		return True

	return False

def run_bash():
	os.putenv("PROMPT_COMMAND","echo \"Type 'exit' to return to the installer.\"")
	return run_cmd("bash")

def get_uri(uri, path):
	uri = uri.strip()
	status = 1

	if re.match('^(ftp|http(s)?)://',uri):
		status = run_cmd("wget --quiet " + uri + " -O " + path)

	elif re.match('^rsync://', uri):
		status = run_cmd("rsync --quiet " + uri + " " + path)

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
