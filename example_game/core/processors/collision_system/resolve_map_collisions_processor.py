__all__ = ['ResolveMapCollisionsProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.position import Position
from core.components.collidable import Collidable

from pyrpg.core.config import GAME # for TILE_RES_PX

# Logger init
logger = logging.getLogger(__name__)

class ResolveMapCollisionsProcessor(Processor):
    ''' Resolve collisions with the map so that entities are
    not crossing the collision tiles.

    Involved components:
        -   Position
        -   Collidable

    Related processors:

    What if this processor is disabled?
        -   entities can cross the map walls

    Where the processor should be planned?
        -   after ResolveEntityCollisionsProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
    ]

    def __init__(self, maps, *args, **kwargs):
        ''' Init the processor.

        Parameters:
            :param maps: Reference to the dictionary of maps.
            :param maps: reference

        '''
        super().__init__(*args, **kwargs)

        self.maps = maps

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' On collision, return the entity on its original position.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Do collision against the map 
        for ent_moved, (coll_moved, pos_moved) in self.world.get_components(Collidable, Position):
            
            # Get the map using the global dict of maps
            collision_map = self.maps.get(pos_moved.map)

            # NEW check collisions by function collision_map.check_collision(((int(pos_moved.x - coll_moved.x) // 64),(int(pos_moved.y - coll_moved.y) // 64)))
            if (collision_map.check_collision((int(pos_moved.x + coll_moved.dx - coll_moved.x) // GAME["TILE_RES_PX"]), (int(pos_moved.y + coll_moved.dy - coll_moved.y) // GAME["TILE_RES_PX"])) or 
                collision_map.check_collision((int(pos_moved.x + coll_moved.dx - coll_moved.x) // GAME["TILE_RES_PX"]), (int(pos_moved.y + coll_moved.dy + coll_moved.y) // GAME["TILE_RES_PX"])) or
                collision_map.check_collision((int(pos_moved.x + coll_moved.dx + coll_moved.x) // GAME["TILE_RES_PX"]), (int(pos_moved.y + coll_moved.dy - coll_moved.y) // GAME["TILE_RES_PX"])) or
                collision_map.check_collision((int(pos_moved.x + coll_moved.dx + coll_moved.x) // GAME["TILE_RES_PX"]), (int(pos_moved.y + coll_moved.dy + coll_moved.y) // GAME["TILE_RES_PX"]))):

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

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
