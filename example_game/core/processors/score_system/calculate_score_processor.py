__all__ = ['CalculateScoreProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.flag_has_scored import FlagHasScored
from core.components.has_score import HasScore

# For creation of events
from pyrpg.core.events.event import Event

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

    def __init__(self, FNC_ADD_EVENT, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)
        self.add_event_fnc = FNC_ADD_EVENT

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that can have score and that earned 
        some score in this cycle.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Damaging and FlagHasCollided - those are candidates for causing damage
        for ent_with_score, (has_score, flag_has_scored) in self.world.get_components(HasScore, FlagHasScored):

            has_score.score += flag_has_scored.score

            # Report score was counted
            score_event = Event('SCORE', ent_with_score, None, params={'scored' : ent_with_score, 'score' : flag_has_scored.score, 'total' : has_score.score})
            self.add_event_fnc(score_event)

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
