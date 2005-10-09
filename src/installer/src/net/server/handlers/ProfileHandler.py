import GLIServerProfile
import handler

class ProfileHandler(handler.Handler):

	def loadprofile(self):
		content = """
		<h2>Load Profile</h2>
		<br>
		<form action="/loadprofile2" method="POST" enctype="multipart/form-data">
		Use local (to server) file: <input type="text" name="localfile"><br>
		or<br>
		Upload file: <input type="file" name="uploadfile"><br>
		<input type="submit" value="Load">
		</form>
		"""
		return self.wrap_in_template(content)

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
		return self.wrap_in_template(content)

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

	def handle(self, path):
		paths = { '/loadprofile': self.loadprofile,
		          '/loadprofile2': self.loadprofile2,
		          '/saveprofile': self.saveprofile,
		          '/saveprofile2': self.saveprofile2
		        }
		return_content = paths[path]()
		return self.headers_out, return_content
