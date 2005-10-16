import GLIServerProfile
import handler

class Welcome(handler.Handler):

	def welcome(self):
		return self.wrap_in_template("Do some shit on the left")
		
	def showargs(self):
		text = "These are the GET params you passed:<br><br><pre>"
		text += str(self.get_params)
		text += "</pre><br><br>These are the POST params you passed:<br><br><pre>"
		text += str(self.post_params)
		text += "</pre>"
		return self.wrap_in_template(text)

	def handle(self, path):
		paths = { '/welcome': self.welcome,
				'/showargs': self.showargs
		        }
		return_content = paths[path]()
		return self.headers_out, return_content
