__all__ = ['ResolveEntityCollisionsExProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.collidable import Collidable
from pyrpg.core.ecs.components.new.movable import Movable
from pyrpg.core.ecs.components.new.flag_has_collided import FlagHasCollided

# Logger init
logger = logging.getLogger(__name__)

class ResolveEntityCollisionsExProcessor(Processor):
    ''' Process collisions stored in component FlagHasCollided and do not
    allow to overlap.
    Unlike NewResolveCollisionsProcessor this one is activly trying to move 
    entities away from collisions using collision vector calculated during collision.

    Involved components:
        -   Position
        -   Movable
        -   FlagHasCollided

    Related processors:
        -   RemoveFlagHasCollidedProcessor
        -   NewGenerateCollisionsFullProcessor
        -   NewGenerateCollisionsProcessor

    What if this processor is disabled?
        -   collisions are not happening

    Where the processor should be planned?
        -   after NewGenerateCollisionsProcessor
        -   before RemoveFlagHasCollidedProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.collision_system.generate_entity_collisions_processor:GenerateEntityCollisionsProcessor'
    ]

    def __init__(self, add_command_fnc):
        ''' Init the processor.
        '''
        super().__init__()

        self.add_command_fnc = add_command_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Moves entities to omit the collision.
        '''
        self.cycle +=1

        # Get all entities that have collided with something and are moveable and are not to be ignored for collision resolution position fix
        for ent, (position, flag_has_collided, collidable, _) in self.world.get_components(Position, FlagHasCollided, Collidable, Movable):

            for _, _, coll_fix_vector, ignore_position_fix in flag_has_collided.collisions:

                # 1/ add command to move using vector stored in FlagHasCollided
                # PROBLEM is that the velocity in Movable components affects this a lot
                # self.add_command_fnc(('new_move_vect_noadd', {"entity" : ent, "vector" : coll_fix_vector}))

                # 2/ directly adjust the position component without issuing any command and without changing the direction
                
                # Ignore fixing of position in case entity has ignore_collision_fix
                if ignore_position_fix: continue
                
                # Store the last position
                position.lastx = position.x
                position.lasty = position.y
                position.lastmap = position.map
                
                # Change to the new position
                # Find the minimum move on x or y axis and do the minimal movement - at the same time if on some axis is 0 movement, do not move on that axis as the collisin fix will not work
                # use the fact that bool(0) gains False

                # If either X or Y value of correction vector is 0 use the vector as it is
                '''
                if not coll_fix_vector.x or not coll_fix_vector.y:
                    position.x += coll_fix_vector.x
                    position.y += coll_fix_vector.y
                else:
                    position.x += coll_fix_vector.x if abs(coll_fix_vector.x) < abs(coll_fix_vector.y) else 0
                    position.y += coll_fix_vector.y if abs(coll_fix_vector.y) <= abs(coll_fix_vector.x) else 0
                '''
                
                # Alternativelly, move a little bit in every direction in order for entities not to get stucked
                sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)
                
                if not coll_fix_vector.x and coll_fix_vector.y:
                    position.x += sign(coll_fix_vector.y) * collidable.position_fix_walkaround_mode * collidable.position_fix_for_self
                    position.y += coll_fix_vector.y * collidable.position_fix_for_self
                elif coll_fix_vector.x and not coll_fix_vector.y:
                    position.x += coll_fix_vector.x * collidable.position_fix_for_self
                    position.y += sign(coll_fix_vector.x) * collidable.position_fix_walkaround_mode * collidable.position_fix_for_self
                elif abs(coll_fix_vector.x) < abs(coll_fix_vector.y):
                    position.x += coll_fix_vector.x * collidable.position_fix_for_self
                    position.y += sign(coll_fix_vector.y) * collidable.position_fix_walkaround_mode * collidable.position_fix_for_self
                else:
                    position.x += sign(coll_fix_vector.x) * collidable.position_fix_walkaround_mode * collidable.position_fix_for_self
                    position.y += coll_fix_vector.y * collidable.position_fix_for_self

                logger.debug(f'({self.cycle}) - Entity {ent} - New possition: [{position.x}, {position.y}]')

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to
        non-serializable components
        '''
        pass

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the lost reference again
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass