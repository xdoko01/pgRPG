''' pyrpg/pyrgp/core/components/map.py

'''
# Neccessary for accessing engine variables - maps
import pyrpg.core.engine as engine

def load_map(map_id):
	''' Called from Quest class. Loads map instance and save it
	to the list of maps stored on ngine level.
	'''

	# Assert that map is not yet registered/created
	assert (map_id not in engine.maps)

	# Most of the work is done here
	new_map = Map(map_id)
	
	# Store the map in list of the active maps
	engine.maps.update( {map_id : new_map} )


class Map:

	'''
	entities = {
		'q1p1n1' : MapEntity,
		'q1p1i1' : MapEntity
	}
	'''

	def __init__(self, map_id):
		
		self.entities = {}

	def clear_resources(self):
		""" called by ENgine.unload_map """

		for entity_id, entity_ref in self.entities.items():
			entity_ref.clear_resources()

	def register_entity (self, entity):
		if entity.id not in self.entities:
			self.entities.update({ entity.id : entity })

	def unregister_entity (self, entity_id):
		del self.entities[entity_id]
