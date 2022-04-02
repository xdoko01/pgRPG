__all__ = ['NewResolveEntityCollisionsExProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.new_collidable import NewCollidable
from pyrpg.core.ecs.components.new.movable import Movable
from pyrpg.core.ecs.components.new.flag_has_collided import FlagHasCollided

# Logger init
logger = logging.getLogger(__name__)

class NewResolveEntityCollisionsExProcessor(Processor):
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
        'new.collision_system.new_generate_entity_collisions_processor:NewGenerateEntityCollisionsProcessor'
    ]

    def __init__(self, FNC_ADD_COMMAND):
        ''' Init the processor.
        '''
        super().__init__()

        self.add_command_fnc = FNC_ADD_COMMAND

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Moves entities to omit the collision.
        '''
        self.cycle +=1

        # Get all entities that have collided with something and are moveable and are not to be ignored for collision resolution position fix
        for ent, (position, flag_has_collided, collidable, _) in self.world.get_components(Position, FlagHasCollided, NewCollidable, Movable):

            for collision in flag_has_collided.collisions:

                # Store the last position
                position.lastx = position.x
                position.lasty = position.y
                position.lastmap = position.map
                
                # CHange position based on the correction vector
                position.x += collision.corr_vect.x
                position.y += collision.corr_vect.y

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