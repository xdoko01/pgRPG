__all__ = ['ResolveMapCollisionsProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.position import Position
from core.components.collidable import Collidable
from core.components.flag_has_collided import FlagHasCollided

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

                logger.debug(f'({self.cycle}) - Entity {ent_moved} hit the map wall on position [{pos_moved.x}, {pos_moved.y}]. Back to Original possition: [{pos_moved.lastx}, {pos_moved.lasty}]')

                # Rollback to original position for the entity that has moved into the wall
                pos_moved.x = pos_moved.lastx
                pos_moved.y = pos_moved.lasty

                # Rollback to original position the entities that have collided with the entity that hit the wall
                # This should go recursivelly

                # Keep list of entities that might pushed our ent_moved into the wall
                ents_to_check: list = []
                ents_to_check.append(ent_moved)

                # Keep the set of all already fixed entity_ids
                ents_fixed: set = {ent_moved}

                ents_checked: set = set()

                while ents_to_check:

                    ent_to_check = ents_to_check.pop(0)
                    
                    # Do not check already checked entity
                    if ent_to_check in ents_checked: 
                        logger.debug(f'({self.cycle}) - Entity {ent_to_check} was already checked before. Skipping. {ents_to_check=}, {ents_checked=}')
                        continue

                    # Entity ent_to_check not yet checked, proceed with checks
                    logger.debug(f'({self.cycle}) - Entity {ent_to_check} is being checked if it has collided with someone. {ents_to_check=}, {ents_checked=}')

                    flag_has_collided = self.world.try_component(ent_to_check, FlagHasCollided)
                    collisions = [] if flag_has_collided is None else flag_has_collided.collisions
                    
                    logger.debug(f'({self.cycle}) - Entity {ent_to_check} has collided with {collisions}. Those will be verified')

                    for collision in collisions:

                        # Information about collision with other entity
                        coll_ent, correction_vect, apply_fix, accept_fix, walkaround_mode = collision
                        
                        # Append the entity to the list to check
                        ents_to_check.append(coll_ent)
                        logger.debug(f'({self.cycle}) - Entity {ent_to_check} collided with {coll_ent=}. Adding to {ents_to_check=}.')

                        # Rollback the position if not already done
                        if coll_ent not in ents_fixed:
                            coll_ent_pos = self.world.component_for_entity(coll_ent, Position)
                            logger.debug(f'({self.cycle}) - Entity {coll_ent} intermediarly hit the entity that hit the wall. Curr Pos: [{coll_ent_pos.x}, {coll_ent_pos.y}]. Back to Original possition: [{coll_ent_pos.lastx}, {coll_ent_pos.lasty}]')

                            #coll_ent_pos.x = coll_ent_pos.lastx
                            #coll_ent_pos.y = coll_ent_pos.lasty

                            ents_fixed.add(coll_ent)
                    
                    ents_checked.add(ent_to_check)


            #else: #no collision with the map
            #    pos_moved.lastx = pos_moved.x
            #    pos_moved.lasty = pos_moved.y
            #    pos_moved.lastmap = pos_moved.map


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
