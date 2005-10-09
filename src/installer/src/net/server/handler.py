
class Handler(object):

	def __init__(self, get_params, post_params, headers_out, shared_info):
		self.get_params = get_params
		self.post_params = post_params
		self.headers_out = headers_out
		self.shared_info = shared_info

	def wrap_in_template(self, content):
		f = open("template.html", 'rb')
		lines = f.readlines()
		f.close()
		for i in range(len(lines)):
			if lines[i] == "Main content\n":
				lines[i] = content
		return "".join(lines)
		
	def wrap_in_webgli_template(self, content):
		f = open("webgli_template.html", 'rb')
		lines = f.readlines()
		f.close()
		for i in range(len(lines)):
			if lines[i] == "Main content\n":
				lines[i] = content
		return "".join(lines)
