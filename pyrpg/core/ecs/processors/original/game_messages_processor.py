__all__ = ['GameMessagesProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor

class GameMessagesProcessor(Processor):

    def __init__(self, game_messages_handler):
        super().__init__()

        self.game_messages_handler = game_messages_handler

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Call external function that processes all events
        '''
        self.game_messages_handler()

