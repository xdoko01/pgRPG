__all__ = ['CollisionEntityGeneratorProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components

from .functions import filter_only_visible # for filtering only entities with position on the cameras

class CollisionEntityGeneratorProcessor(esper.Processor):
	''' Unlike CollisionEntityGeneratorProcessorFullScan, this processor
	checks only entities that are visible on one of the camera screens.

	
	-	COLLISION SYSTEM
			Checks for collisions and resolves them
			-	COLLISION + MOTION - Only entities that has moved are checked for collision
			-	COLLISION + POSITION - Above entities are checked against Collision and Position.
	'''

	def __init__(self):
		super().__init__()
		

	def process(self, *args, **kwargs):

		# Reset  has_collided flag to False on all valid entities - it is used for deleting entities on collision
		for _, (coll) in self.world.get_component(components.Collidable):
			coll.has_collided = False

		# For all camera screens in the game window
		for _, (camera) in self.world.get_component(components.Camera):

			# Get all entities that have Motion and Collidable (only those can activelly hit something) - i.e. that could have moved and iterate those
			for ent_moved, (pos_moved, coll_moved) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.Collidable)):
				

				# Compare that all collision + position entities - DUMMY WAY
				for ent_other, (pos_other, coll_other) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.Collidable)):
					
					# Heuristic no.-1 - Test only those that have Motion component
					#if not self.world.has_component(ent_moved, Motion): continue

					# Heuristic no.0 - Test only those that have moved component
					#if not self.world.component_for_entity(ent_moved, Motion).has_moved: continue

					# Heuristic no.1 - Skip if testing itself
					if ent_moved == ent_other: continue

					# Heuristic no 1.5 - Test only entities on the same map
					if pos_moved.map != pos_other.map: continue

					# Heuristic no.2 - Test only those in close distance
					#if abs(pos_moved.x - pos_other.y) > 200 or abs(pos_moved.y - pos_other.y) > 200: continue 

					# Heuristic no.3 - Do not test twice the same double of entities, i.e. 1,3 and 3,1
					
					# AABB comaprison - Collision
					if(pos_moved.x - coll_moved.x < pos_other.x + coll_other.x and
						pos_moved.x + coll_moved.x > pos_other.x - coll_other.x and
						pos_moved.y - coll_moved.y < pos_other.y + coll_other.y and
						pos_moved.y + coll_moved.y > pos_other.y - coll_other.y):
						
						# Add collision to the collision component
						coll_other.collision_events.add(ent_moved)
						#coll_moved.collision_events.add(ent_other)

						# Indicate the collision has happened - used for example in collision_deletion_processor
						coll_other.has_collided = True



