__all__ = ['GenerateScoreOnPickupProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.flag_was_picked_by import FlagWasPickedBy
from core.components.scorable_on_pickup import ScorableOnPickup
from core.components.flag_has_scored import FlagHasScored

# Logger init
logger = logging.getLogger(__name__)

class GenerateScoreOnPickupProcessor(Processor):
    ''' Detects entities that are picked and that generate score upon
    the pickup. The FlagHasScored is then added to the respective picker.

    Involved components:
        -   FlagWasPickedBy
        -   ScorableOnPickup
        -   FlagHasScored

    Related processors:
        -   CalculateScoreProessor
        -   RemoveFlagHasScoredProcessor

    What if this processor is disabled?
        -   no score is generated upon pickup

    Where the processor should be planned?
        -   after PerformPickupProcessor
        -   before RemoveFlagHasScoredProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.pickup_system:PerformPickupProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are picked + have the ability to
        generate score and assign FlagHasScored to respective picker.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent_picked, (flag_was_picked_by, scorable_on_pickup) in self.world.get_components(FlagWasPickedBy, ScorableOnPickup):

            self.world.add_component(flag_was_picked_by.picker, FlagHasScored(score=scorable_on_pickup.score))

            logger.debug(f'({self.cycle}) - Entity {flag_was_picked_by.picker} is about to have increased score by {scorable_on_pickup.score}.')

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
