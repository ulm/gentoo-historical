"""
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
Gentoo Linux Installer

$Id: GLIServerProfile.py,v 1.2 2006/01/27 02:19:33 agaffney Exp $
Copyright 2005 Gentoo Technologies Inc.
"""

import string, re, GLIUtility, SimpleXMLParser, os.path
import xml.dom.minidom
from GLIException import *

class ServerProfile:

	##
	# Initializes the ClientConfiguration.
	def __init__(self):
		self._clients = []
		self._profiles = []
		self._tmp_clients = []
		self._tmp_profiles = []
		self.data = ""  # used for serialization

		self._parser = SimpleXMLParser.SimpleXMLParser()

		self._parser.addHandler('clients-profiles/profiles', self.set_profiles, call_on_null=True)
		self._parser.addHandler('clients-profiles/profiles/profile', self.add_profile, call_on_null=True)
		self._parser.addHandler('clients-profiles/clients', self.set_clients, call_on_null=True)
		self._parser.addHandler('clients-profiles/clients/client', self.add_client, call_on_null=True)
		
	##
	# Parses the given filename populating the client_configuration.
	# @param filename the file to be parsed.  This should be a URI actually.
	def parse(self, filename):
		self._parser.parse(filename)

	##
	# Serializes the Client Configuration into an XML format that is returned.
	def serialize(self):
#		fntable ={	'architecture-template': self.get_architecture_template,
#				}
		self.data = "<clients-profiles>"

#		for key in fntable.keys():
#			self.data += "<%s>%s</%s>" % (key, fntable[key](), key)

		# Serialize the special cases.
		self.serialize_profiles()
		self.serialize_clients()

		# Add closing tag
		self.data += "</clients-profiles>"
		
		#Finish by putting it all in nice XML.
		dom = xml.dom.minidom.parseString(self.data)
		return dom.toprettyxml()
		
	##
	# Sets the profiles
	# @param xml_path not used here.
	# @param architecture_template the architecture to be installed
	# @param xml_attr not used here.
	def set_profiles(self, xml_path, profiles, attr):
		if not profiles:
			self._profiles = self._tmp_profiles
			self._tmp_profiles = []
		else:
			self._profiles = profiles

	##
	# Returns the profiles
	def get_profiles(self):
		return self._profiles

	def add_profile(self, xml_path, profile, attr):
		tmp_profile = {}
		if "name" in attr.getNames():
			for attrName in attr.getNames():
				tmp_profile[attrName] = str(attr.getValue(attrName))
		self._tmp_profiles.append(tmp_profile)

	def serialize_profiles(self):
		self.data += "<profiles>"
		for profile in self._profiles:
			self.data += "<profile"
			for attr in profile:
				self.data += " %s=\"%s\"" % (attr, profile[attr])
			self.data += " />"
		self.data += "</profiles>"
	
	##
	# Sets the clients
	# @param xml_path not used here.
	# @param architecture_template the architecture to be installed
	# @param xml_attr not used here.
	def set_clients(self, xml_path, clients, attr):
		if not clients:
			self._clients = self._tmp_clients
			self._tmp_clients = []
		else:
			self._clients = clients

	##
	# Returns the clients
	def get_clients(self):
		return self._clients

	def add_client(self, xml_path, client, attr):
		tmp_client = {}
		if "hostname" in attr.getNames():
			for attrName in attr.getNames():
				tmp_client[attrName] = str(attr.getValue(attrName))
		self._tmp_clients.append(tmp_client)

	def serialize_clients(self):
		self.data += "<clients>"
		for client in self._clients:
			self.data += "<client"
			for attr in client:
				self.data += " %s=\"%s\"" % (attr, client[attr])
			self.data += " />"
		self.data += "</clients>"
	
