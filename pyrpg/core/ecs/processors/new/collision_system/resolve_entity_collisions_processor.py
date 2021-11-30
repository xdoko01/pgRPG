__all__ = ['ResolveEntityCollisionsProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.flag_has_collided import FlagHasCollided

# Logger init
logger = logging.getLogger(__name__)

# Simple static resolution - cannot move into collidable object
# PROS - simple and reliable
# CONS - it is not realistic - the moving entity should push the static entity
#    - alternative might be issuing command
#      - here is problem if movement is generated from brain then one command would mean step back
#        and the brain command will step forward again ...
### What requirements are there, really?
#  - moving entity (FlagHasMoved) hits static entity (no FlagHasMoved + but Moveable)
#    - moving entity pushes static entity - command change possition (that will keep direction just change position)
#  - moving entity (FlagHasMoved) hits static entity ()
# how to implement area that is causing damage such as Lava - CollisionDamageableProcessor + this processor must be skipped

class ResolveEntityCollisionsProcessor(Processor):
    ''' Process collisions stored in component FlagHasCollided and do not
    allow to overlap.

    Involved components:
        -   Position
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

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' On collision, return the entity on its original position.
        '''
        self.cycle += 1

        # Get all entities that have collided with something
        for ent, (position, flag_has_collided) in self.world.get_components(Position, FlagHasCollided):

            logger.debug(f'({self.cycle}) - Entity {ent} - original position: [{position.x}, {position.y}]')

            position.x = position.lastx
            position.y = position.lasty
            position.map = position.lastmap

            logger.debug(f'({self.cycle}) - Entity {ent} - new position: [{position.x}, {position.y}]')

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

