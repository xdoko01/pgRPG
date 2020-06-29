__all__ = ['CollisionDamageProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components
import core.events.event as event # for creation of events
import core.config.config as config # for the time before dead body disappears

class CollisionDamageProcessor(esper.Processor):
	def __init__(self, damage_event_queue):
		super().__init__()
		self.damage_event_queue = damage_event_queue

	def process(self, *args, **kwargs):

		for ent, (damaging, collision) in self.world.get_components(components.Damaging, components.Collidable):

			# Process everything that collided with Damaging entity (typically arrow, projectile, ...)
			for col_event_entity in collision.collision_events.copy():

				# If hitted component has Damageble component then proceed
				if self.world.has_component(col_event_entity, components.Damageable):

					# Get the Damageble component of the entity that was hit by the Projectile
					col_event_entity_damageable = self.world.component_for_entity(col_event_entity, components.Damageable) 
					
					# Get the Collidable component of the entity that was hitted - in order to remove the collision
					col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)

					#try:
					#	# Remove Position component from the weapon so that it is not displayable on the map - weapon is picked
					#	self.world.remove_component(ent, components.Position)
					#	# Remove Camera component from the weapon so that the screen disappears - weapon is picked
					#	self.world.remove_component(ent, components.Camera)
					#except KeyError:
					#	pass

					######################
					# Remove the col_event_entity from Damagable entity
					collision.collision_events.remove(col_event_entity)

					# Remove the col event related to item from the Damaging
					col_event_entity_coll.collision_events.remove(ent)
					#####################

					# Report that item was hit - generate event
					damage_event = event.Event('DAMAGE', ent, col_event_entity, params={'damaging' : ent, 'damaged' : col_event_entity})
					self.damage_event_queue.append(damage_event)

					# Decrease the health
					col_event_entity_damageable.health -= damaging.damage

					# Die if health is up
					if col_event_entity_damageable.health < 0:
						
						# Set health to 0
						col_event_entity_damageable.health = 0

						# Generate DEATH event
						kill_event = event.Event('KILL', ent, col_event_entity, params={'killed_by' : ent, 'killed' : col_event_entity})
						self.damage_event_queue.append(kill_event)

						# Add IsDead tag/component to the entity col_event_entity
						self.world.add_component(col_event_entity, components.IsDead())

						# Remove Motion component from the entity - nobody wants to see dead body moving
						try:
							self.world.remove_component(col_event_entity, components.Motion)
						except KeyError:
							pass

						# Remove Brain component from the entity - nobody wants to see dead body performing commands
						try:
							self.world.remove_component(col_event_entity, components.Brain)
						except KeyError:
							pass

						# Remove Collidable component from the entity - dead body does not colide with anything
						try:
							self.world.remove_component(col_event_entity, components.Collidable)
						except KeyError:
							pass

						# Remove Camera component from the entity - dead entity is no longer focused
						try:
							self.world.remove_component(col_event_entity, components.Camera)
						except KeyError:
							pass

						# Add temporary component to the entity - visible for 20s
						self.world.add_component(col_event_entity, components.Temporary(ttl=config.DEAD_TIME_TO_DISAPPEAR))


