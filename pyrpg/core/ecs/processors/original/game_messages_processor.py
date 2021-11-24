__all__ = ['GameMessagesProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors

class GameMessagesProcessor(esper.Processor):

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

