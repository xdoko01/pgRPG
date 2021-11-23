__all__ = ['CollisionWeaponProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pyrpg.core.events.event as event # for creation of events


class CollisionWeaponProcessor(esper.Processor):
	def __init__(self, weapon_event_queue):
		super().__init__()
		self.weapon_event_queue = weapon_event_queue

	def process(self, *args, **kwargs):
		for ent, (weapon, collision) in self.world.get_components(components.Weapon, components.Collidable):

			# Process everything that collided with weapon entity
			for col_event_entity in collision.collision_events.copy():
					
					# If entity (that have collided with weapon) can wear weapons items (HasWeapon)
					if self.world.has_component(col_event_entity, components.HasWeapon):
						
						# Get the HasWeapon component of the entity that picked up Weapon
						col_event_entity_has_weapon = self.world.component_for_entity(col_event_entity, components.HasWeapon)
						
						# Get the Collidable component of the entity that picked up Weapon - in order to remove the collision
						col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)

						# Add weapon to the HasWeapon - only in case that the slot for Weapon is available
						# For that purpose weapon must have some type
						if not col_event_entity_has_weapon.weapons.get(weapon.type).get('weapon'):
							col_event_entity_has_weapon.weapons[weapon.type]['weapon'] = ent
							
							# Store the action connected to the weapon in the hasWeapon component
							# OBSOLETE - action removed from hasWeapon component, newly is determined by the weapon
							#col_event_entity_has_weapon.action = self.world.component_for_entity(ent, components.Weapon).action

							# Change to the new weapon
							col_event_entity_has_weapon.set_weapon_in_use(weapon.type)

							try:
								# Remove Position component from the weapon so that it is not displayable on the map - weapon is picked
								self.world.remove_component(ent, components.Position) 
								# Remove Camera component from the weapon so that the screen disappears - weapon is picked
								self.world.remove_component(ent, components.Camera) 
							except KeyError:
								pass


							# Remove the col_event_entity from HasWeapon entity
							collision.collision_events.remove(col_event_entity)

							# Remove the col event related to item from the Weapon
							col_event_entity_coll.collision_events.remove(ent)

							# Report that item was weared - generate event
							weapon_event = event.Event('WEAPON_ARMED', ent, col_event_entity, params={'weapon' : ent, 'picker' : col_event_entity})
							self.weapon_event_queue.append(weapon_event)
