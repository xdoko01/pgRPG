__all__ = ['CalculateDamageProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.original.damageable import Damageable
from pyrpg.core.ecs.components.original.flag_add_damage import FlagAddDamage
from pyrpg.core.ecs.components.original.flag_no_health import FlagNoHealth

# For creation of events
from pyrpg.core.events.event import Event

class CalculateDamageProcessor(Processor):
    def __init__(self, damage_event_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.damage_event_queue = damage_event_queue

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have can take damage and were damaged
        for ent, (damageble, flag_add_damage) in self.world.get_components(Damageable, FlagAddDamage):

            # Add damage to the entity,health cannot drop below 0
            damageble.health = max(0, damageble.health - flag_add_damage.damage)

            # Report damage event
            damage_event = event.Event('DAMAGE', ent, flag_add_damage.src_entity, params={'damaging' : flag_add_damage.src_entity, 'damaged' : ent})
            self.damage_event_queue.append(damage_event)

            print(f'CalculateDamageProcessor: Entity {ent} has been damaged by {flag_add_damage.src_entity}, now having total health of {damageble.health}.')

            # Add FlagNoHealth if entity has no health
            if damageble.health == 0:

                self.world.add_component(ent, FlagNoHealth(src_entity=flag_add_damage.src_entity))
