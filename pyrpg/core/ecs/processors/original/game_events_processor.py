__all__ = ['GameEventsProcessor', 'GameEventsExProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors

class GameEventsProcessor(esper.Processor):
    ''' Original event processor that calls the function that processes 
    all events in the event queue.
    '''

    def __init__(self, game_event_handler):
        super().__init__()

        self.game_event_handler = game_event_handler

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Call external function that processes all events
        '''
        self.game_event_handler()


class GameEventsExProcessor(esper.Processor):
    ''' New event processor that alows to ignore some events and also
    to selectively process only some event types.
    '''

    def __init__(self, game_event_handler, **kwargs):
        ''' Example of instance creation

            processors.GameEventsExProcessor(process_game_events, ignore=('PHASE_START', 'QUEST_START'))
            processors.GameEventsExProcessor(process_game_events, process=('PHASE_START', 'QUEST_START'))
        '''

        super().__init__()

        self.game_event_handler = game_event_handler
        self.to_ignore = kwargs.get('ignore', None)
        self.to_process = kwargs.get('process', None)


    def process(self, *args, **kwargs):
        ''' Call external function that processes events
        '''
        self.game_event_handler(process=self.to_process, ignore=self.to_ignore)
