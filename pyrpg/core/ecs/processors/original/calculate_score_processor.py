__all__ = ['CalculateScoreProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.original.has_score import HasScore
from pyrpg.core.ecs.components.original.flag_add_score import FlagAddScore

# For creation of events
from pyrpg.core.events.event import Event

class CalculateScoreProcessor(Processor):
    def __init__(self, score_event_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.score_event_queue = score_event_queue

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Score comp and there is some score to be added
        for ent, (has_score, flag_add_score) in self.world.get_components(HasScore, FlagAddScore):

            # Score can be delegated from one entity to another by using delegate attribute on Score component
            if has_score.delegate is not None:
                # Check if component exists and overwrite score with delegated component
                ent = has_score.delegate
                has_score = self.world.try_component(ent, (HasScore))

            # Add score to the correct component - if score component exists, else do nothing
            try:
                # Add Score
                has_score.score += flag_add_score.add_score

                # Report score was counted
                score_event = Event('SCORE', ent, None, params={'scored' : ent, 'score' : flag_add_score.add_score, 'total' : has_score.score})
                self.score_event_queue.append(score_event)

                print(f'CalculateScoreProcessor: Entity {ent} has scored {flag_add_score.add_score}, now having total score of {has_score.score}.')

            except AttributeError:
                print(f'Entity ID {has_score.delegated} does not have Score component and hence score cannot be counted.')
                pass


