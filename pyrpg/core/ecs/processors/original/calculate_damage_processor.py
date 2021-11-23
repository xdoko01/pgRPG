__all__ = ['CalculateDamageProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pyrpg.core.events.event as event # for creation of events

class CalculateDamageProcessor(esper.Processor):
    def __init__(self, damage_event_queue):
        super().__init__()
        self.damage_event_queue = damage_event_queue

    def process(self, *args, **kwargs):

        # Get all entities that have can take damage and were damaged
        for ent, (damageble, flag_add_damage) in self.world.get_components(components.Damageable, components.FlagAddDamage):

            # Add damage to the entity,health cannot drop below 0
            damageble.health = max(0, damageble.health - flag_add_damage.damage)

            # Report damage event
            damage_event = event.Event('DAMAGE', ent, flag_add_damage.src_entity, params={'damaging' : flag_add_damage.src_entity, 'damaged' : ent})
            self.damage_event_queue.append(damage_event)

            print(f'CalculateDamageProcessor: Entity {ent} has been damaged by {flag_add_damage.src_entity}, now having total health of {damageble.health}.')

            # Add FlagNoHealth if entity has no health
            if damageble.health == 0:

                self.world.add_component(ent, components.FlagNoHealth(src_entity=flag_add_damage.src_entity))
