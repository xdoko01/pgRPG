__all__ = ['GenerateScoreOnDestroyProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.flag_was_damaged_by import FlagWasDamagedBy
from pyrpg.core.ecs.components.new.scorable_on_destroy import ScorableOnDestroy
from pyrpg.core.ecs.components.new.is_destroyed import IsDestroyed
from pyrpg.core.ecs.components.new.flag_add_score import FlagAddScore

# Logger init
logger = logging.getLogger(__name__)

class GenerateScoreOnDestroyProcessor(Processor):
    ''' Detects entities that are destroyed and that generate score upon
    the destroy. The FlagAddScore is then added to the respective entity.

    Involved components:
        -   FlagWasDamagedBy
        -   ScorableOnDestroy
        -   FlagAddScore

    Related processors:
        -   CalculateScoreProessor
        -   RemoveFlagAddScoreProcessor

    What if this processor is disabled?
        -   no score is generated upon destroy

    Where the processor should be planned?
        -   after PerformDamageProcessor
        -   after GenerateScoreOnDamageProcessor - in order destroy score overwrites damage score 
        -   before RemoveFlagAddScoreProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.damage_system:PerformDamageProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are destroyed + have the ability to
        generate score and assign FlagAddScore to respective entity.
        '''
        self.cycle += 1

        # Get all entities that have Damaging and FlagHasCollided - those are candidates for causing damage
        for ent_destroyed, (flag_was_damaged_by, scorable_on_destroy, is_destroyed) in self.world.get_components(FlagWasDamagedBy, ScorableOnDestroy, IsDestroyed):

            # Assign FlagAddScore to every entity recorded on FlagWasDamagedBy
            for ent_damaging in flag_was_damaged_by.entities:

                self.world.add_component(ent_damaging, FlagAddScore(score=scorable_on_destroy.score))

                logger.debug(f'({self.cycle}) - Entity {ent_damaging} is about to have increased score by {scorable_on_destroy.score}.')

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
