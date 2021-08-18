__all__ = ['NewResolveEntityCollisionsExProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class NewResolveEntityCollisionsExProcessor(esper.Processor):
    ''' Process collisions stored in component NewFlagHasCollided and do not
    allow to overlap.
    Unlike NewResolveCollisionsProcessor this one is activly trying to move 
    entities away from collisions using collision vector calculated during collision.

    Involved components:
        -   NewCollidable
        -   NewFlagHasCollided

    Related processors:
        -   NewRemoveFlagHasCollidedProcessor
        -   NewGenerateCollisionsFullProcessor
        -   NewGenerateCollisionsProcessor

    What if this processor is disabled?
        -   collisions are not happening

    Where the processor should be planned?
        -   after NewGenerateCollisionsProcessor
        -   before NewRemoveFlagHasCollidedProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['NewGenerateEntityCollisionsProcessor']


    def __init__(self, add_command_fnc):
        ''' Init the processor.
        '''
        super().__init__()

        self.add_command_fnc = add_command_fnc

    def process(self, *args, **kwargs):
        ''' Moves entities to omit the collision.
        '''
        self.cycle +=1

        # Get all entities that have collided with something and are moveable and are not to be ignored for collision resolution position fix
        for ent, (position, flag_has_collided, _) in self.world.get_components(components.Position, components.NewFlagHasCollided, components.NewMovable):

            for _, _, coll_fix_vector, ignore_position_fix in flag_has_collided.collisions:

                # 1/ add command to move using vector stored in NewFlagHasCollided
                # PROBLEM is that the velocity in NewMovable components affects this a lot
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
                if not coll_fix_vector.x or not coll_fix_vector.y:
                    #position.x += coll_fix_vector[0]
                    #position.y += coll_fix_vector[1]
                    position.x += coll_fix_vector.x
                    position.y += coll_fix_vector.y
                else:
                    #position.x += coll_fix_vector[0] if abs(coll_fix_vector[0]) < abs(coll_fix_vector[1]) else 0
                    #position.y += coll_fix_vector[1] if abs(coll_fix_vector[1]) <= abs(coll_fix_vector[0]) else 0
                    position.x += coll_fix_vector.x if abs(coll_fix_vector.x) < abs(coll_fix_vector.y) else 0
                    position.y += coll_fix_vector.y if abs(coll_fix_vector.y) <= abs(coll_fix_vector.x) else 0

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