__all__ = ['CollisionDamageProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.original.damaging import Damaging
from pyrpg.core.ecs.components.original.collidable import Collidable
from pyrpg.core.ecs.components.original.flag_add_damage import FlagAddDamage

# For creation of events
from pyrpg.core.events.event import Event

class CollisionDamageProcessor(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Iterate all entities that are generating damage and can be collided
        for ent, (damaging, collision) in self.world.get_components(Damaging, Collidable):

            # Add component FlagAddDamage to all entities that have touched Damaging entity (i.e. NPC touched arrow)
            for col_event_entity in collision.collision_events:

                # Check if Damaging entity has parent parameter
                # If yes, then the source of damage comes from the parent not from entity itself

                # Add flag FlagAddDamage to the entities that have collided with Scorable component
                self.world.add_component(col_event_entity,
                                         FlagAddDamage(damage=damaging.damage, src_entity=damaging.parent if damaging.parent is not None else ent))

