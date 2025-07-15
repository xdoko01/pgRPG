__all__ = ['PerformPathfindingCalculationProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Logger init
logger = logging.getLogger(__name__)

class PerformPathfindingCalculationProcessor(Processor):
    ''' Calls Pathfind manager for performing calculations for registred pathfinding requests.
    '''

    PREREQ = [
    ]

    def __init__(self, FNC_CALC_PATHS, max_no_of_calcs=None, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.calc_path_handler = FNC_CALC_PATHS
        self.max_no_of_calcs = max_no_of_calcs


    def process(self, *args, **kwargs):
        ''' Call external function that processes all commands
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Call path calc calculation handler - processing calc path calculations in the queue
        self.calc_path_handler(max_steps=self.max_no_of_calcs)

        logger.debug(f'({self.cycle}) - Calc Path handler executed.')

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
