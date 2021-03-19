__all__ = ['CollisionTeleportProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components
import core.events.event as event # for creation of events

class CollisionTeleportProcessor(esper.Processor):
	def __init__(self, teleport_event_queue):
		super().__init__()

		self.teleport_event_queue = teleport_event_queue

	def process(self, *args, **kwargs):
		for ent, (teleport, collision) in self.world.get_components(components.Teleport, components.Collidable):

			# Process everything that collided with teleport
			for col_event_entity in collision.collision_events.copy():
					
					# If entity is Teleportable and has position
					if self.world.has_components(col_event_entity, components.Teleportable, components.Position, components.Collidable):
						
						# Get the Position, Collidable and HasInventory component of the teleportee entity
						col_event_entity_pos = self.world.component_for_entity(col_event_entity, components.Position) 
						col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)
						try:
							col_event_entity_inventory = self.world.component_for_entity(col_event_entity, components.HasInventory)
							
							# Does the teleportee have the key in the inventory?
							# Either no key is required by the teleport or key is in teleportees inventory
							teleportee_has_key = teleport.key is None or teleport.key in col_event_entity_inventory.inventory

						except KeyError:
							teleportee_has_key = teleport.key is None

						# Do the teleportation of the teleportee - only if it has the key (by default no key necessary)
						if teleportee_has_key:
							col_event_entity_pos.x = teleport.dest_x
							col_event_entity_pos.y = teleport.dest_y
							col_event_entity_pos.map = teleport.dest_map 

							# Report that teleportation occured - generate event
							teleport_event = event.Event('TELEPORTATION', ent, col_event_entity, params={'teleport' : ent, 'teleportee' : col_event_entity})
							self.teleport_event_queue.append(teleport_event)

						# Remove the col_event_entity from Teleport
						collision.collision_events.remove(col_event_entity)

						# Remove the col event related to teleport from the Entity
						col_event_entity_coll.collision_events.remove(ent)
