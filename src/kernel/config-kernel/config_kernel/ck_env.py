#
# Library of functions for dealing with the kernel config environment
#
# $Header: /var/cvsroot/gentoo/src/kernel/config-kernel/config_kernel/ck_env.py,v 1.3 2004/04/03 16:30:08 latexer Exp $

import sys, os
import string
from shutil import copy
from tempfile import gettempdir
from ck_display import *

envFile="05kernel"
envPrefix="/etc/env.d"

def setenv(varsNew):
	err, envVars = readEnvFile()
	if err:
		warn ("No previous variable definitions found")
		envVars={}

	for key in varsNew.keys():
		if key == "KBUILD_OUTPUT_PREFIX" and varsNew[key] == "none":
			envVars[key]=""
		elif varsNew[key]:
			envVars[key]=varsNew[key]
	
	tempEnv = os.path.join(gettempdir(), envFile)
	file = open(tempEnv, "w")
	info("Writing out changes to " + os.path.join(envPrefix,envFile))
	for key in envVars.keys():
		if envVars[key]:
			# Pad our variables with quotation marks if they need it
			if envVars[key][0] != '"':
				envVars[key] = '"' + envVars[key]
			if envVars[key][-1] != '"':
				envVars[key] = envVars[key] + '"'
			file.write(key + "=" + envVars[key] + "\n")
		else:
			file.write(key + "=\"\"\n")

	file.close()
	copy(tempEnv, os.path.join(envPrefix, envFile))
	info("Running env-update. You should run 'source /etc/profile' to update")
	info("your environment, or log out and in again.")
	envupdate()

# getenv(variable) queries the current value of a certain variable 
# in /etc/env.d/05kernel. Return a pair with the value, and any error
# that maybe encountered.
def getenv(variable):
	err, vars = readEnvFile()
	if err:
		return None, "Variable not found"

	if vars.has_key(variable):
		return (vars[variable], None)
	else:
		return (None, "Variable not found")

# readEnvFile() returns a dictionary of variables and their values from the env.d kernel file
def readEnvFile():
	vars = {}
	try:
		f = open(os.path.join(envPrefix,envFile), 'r')
	except OSError, details:
		return (str(details), None)
	except IOError, details:
		return (str(details), None)
	try:
		lines = f.readlines()
	except OSError, details:
		return (str(details), None)
	except IOError, details:
		return (str(details), None)

	f.close()
	
	lines = map(string.strip,lines)
	for line in lines:
		words = string.split(line, "=")
		words = map(string.strip,words)
		if words[-1] != words[0]:
			vars[words[0]] = words[1].strip("\"")

	return None, vars

def envupdate():
	fromchild, tochild, childerror = os.popen3("env-update")
	val = childerror.readline()
	if val:
		warn("Error updating the environment!")


# vim:ts=4:
