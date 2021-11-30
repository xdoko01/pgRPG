__all__ = ['DebugProcessorPerformanceProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Logger init
logger = logging.getLogger(__name__)

class DebugProcessorPerformanceProcessor(Processor):
    ''' Log the running time of the processors
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Get all components comp_name and list their values
        '''
        self.cycle += 1
        logger.debug(f'({self.cycle}) - {self.world.process_times} ')

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization by attaching
        the removed references again.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass