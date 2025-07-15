__all__ = ['GenerateScoreOnNoHealthProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_was_damaged_by import FlagWasDamagedBy
from core.components.scorable_on_no_health import ScorableOnNoHealth
from core.components.flag_has_no_health import FlagHasNoHealth
from core.components.flag_has_scored import FlagHasScored

# Logger init
logger = logging.getLogger(__name__)

class GenerateScoreOnNoHealthProcessor(Processor):
    ''' Detects entities that are destroyed and that generate score upon
    the destroy. The FlagHasScored is then added to the respective entity.

    Involved components:
        -   FlagWasDamagedBy
        -   ScorableOnNoHealth
        -   FlagHasScored

    Related processors:
        -   CalculateScoreProcessor
        -   RemoveFlagHasScoredProcessor

    What if this processor is disabled?
        -   no score is generated upon destroy

    Where the processor should be planned?
        -   after PerformDamageProcessor
        -   after GenerateScoreOnDamageProcessor - in order destroy score overwrites damage score 
        -   before RemoveFlagHasScoredProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'damage_system:PerformDamageProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        '''  Detects entities that are destroyed + have the ability to
        generate score and assign FlagHasScored to respective entity.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Damaging and FlagHasCollided - those are candidates for causing damage
        for ent_destroyed, (flag_was_damaged_by, scorable_on_no_health, flag_has_no_health) in self.world.get_components(FlagWasDamagedBy, ScorableOnNoHealth, FlagHasNoHealth):

            # Assign FlagAddScore to every entity recorded on FlagWasDamagedBy
            for ent_damaging in flag_was_damaged_by.entities:

                self.world.add_component(ent_damaging, FlagHasScored(score=scorable_on_no_health.score))

                logger.debug(f'({self.cycle}) - Entity {ent_damaging} is about to have increased score by {scorable_on_no_health.score}.')

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
