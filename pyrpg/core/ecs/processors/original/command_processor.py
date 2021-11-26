__all__ = ['CommandProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor

class CommandProcessor(Processor):

    def __init__(self, game_commands_handler, debug=False):
        super().__init__()

        self.game_commands_handler = game_commands_handler
        self.debug = debug

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Call external function that processes all commands
        '''

        # In order to pass pressed keys to commands (such as ENTER is pressed)
        keys = kwargs.get('keys', [])
        events = kwargs.get('events', [])
        quests = kwargs.get('quests', {})

        # Call command handler - processing commands from the queue
        self.game_commands_handler(keys=keys, events=events, debug=self.debug)
