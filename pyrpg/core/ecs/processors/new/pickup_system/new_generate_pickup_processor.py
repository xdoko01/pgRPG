__all__ = ['NewGeneratePickupProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.pickable import Pickable
from pyrpg.core.ecs.components.new.new_flag_has_collided import NewFlagHasCollided
from pyrpg.core.ecs.components.new.new_flag_is_about_to_pick_entity import NewFlagIsAboutToPickEntity

# Logger init
logger = logging.getLogger(__name__)

class NewGeneratePickupProcessor(Processor):
    ''' Detects entities that are pickable + have collided and assignes
    the NewFlagIsAboutToPickEntity to their pickers.

    Involved components:
        -   Pickable
        -   NewFlagHasCollided
        -   NewFlagIsAboutToPickEntity

    Related processors:
        -   NewPerformPickupProcessor
        -   NewRemoveFlagIsAboutToPickEntityProcessor

    What if this processor is disabled?
        -   entities are not being picked up

    Where the processor should be planned?
        -   after NewGenerateEntityCollisionsProcessor
        -   before NewPerformPickupProcessor
        -   before NewRemoveFlagIsAboutToPickEntityProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.collision_system.new_generate_entity_collisions_processor:NewGenerateEntityCollisionsProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are pickable + have collided and assigns
        the NewFlagIsAboutToPickEntity to their pickers
        '''
        self.cycle += 1

        # Get all entities that have Pickable and NewFlagHasCollided - those are candidates for pickup
        for ent_pickable, (pickable, flag_has_collided) in self.world.get_components(Pickable, NewFlagHasCollided):

            # Assign the NewFlagIsAboutToPickEntity to ALL entities that collided with pickable entity ent
            for ent_picker, _, _, _ in flag_has_collided.collisions:

                self.world.add_component(ent_picker, NewFlagIsAboutToPickEntity(entity_for_pickup=ent_pickable))
                logger.debug(f'({self.cycle}) - Entity {ent_picker} is trying to pick entity {ent_pickable}.')

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

