# Test plugin implementation

import plugin,sys

class application:
	def __init__(self):
		#
		# Create out plugin handler, and set the plugin search path to "."
		#
		self.plugins = plugin.Plugin(".")

		#
		# If log4py is available, we use it to generate Plugin Framework debug output.
		#
		try:
			import log4py
			logger = log4py.Logger(log4py.FALSE).get_instance(self.plugins)
			logger.set_loglevel(log4py.LOGLEVEL_DEBUG)
			self.plugins.set_debug_callback(logger.debug)
		except:
			print "log4py not available"
			pass


	def load_plugins(self):
		#
		# Load up three different plugins, all three from this module.
		#
		# The latter two only work if this file is the main program OR
		# was already imported by the main program.
		#
		self.plugins.load_plugin("testplugin.plugin1")
		self.plugins.load_plugin("plugin2")
		self.plugins.load_plugin("plugin3")

	def load_plugins2(self):
		#
		# Load up an additional, external, plugin.
		#
		self.plugins.load_plugin("testplugin2.plugin1")

	def unload_plugins(self):
		#
		# Unload all three plugins.  The unloading order doesn't matter.
		#
		self.plugins.unload_plugin("testplugin.plugin1")
		self.plugins.unload_plugin("plugin2")
		self.plugins.unload_plugin("plugin3")
		self.plugins.unload_plugin("testplugin2.plugin1")

	def unload_plugins2(self):
		#
		# Unload all plugins.
		#
		self.plugins.unload_all_plugins()

	def test_plugins(self):
		sys.stdout.write("\n>>> Calling 'only1' [ ")
		ret = self.plugins.call("only1", "hello")
		sys.stdout.write("] Done.\n")
		sys.stdout.flush()
		print ">>> Returned:",ret

		sys.stdout.write("\n>>> Calling 'only2' [ ")
		ret = self.plugins.call("only2", "hello")
		sys.stdout.write("] Done.\n")
		sys.stdout.flush()
		print ">>> Returned:",ret

		sys.stdout.write("\n>>> Calling 'only3' [ ")
		ret = self.plugins.call("only3", "hello")
		sys.stdout.write("] Done.\n")
		sys.stdout.flush()
		print ">>> Returned:",ret

		sys.stdout.write("\n>>> Calling 'all'   [ ")
		ret = self.plugins.call("all", "all, by priority")
		sys.stdout.write("] Done.\n")
		sys.stdout.flush()
		print ">>> Returned:",ret


class plugin1:
	loadable = 1

	def __init__(self, hdlr):
		hdlr.add_callback("only1", 100, self.hello)
		hdlr.add_callback("all", 100, self.hello)

	def unload(self, hdlr):
		hdlr.remove_callback("only1", 100, self.hello)
		hdlr.remove_callback("all", 100, self.hello)

	def hello(self, arg):
		sys.stdout.write("testplugin.plugin1 ")
		return "testplugin.plugin1 "


class plugin2:
	loadable = 1

	def __init__(self, hdlr):
		hdlr.add_callback("only2", 100, self.hello)
		hdlr.add_callback("all", 80, self.hello)

	def unload(self, hdlr):
		hdlr.remove_callback("only2", 100, self.hello)
		hdlr.remove_callback("all", 80, self.hello)

	def hello(self, arg):
		sys.stdout.write("testplugin.plugin2 ")
		return "testplugin.plugin2 "


class plugin3:
	loadable = 1

	def __init__(self, hdlr):
		hdlr.add_callback("only3", 100, self.hello)
		hdlr.add_callback("all", 60, self.hello)

	def unload(self, hdlr):
		hdlr.remove_callback("only3", 100, self.hello)
		hdlr.remove_callback("all", 60, self.hello)

	def hello(self, arg):
		sys.stdout.write("testplugin.plugin3 ")
		return "testplugin.plugin3 "


app = application()
app.load_plugins()
app.test_plugins()
app.load_plugins2()
app.test_plugins()
app.unload_plugins()

app.load_plugins()
app.unload_plugins2()
