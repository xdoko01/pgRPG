__all__ = ['RenderBackgroundProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors

class RenderBackgroundProcessor(esper.Processor):
	def __init__(self, window, clear_color=(0, 0, 0), debug=False):

		super().__init__()
		self.window = window
		self.clear_color = clear_color
		self.debug = debug

	def process(self, *args, **kwargs):
		# Clear the main game window surface
		self.window.fill(self.clear_color)
	
	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components (window)
		'''
		self.window = None

	def post_load(self, window):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to window again
		'''
		self.window = window
