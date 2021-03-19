__all__ = ['CommandProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors

class CommandProcessor(esper.Processor):

	def __init__(self, game_commands_handler, debug=False):
		super().__init__()

		self.game_commands_handler = game_commands_handler
		self.debug = debug

	def process(self, *args, **kwargs):
		''' Call external function that processes all commands
		'''

		# In order to pass pressed keys to commands (such as ENTER is pressed)
		keys = kwargs.get('keys', [])
		events = kwargs.get('events', [])
		quests = kwargs.get('quests', {})

		# Call command handler - processing commands from the queue
		self.game_commands_handler(keys=keys, events=events, debug=self.debug)
