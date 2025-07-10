__all__ = ['RemoveFlagHasScoredProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.flag_has_scored import FlagHasScored

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagHasScoredProcessor(Processor):
    ''' Removes the flag that the entity has scored.

    Involved components:
        -   FlagHasScored

    Related processors:
        -   CalculateScoreProcessor

    What if this processor is disabled?
        -   uncontrolled adding of score

    Where the processor should be planned?
        -   after CalculateScoreProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'score_system:CalculateScoreProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the flag that the entity has scored.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagHasScored):

            self.world.remove_component(ent, FlagHasScored)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagHasScored" was removed.')

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

