"""
Gentoo Linux Installer

$Id: SimpleXMLParser.py,v 1.1 2004/10/08 20:55:17 samyron Exp $
Copyright 2004 Gentoo

"""

import xml.sax, string

class SimpleXMLParser(xml.sax.ContentHandler):

	def __init__(self, file=None):
		self._xml_elements = []
		self._xml_current_attr = None
		self._xml_current_data = ""
		self._fntable = {}
		self._path = file

	def addHandler(self, path, fn, call_on_null=False):
		try:
			self._fntable[path].append((fn,call_on_null))
		except KeyError:
			self._fntable[path] = [(fn, call_on_null)]

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
		self._xml_current_attr = attr
		self._xml_current_data = ""

	def endElement(self, name):
		path = self._xml_element_path()
		
		if path in self._fntable.keys():
			for fn in self._fntable[path]:
				if self._xml_current_data != "" or fn[1]:
					fn[0](path, self._xml_current_data, self._xml_current_attr)

		# Keep the XML state
		self._xml_current_data = ""
		self._xml_current_attr = None  
		self._xml_elements.pop()

	def characters(self, data):
		"""
		XML SAX character data handler
        
		Called when the SAX parser encounters character data.
		"""
                                        
		# This converts data to a string instead of being Unicode
		# Maybe we should use Unicode strings instead of normal strings?
		self._xml_current_data += string.strip(str(data))

	def _xml_element_path(self):
		"""
		Return path to current XML node
		"""                
		return string.join(self._xml_elements, '/')

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
