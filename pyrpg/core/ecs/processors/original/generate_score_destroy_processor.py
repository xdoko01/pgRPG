__all__ = ['GenerateScoreDestroyProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.original.scorable_on_destroy import ScorableOnDestroy
from pyrpg.core.ecs.components.original.collidable import Collidable
from pyrpg.core.ecs.components.original.flag_no_health import FlagNoHealth
from pyrpg.core.ecs.components.original.flag_add_score import FlagAddScore

class GenerateScoreDestroyProcessor(Processor):
    def __init__(self):
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):

        # Get all entities that have collided and are damagable and are capable of points generation upon damage
        for _, (scorable_on_destroy, flag_no_health, collidable) in self.world.get_components(ScorableOnDestroy, FlagNoHealth, Collidable):

            # Process everything that collided with ScorableOnDamage entity (typically arrow, projectile, ...)
            for col_event_entity in collidable.collision_events:

                # Add flag FlagAddScore to the entities that have collided with ScorableOnDamage component
                self.world.add_component(col_event_entity,
                                         FlagAddScore(add_score=scorable_on_destroy.score))

                print(f'GenerateScoreDestroyProcessor: FlagAddScore assigned with value {scorable_on_destroy.score} to entity {col_event_entity}.')

