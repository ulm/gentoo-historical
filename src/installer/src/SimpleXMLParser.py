"""
Gentoo Linux Installer

$Id: SimpleXMLParser.py,v 1.3 2005/04/14 15:44:03 agaffney Exp $
Copyright 2004 Gentoo

"""

import xml.sax, string

class SimpleXMLParser(xml.sax.ContentHandler):

	##
	# Brief description of function
	# @param self Parameter description
	# @param file=None Parameter description
	def __init__(self, file=None):
		self._xml_elements = []
		self._xml_attrs = []
		self._xml_current_data = ""
		self._fntable = {}
		self._path = file

	##
	# Brief description of function
	# @param self Parameter description
	# @param path Parameter description
	# @param fn Parameter description
	# @param call_on_null=False Parameter description
	def addHandler(self, path, fn, call_on_null=False):
		try:
			self._fntable[path].append((fn,call_on_null))
		except KeyError:
			self._fntable[path] = [(fn, call_on_null)]

	##
	# Brief description of function
	# @param self Parameter description
	# @param path Parameter description
	# @param fn Parameter description
	def delHandler(self, path, fn):
		try:
			for function in self._fntable[path]:
				if function[0] == fn:
					self._fntable[path].remove(function)
					return True
			return False
		except KeyError:
			return False

	def startElement(self, name, attr): 
		"""
		XML SAX start element handler

		Called when the SAX parser encounters an XML openning element.
		"""

		self._xml_elements.append(name)
		self._xml_attrs.append(attr)
		self._xml_current_data = ""

	##
	# Brief description of function
	# @param self Parameter description
	# @param name Parameter description
	def endElement(self, name):
		path = self._xml_element_path()
		if path in self._fntable.keys():
			for fn in self._fntable[path]:
				if self._xml_current_data != "" or fn[1]:
					fn[0](path, self._xml_current_data, self._xml_attrs[-1])

		# Keep the XML state
		self._xml_current_data = ""
		self._xml_attrs.pop()
		self._xml_elements.pop()

	##
	# Brief description of function
	# @param self Parameter description
	# @param data Parameter description
	def characters(self, data):
		"""
		XML SAX character data handler
        
		Called when the SAX parser encounters character data.
		"""
                                        
		# This converts data to a string instead of being Unicode
		# Maybe we should use Unicode strings instead of normal strings?
		self._xml_current_data += string.strip(str(data))

	##
	# Brief description of function
	# @param self Parameter description
	def _xml_element_path(self):
		"""
		Return path to current XML node
		"""                
		return string.join(self._xml_elements, '/')

	##
	# Brief description of function
	# @param self Parameter description
	# @param path=None Parameter description
	def parse(self, path=None):
		"""
		Parse serialized configuration file.
		"""
		if path == None and self._path == None:
			raise "NoFileGiven","You must specify a file to parse!"
		elif path == None:       
			xml.sax.parse(self._path, self)
		else:
			xml.sax.parse(path, self)
