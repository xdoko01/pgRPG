__all__ = ['GenerateScoreDestroyProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

class GenerateScoreDestroyProcessor(esper.Processor):
    def __init__(self):
        super().__init__()

    def process(self, *args, **kwargs):

        # Get all entities that have collided and are damagable and are capable of points generation upon damage
        for _, (scorable_on_destroy, flag_no_health, collidable) in self.world.get_components(components.ScorableOnDestroy, components.FlagNoHealth, components.Collidable):

            # Process everything that collided with ScorableOnDamage entity (typically arrow, projectile, ...)
            for col_event_entity in collidable.collision_events:

                # Add flag FlagAddScore to the entities that have collided with ScorableOnDamage component
                self.world.add_component(col_event_entity,
                                         components.FlagAddScore(add_score=scorable_on_destroy.score))

                print(f'GenerateScoreDestroyProcessor: FlagAddScore assigned with value {scorable_on_destroy.score} to entity {col_event_entity}.')

