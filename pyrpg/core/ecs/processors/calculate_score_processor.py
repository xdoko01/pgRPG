__all__ = ['CalculateScoreProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pyrpg.core.events.event as event # for creation of events

class CalculateScoreProcessor(esper.Processor):
    def __init__(self, score_event_queue):
        super().__init__()
        self.score_event_queue = score_event_queue

    def process(self, *args, **kwargs):

        # Get all entities that have Score comp and there is some score to be added
        for ent, (has_score, flag_add_score) in self.world.get_components(components.HasScore, components.FlagAddScore):

            # Score can be delegated from one entity to another by using delegate attribute on Score component
            if has_score.delegate is not None:
                # Check if component exists and overwrite score with delegated component
                ent = has_score.delegate
                has_score = self.world.try_component(ent, (components.HasScore))

            # Add score to the correct component - if score component exists, else do nothing
            try:
                # Add Score
                has_score.score += flag_add_score.add_score

                # Report score was counted
                score_event = event.Event('SCORE', ent, None, params={'scored' : ent, 'score' : flag_add_score.add_score, 'total' : has_score.score})
                self.score_event_queue.append(score_event)

                print(f'CalculateScoreProcessor: Entity {ent} has scored {flag_add_score.add_score}, now having total score of {has_score.score}.')

            except AttributeError:
                print(f'Entity ID {has_score.delegated} does not have Score component and hence score cannot be counted.')
                pass


