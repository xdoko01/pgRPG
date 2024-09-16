__all__ = ['PerformPickupProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.position import Position
from core.components.camera import Camera
from core.components.has_inventory import HasInventory
from core.components.flag_was_picked_by import FlagWasPickedBy
from core.components.flag_has_picked import FlagHasPicked
from core.components.flag_is_about_to_pick_entity import FlagIsAboutToPickEntity

from pyrpg.functions.dict_utils import add_dict_value, get_dict_value

# For creation of events
from pyrpg.core.events.event import Event

# Logger init
logger = logging.getLogger(__name__)

class PerformPickupProcessor(Processor):
    ''' Detects entities that are about to be picked and performs
    the actual pickup if the picker is capable.

    Involved components:
        -   Position
        -   Camera
        -   HasInventory
        -   FlagWasPickedBy
        -   FlagHasPicked
        -   FlagIsAboutToPickEntity

    Related processors:
        -   GeneratePickupProcessor
        -   RemoveFlagIsAboutToPickEntityProcessor
        -   RemoveFlagWasPickedByProcessor
        -   RemoveFlagHasPickedProcessor

    What if this processor is disabled?
        -   entities are not being picked up

    Where the processor should be planned?
        -   after GeneratePickupProcessor
        -   before NewRemoveFlagPickedByProcessor
        -   before RemoveFlagIsAboutToPickEntityProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.pickup_system.generate_pickup_processor:GeneratePickupProcessor'
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are about to be picked and performs
        the actual pickup if the picker is capable.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Inventory and FlagIsAboutToPickEntity - those are candidates for successful pickers
        for ent_picker, (has_inventory, flag_is_about_to_pick_entity) in self.world.get_components(HasInventory, FlagIsAboutToPickEntity):

            # Add the entity into the HasInventory inventory set
            has_inventory.inventory.add(flag_is_about_to_pick_entity.entity_for_pickup)

            # Add the entity into the HasInventory categories dictionary, if category defined
            if flag_is_about_to_pick_entity.category:
                add_dict_value(has_inventory.categories, flag_is_about_to_pick_entity.category, flag_is_about_to_pick_entity.entity_for_pickup)

            # Remove Position component from the item so that it is not displayable on the map - item is picked
            self.world.remove_component(flag_is_about_to_pick_entity.entity_for_pickup, Position) 

            # Remove Camera component from the item so that the screen disappears - item is picked
            try:
                self.world.remove_component(flag_is_about_to_pick_entity.entity_for_pickup, Camera) 
            except KeyError:
                pass

            # Assign FlagWasPickedBy component to the picked entity
            self.world.add_component(flag_is_about_to_pick_entity.entity_for_pickup, FlagWasPickedBy(picker=ent_picker))
            logger.debug(f'({self.cycle}) - Entity {ent_picker} has picked entity {flag_is_about_to_pick_entity.entity_for_pickup}.')

            # Assign FlagHasPicked component to the picker entity
            self.world.add_component(ent_picker, FlagHasPicked(entity=flag_is_about_to_pick_entity.entity_for_pickup))
            logger.debug(f'({self.cycle}) - Entity {flag_is_about_to_pick_entity.entity_for_pickup} was picked by entity {ent_picker}.')

            # Report that item was picked up - generate event
            pickup_event = Event(
                'ITEM_PICKUP', 
                flag_is_about_to_pick_entity.entity_for_pickup, 
                ent_picker, 
                params={
                    'item' : flag_is_about_to_pick_entity.entity_for_pickup, 
                    'picker' : ent_picker, 
                    'category' :  flag_is_about_to_pick_entity.category,
                    'amount_in_category' : len(get_dict_value(has_inventory.categories, flag_is_about_to_pick_entity.category, not_found=[]))
                }
            )

            self.add_event_fnc(pickup_event)

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

