__all__ = ['CollisionMapProcessorFullScan']

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.original.collidable import Collidable
from pyrpg.core.ecs.components.original.position import Position

class CollisionMapProcessorFullScan(Processor):
    ''' Checks for collisions with the titles on the map.

    It checks collisions for all world entities. Unlike 
    CollisionMapProcessor that checks collisions only for the
    entities that are visible on the map.

    '''

    def __init__(self, maps, *args, **kwargs):
        ''' maps is link to global dict of maps
        '''
        super().__init__(*args, **kwargs)

        self.maps = maps

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        super().process(*args, **kwargs)

        # Do collision against the map
        for ent_moved, (coll_moved, pos_moved) in self.world.get_components(Collidable, Position):
            
            # Get collision map using the global dict of maps
            #collision_map = self.maps.get(pos_moved.map).collision_map
            collision_map = self.maps.get(pos_moved.map)

            # Get the map position where the entity is situated
            
            # Topleft corner is situated
            #if (collision_map[int(pos_moved.y - coll_moved.y) // 64][int(pos_moved.x - coll_moved.x) // 64] != 0 or
            #	# Topright corner is situated
            #	collision_map[int(pos_moved.y - coll_moved.y) // 64][int(pos_moved.x + coll_moved.x) // 64] != 0 or
            #	# Bottomleft corner
            #	collision_map[int(pos_moved.y + coll_moved.y) // 64][int(pos_moved.x - coll_moved.x) // 64] != 0 or
            #	# Bottom right corner
            #	collision_map[int(pos_moved.y + coll_moved.y) // 64][int(pos_moved.x + coll_moved.x) // 64] != 0):

            # NEW check collisions by function collision_map.check_collision(((int(pos_moved.x - coll_moved.x) // 64),(int(pos_moved.y - coll_moved.y) // 64)))
            if (collision_map.check_collision((int(pos_moved.x - coll_moved.x) // 64),(int(pos_moved.y - coll_moved.y) // 64)) or 
                collision_map.check_collision((int(pos_moved.x - coll_moved.x) // 64),(int(pos_moved.y + coll_moved.y) // 64)) or
                collision_map.check_collision((int(pos_moved.x + coll_moved.x) // 64),(int(pos_moved.y - coll_moved.y) // 64)) or
                collision_map.check_collision((int(pos_moved.x + coll_moved.x) // 64),(int(pos_moved.y + coll_moved.y) // 64))):

                # Fix position for the entity that has moved
                pos_moved.x = pos_moved.lastx
                pos_moved.y = pos_moved.lasty

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components
        '''
        self.maps = None

    def post_load(self, maps):
        ''' Reconfigure the processor after de-serialization by attaching
        the reference to maps again
        '''
        self.maps = maps
