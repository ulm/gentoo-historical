"""
Gentoo Linux Installer

Copyright 2004 Gentoo Technologies Inc.

The GLIUtility module contians all utility functions used throughout GLI.
"""

import string
import os
import re

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
	expr = re.compile('^[\w\.\-\/]+$')

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
	valid_uri_types = ( 'ftp:', 'rsync:', 'http:', 'file:' )
		
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
	if uri.split('/')[0] in ('ftp:', 'rsync:', 'http:' ):
		
		# Check for hostname or ip address
		if (not _is_hostname(uri.split('/')[2])) and (not _is_ip(uri.split('/')[2])):
			return False
		
		# Check to make sure the rest is a propper path
		if not _is_path(string.join(uri.split('/')[3:], '/')):
			return False

	# If we are dealing with a local uri
	else:
		# Check for file validity
		if not _is_file(uri[colon_location + 3:]):
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
