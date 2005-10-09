import GLIServerProfile
import handler

class Welcome(handler.Handler):

	def welcome(self):
		return self.wrap_in_template("Do some shit on the left")

	def handle(self, path):
		paths = { '/welcome': self.welcome,
		        }
		return_content = paths[path]()
		return self.headers_out, return_content
