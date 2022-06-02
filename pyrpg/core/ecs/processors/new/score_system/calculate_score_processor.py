__all__ = ['CalculateScoreProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.flag_has_scored import FlagHasScored
from pyrpg.core.ecs.components.new.has_score import HasScore

# Logger init
logger = logging.getLogger(__name__)

class CalculateScoreProcessor(Processor):
    ''' Detects entities that can have score and that earned some scor in this cycle.

    Involved components:
        -   HasScore
        -   FlagHasScored

    Related processors:
        -   GenerateScoreOnDamageProcessor
        -   GenerateScoreOnDestroyProcessor
        -   RemoveFlagHasScoredProcessor

    What if this processor is disabled?
        -   no score is calculated

    Where the processor should be planned?
        -   after GenerateScoreOnDamageProcessor
        -   after GenerateScoreOnDestroyProcessor
        -   before RemoveFlagHasScoredProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that can have score and that earned 
        some score in this cycle.
        '''
        self.cycle += 1

        # Get all entities that have Damaging and FlagHasCollided - those are candidates for causing damage
        for ent_with_score, (has_score, flag_has_scored) in self.world.get_components(HasScore, FlagHasScored):

            has_score.score += flag_has_scored.score

            logger.debug(f'({self.cycle}) - Entity {ent_with_score} increased score by {flag_has_scored.score}. New score is {has_score.score}.')

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
