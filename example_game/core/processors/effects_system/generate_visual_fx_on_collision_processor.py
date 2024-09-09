__all__ = ['GenerateVisualFXOnCollisionProcessor']

import logging
import copy

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.visual_fx_on_collision import VisualFXOnCollision
from pyrpg.core.ecs.components.new.flag_has_collided import FlagHasCollided

# Logger init
logger = logging.getLogger(__name__)

class GenerateVisualFXOnCollisionProcessor(Processor):
    ''' Creates new entity containing visual fx on the collision spot.

    Involved components:
        -   VisualFXOnCollision
        -   FlagHasCollided

    Related processors:
        -   GenerateEntityCollisionsProcessor

    What if this processor is disabled?
        -   visual effect is not shown

    Where the processor should be planned?
        -   after GenerateEntityCollisionsProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.collision_system:GenerateCollisionsProcessor'
    ]

    __slots__ = ['create_entity_fnc']

    def __init__(self, create_entity_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)
        self.create_entity_fnc = create_entity_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the FlagHasCollided flag.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (position, flag_has_collided, vfx_on_collision) in self.world.get_components(Position, FlagHasCollided, VisualFXOnCollision):

            # Create new entity representing the effect
            new_entity = self.create_entity_fnc(
                {
                    "templates" : [vfx_on_collision.effect]
                }
            )

            # Add the correct position - either the position of the effect moves dynamically together with the entity
            # or position of the effect is fixed on one place
            self.world.add_component(
                new_entity, 
                copy.copy(position) if vfx_on_collision.fixed_position else position
            )

            logger.debug(f'({self.cycle}) - Entity {ent} - has produced visual fx entity {new_entity} upon collision.')

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
