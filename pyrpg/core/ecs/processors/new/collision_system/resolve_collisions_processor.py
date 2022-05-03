__all__ = [
    'ResolveCollisionsProcessor'
]

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.collidable import Collidable
from pyrpg.core.ecs.components.new.movable import Movable
from pyrpg.core.ecs.components.new.flag_has_collided import FlagHasCollided
from pyrpg.functions import sign

from pyrpg.functions import allow_deny_item_filter

# Logger init
logger = logging.getLogger(__name__)

class ResolveCollisionsProcessor(Processor):
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
        -   GenerateCollisionsFullProcessor
        -   NewGenerateEntityCollisionsProcessor

    What if this processor is disabled?
        -   collisions are not happening

    Where the processor should be planned?
        -   after NewGenerateEntityCollisionsProcessor
        -   before RemoveFlagHasCollidedProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.collision_system:GenerateCollisionsProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Moves entities to omit the collision.
        '''
        self.cycle +=1

        # Get all entities that have collided with something and are moveable and are not to be ignored for collision resolution position fix
        for ent, (position, flag_has_collided, collidable, _) in self.world.get_components(Position, FlagHasCollided, Collidable, Movable):

            for collision in flag_has_collided.collisions:

                # Information about collision with other entity
                coll_ent, correction_vect, apply_fix, accept_fix, walkaround_mode = collision

                # Ignore correction - if entity should not be corrected by this particular entity
                if not apply_fix: continue

                # Store the last position
                position.lastx = position.x
                position.lasty = position.y
                position.lastmap = position.map

                # Change position based on the correction vector and other parameters - this particular algorithm is supporting walking around entities
                if not correction_vect.x and correction_vect.y:
                    position.x += sign(correction_vect.y) * collidable.position_fix_walkaround_mode * accept_fix
                    position.y += correction_vect.y * accept_fix

                elif correction_vect.x and not correction_vect.y:
                    position.x += correction_vect.x * accept_fix 
                    position.y += sign(correction_vect.x) * collidable.position_fix_walkaround_mode * accept_fix
        
                elif abs(correction_vect.x) < abs(correction_vect.y):
                    position.x += correction_vect.x * accept_fix
                    position.y += sign(correction_vect.y) * collidable.position_fix_walkaround_mode * accept_fix

                else:
                    position.x += sign(correction_vect.x) * collidable.position_fix_walkaround_mode * accept_fix
                    position.y += correction_vect.y * accept_fix


                logger.debug(f'({self.cycle}) - Entity {ent} corrected after collision with entity {coll_ent} - New possition: [{position.x}, {position.y}]')

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to
        non-serializable components
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization by attaching
        the lost reference again
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass