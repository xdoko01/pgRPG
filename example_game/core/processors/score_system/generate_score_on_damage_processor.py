__all__ = ['GenerateScoreOnDamageProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.flag_was_damaged_by import FlagWasDamagedBy
from core.components.scorable_on_damage import ScorableOnDamage
from core.components.flag_has_scored import FlagHasScored

# Logger init
logger = logging.getLogger(__name__)

class GenerateScoreOnDamageProcessor(Processor):
    ''' Detects entities that are damaged and that generate score upon
    the damage. The FlagHasScored is then added to the respective entity.

    Involved components:
        -   FlagWasDamagedBy
        -   ScorableOnDamage
        -   FlagHasScored

    Related processors:
        -   CalculateScoreProessor
        -   RemoveFlagHasScoredProcessor

    What if this processor is disabled?
        -   no score is generated upon damage

    Where the processor should be planned?
        -   after PerformDamageProcessor
        -   before RemoveFlagHasScoredProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.damage_system:PerformDamageProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are damaged + have the ability to
        generate score and assign FlagHasScored to respective entity.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Damaging and FlagHasCollided - those are candidates for causing damage
        for ent_damaged, (flag_was_damaged_by, scorable_on_damage) in self.world.get_components(FlagWasDamagedBy, ScorableOnDamage):

            # Assign FlagAddScore to every entity recorded on FlagWasDamagedBy
            for ent_damaging in flag_was_damaged_by.entities:

                self.world.add_component(ent_damaging, FlagHasScored(score=scorable_on_damage.score))

                logger.debug(f'({self.cycle}) - Entity {ent_damaging} is about to have increased score by {scorable_on_damage.score}.')

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
