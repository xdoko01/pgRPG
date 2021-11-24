__all__ = ['CollisionAmmoPackProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pyrpg.core.events.event as event # for creation of events


class CollisionAmmoPackProcessor(esper.Processor):
    def __init__(self, ammo_pack_event_queue):
        super().__init__()
        self.ammo_pack_event_queue = ammo_pack_event_queue

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        for ent, (ammo_pack, collision, factory) in self.world.get_components(components.AmmoPack, components.Collidable, components.Factory):

            # Process everything that collided with AmmoPack entity
            for col_event_entity in collision.collision_events.copy():
                    
                    # If entity (that have collided with AmmoPack) can wear weapons items (HasWeapon)
                    if self.world.has_component(col_event_entity, components.HasWeapon):
                        
                        # Get the HasWeapon component of the entity that picked up AmmoPack
                        col_event_entity_has_weapon = self.world.component_for_entity(col_event_entity, components.HasWeapon)
                        
                        # Get the Collidable component of the entity that picked up AmmoPack - in order to remove the collision
                        col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)

                        # Get the generator armed currently on the weapon type
                        current_generator_entity = col_event_entity_has_weapon.weapons.get(ammo_pack.weapon).get('generator')

                        # Add AmmoPack to the HasWeapon - only in case that the slot for AmmoPack is available
                        # For that purpose AmmoPack must have some weapon type assigned
                        if current_generator_entity is None:
                            col_event_entity_has_weapon.weapons[ammo_pack.weapon]['generator'] = ent

                            # Add FlagAmmoPackArmed component refering to entity with HasWeapon component
                            self.world.add_component(ent, components.FlagAmmoPackArmed(armed_entity=col_event_entity))

                            # Remove Position component from the AmmoPack so that it is not displayable on the map - ammo_pack is picked
                            self.world.remove_component(ent, components.Position) 

                            try:
                                # Remove Camera component from the AmmoPack so that the screen disappears - AmmoPack is picked
                                self.world.remove_component(ent, components.Camera)
                            except KeyError:
                                pass


                            # Remove the col_event_entity from HasWeapon entity
                            collision.collision_events.remove(col_event_entity)

                            # Remove the col event related to item from the AmmoPack
                            col_event_entity_coll.collision_events.remove(ent)

                            # Report that AmmoPack was picked - generate event
                            weapon_event = event.Event('AMMO_PACK_ARMED', ent, col_event_entity, params={'ammo_pack' : ent, 'picker' : col_event_entity})
                            self.ammo_pack_event_queue.append(weapon_event)

                        # If same AmmoPack is picked up as already armed on the weapon, add projectiles
                        elif self.world.component_for_entity(current_generator_entity, components.AmmoPack).type == ammo_pack.type:
                            
                            factory_original_generator = self.world.component_for_entity(current_generator_entity, components.Factory)
                            if factory_original_generator.max_units and factory.max_units:
                                factory_original_generator.max_units += (factory.max_units - factory.current_units)
                                print(f'New Max Units value {factory_original_generator.max_units}')
                            elif not factory_original_generator.max_units or not factory.max_units:
                                factory_original_generator.max_units = None
                            

                            # Mark the AmmoPack as depleted and hence for removal
                            self.world.add_component(ent, components.FlagFactoryDepleted())

                            # Remove the col_event_entity from HasWeapon entity
                            collision.collision_events.remove(col_event_entity)

                            # Remove the col event related to item from the AmmoPack
                            col_event_entity_coll.collision_events.remove(ent)

                            # Report that AmmoPack was picked - generate event
                            weapon_event = event.Event('AMMO_PACK_ARMED', ent, col_event_entity, params={'ammo_pack' : ent, 'picker' : col_event_entity})
                            self.ammo_pack_event_queue.append(weapon_event)

