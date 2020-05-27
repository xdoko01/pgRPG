__all__ = ['GameEventsProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors

class GameEventsProcessor(esper.Processor):

	def __init__(self, game_event_handler):
		super().__init__()

		self.game_event_handler = game_event_handler

	def process(self, *args, **kwargs):
		''' Call external function that processes all events
		'''
		self.game_event_handler()