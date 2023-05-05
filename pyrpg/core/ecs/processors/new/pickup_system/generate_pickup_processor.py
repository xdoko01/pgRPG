__all__ = ['GeneratePickupProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.new.pickable import Pickable
from pyrpg.core.ecs.components.new.flag_has_collided import FlagHasCollided
from pyrpg.core.ecs.components.new.flag_is_about_to_pick_entity import FlagIsAboutToPickEntity

# Logger init
logger = logging.getLogger(__name__)

class GeneratePickupProcessor(Processor):
    ''' Detects entities that are pickable + have collided and assignes
    the FlagIsAboutToPickEntity to their pickers.

    Involved components:
        -   Pickable
        -   FlagHasCollided
        -   FlagIsAboutToPickEntity

    Related processors:
        -   PerformPickupProcessor
        -   RemoveFlagIsAboutToPickEntityProcessor

    What if this processor is disabled?
        -   entities are not being picked up

    Where the processor should be planned?
        -   after GenerateEntityCollisionsProcessor
        -   before PerformPickupProcessor
        -   before RemoveFlagIsAboutToPickEntityProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.collision_system:GenerateCollisionsProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are pickable + have collided and assigns
        the FlagIsAboutToPickEntity to their pickers
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Pickable and FlagHasCollided - those are candidates for pickup
        for ent_pickable, (pickable, flag_has_collided) in self.world.get_components(Pickable, FlagHasCollided):

            # Assign the FlagIsAboutToPickEntity to ALL entities that collided with pickable entity ent
            #for ent_picker, *_ in flag_has_collided.collisions:
            for collision in flag_has_collided.collisions:

                self.world.add_component(collision.entity, FlagIsAboutToPickEntity(entity_for_pickup=ent_pickable, category=pickable.category))
                logger.debug(f'({self.cycle}) - Entity {collision.entity} is trying to pick entity {ent_pickable} with category {pickable.category}.')

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization by attaching
        the removed references again.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass

