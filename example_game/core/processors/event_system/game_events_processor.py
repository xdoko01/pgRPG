__all__ = ['GameEventsProcessor', 'GameEventsExProcessor']

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

class GameEventsProcessor(Processor):
    ''' Original event processor that calls the function that processes 
    all events in the event queue.
    '''

    def __init__(self, game_event_handler):
        super().__init__()

        self.game_event_handler = game_event_handler


    def process(self, *args, **kwargs):
        ''' Call external function that processes all events
        '''
        self.game_event_handler()


class GameEventsExProcessor(Processor):
    ''' New event processor that alows to ignore some events and also
    to selectively process only some event types.
    '''

    def __init__(self, game_event_handler, *args, **kwargs):
        ''' Example of instance creation

            processors.GameEventsExProcessor(process_game_events, ignore=('PHASE_START', 'SCENE_START'))
            processors.GameEventsExProcessor(process_game_events, process=('PHASE_START', 'SCENE_START'))
        '''

        super().__init__(*args, **kwargs)

        self.game_event_handler = game_event_handler
        self.to_ignore = kwargs.get('ignore', None)
        self.to_process = kwargs.get('process', None)

    # Not needed, implemented in the super class
    #def initialize(self, register, proc_group_id):
    #    '''Processor registers itself at esper ECS World 
    #    under specific processor group.
    #    '''
    #    register(self, proc_group_id)

    def process(self, *args, **kwargs):
        ''' Call external function that processes events
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        self.game_event_handler(process=self.to_process, ignore=self.to_ignore)

    def finalize(self):
        pass