__all__ = ['PerformDestroyEntitiesProcessor']

import logging
from pygame.time import get_ticks

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.is_destroyed import IsDestroyed

# Logger init
logger = logging.getLogger(__name__)

class PerformDestroyEntitiesProcessor(Processor):
    ''' Deletes entities marked for deletion after defined
    period of time.

    Involved components:
        -   IsDestroyed

    Related processors:
        -   PerformDestroyOnCollisionProcessor

    What if this processor is disabled?
        -   entities (e.g. projectiles) are not destroyed

    Where the processor should be planned?
        -   after PerformDestroyOnCollisionProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.destroy_system.perform_destroy_on_collision_processor:PerformDestroyOnCollisionProcessor',
        'new.destroy_system.perform_destroy_on_stopped_movement_processor:PerformDestroyOnStoppedMovementProcessor'
    ]

    __slots__ = []

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Get all IsDestroyed components and based on ttl remove
        corresponding entities from the world.
        '''
        self.cycle += 1

        # Select all entities that have been destroyed in this cycle
        for ent, (is_destroyed) in self.world.get_component(IsDestroyed):

            # if the time is up, destroy the entity
            logger.debug(f'({self.cycle}) - Entity {ent} - get_ticks {get_ticks()}, destroyed_time {is_destroyed.destroyed_time}, ttl {is_destroyed.ttl}')

            if get_ticks() - is_destroyed.destroyed_time > is_destroyed.ttl:
                self.world.delete_entity(ent)
                # Log information about successful removal
                logger.debug(f'({self.cycle}) - Entity {ent} was deleted from the world.')
