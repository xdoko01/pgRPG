__all__ = ['GenerateDestroyOnCollisionProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.destroy_on_collision import DestroyOnCollision
from core.components.flag_has_collided import FlagHasCollided
from core.components.is_destroyed import IsDestroyed


# Logger init
logger = logging.getLogger(__name__)

class GenerateDestroyOnCollisionProcessor(Processor):
    ''' Assigns IsDestroyed flag to the entity that collided and has
    DestroyOnCollision flag.

    Involved components:
        -   DestroyOnCollision
        -   IsDestroyed

    Related processors:
        -   PerformDestroyEntitiesProcessor

    What if this processor is disabled?
        -   entity is not destroyed upon collision

    Where the processor should be planned?
        -   after GenerateEntityCollisionsProcessor
        -   before ResolveEntityCollisionsExProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'collision_system:GenerateCollisionsProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Generates the IsDestroyed component.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (flag_has_collided, destroy_on_collision) in self.world.get_components(FlagHasCollided, DestroyOnCollision):

            self.world.add_component(ent, IsDestroyed(ttl=destroy_on_collision.ttl))

            logger.debug(f'({self.cycle}) - Entity {ent} - flag "IsDestroyed" was added.')

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
