# Test plugin implementation

import plugin,sys

class plugin1:
	loadable = 1

	def __init__(self, hdlr):
		hdlr.add_callback("all", 90, self.hello)

	def unload(self, hdlr):
		hdlr.remove_callback("all", 90, self.hello)

	def hello(self, arg):
		sys.stdout.write("testplugin2.plugin1 ")
		raise plugin.CallbackException("testplugin2.plugin1")


#def abc():
#	val = traceback.extract_stack()
#	print val
#	for a in val:
#		print a

#	traceback.print_stack()

#	try:
#		raise ZeroDivisionError
#	except ZeroDivisionError:
#		tb = sys.exc_info()[2] #.tb_frame.f_back
#
#	frame = tb.tb_frame
#	
#	while (frame.f_back != None):
#		frame = frame.f_back
#
#	loader_globals = frame.f_globals
#
#	print "filename:",frame.f_code.co_filename
#	print loader_globals["plugin1"]





