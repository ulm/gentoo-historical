import gtk
import GLIScreen

class Panel(GLIScreen.GLIScreen):

	title = "Ugly"

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller, show_title=False)
		vert = gtk.VBox(False, 0)
		vert.set_border_width(10)

		content_str = """
Nothing to see here, move along.
"""
 	
		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=False, fill=False, padding=0)            

		self.add_content(vert)

	def activate(self):
		pass
#		self.controller.SHOW_BUTTON_EXIT    = True
#		self.controller.SHOW_BUTTON_HELP    = True
#		self.controller.SHOW_BUTTON_BACK    = False
#		self.controller.SHOW_BUTTON_FORWARD = True
#		self.controller.SHOW_BUTTON_FINISH  = False
