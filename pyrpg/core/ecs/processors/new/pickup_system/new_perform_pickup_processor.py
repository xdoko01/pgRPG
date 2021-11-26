__all__ = ['NewPerformPickupProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.camera import Camera
from pyrpg.core.ecs.components.new.new_has_inventory import NewHasInventory
from pyrpg.core.ecs.components.new.new_flag_was_picked_by import NewFlagWasPickedBy
from pyrpg.core.ecs.components.new.new_flag_has_picked import NewFlagHasPicked
from pyrpg.core.ecs.components.new.new_flag_is_about_to_pick_entity import NewFlagIsAboutToPickEntity

# For creation of events
from pyrpg.core.events.event import Event

# Logger init
logger = logging.getLogger(__name__)

class NewPerformPickupProcessor(Processor):
    ''' Detects entities that are about to be picked and performs
    the actual pickup if the picker is capable.

    Involved components:
        -   Position
        -   Camera
        -   NewHasInventory
        -   NewFlagWasPickedBy
        -   NewFlagHasPicked
        -   NewFlagIsAboutToPickEntity

    Related processors:
        -   NewGeneratePickupProcessor
        -   NewRemoveFlagIsAboutToPickEntityProcessor
        -   NewRemoveFlagWasPickedByProcessor
        -   NewRemoveFlagHasPickedProcessor

    What if this processor is disabled?
        -   entities are not being picked up

    Where the processor should be planned?
        -   after NewGeneratePickupProcessor
        -   before NewRemoveFlagPickedByProcessor
        -   before NewRemoveFlagIsAboutToPickEntityProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.pickup_system.new_generate_pickup_processor:NewGeneratePickupProcessor'
    ]

    def __init__(self, add_event_fnc):
        ''' Init the processor.
        '''
        super().__init__()

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are about to be picked and performs
        the actual pickup if the picker is capable.
        '''
        self.cycle += 1

        # Get all entities that have Inventory and NewFlagIsAboutToPickEntity - those are candidates for successful pickers
        for ent_picker, (has_inventory, flag_is_about_to_pick_entity) in self.world.get_components(NewHasInventory, NewFlagIsAboutToPickEntity):

            # Add the entity into the NewHasInventory inventory set
            has_inventory.inventory.add(flag_is_about_to_pick_entity.entity_for_pickup)

            # Remove Position component from the item so that it is not displayable on the map - item is picked
            self.world.remove_component(flag_is_about_to_pick_entity.entity_for_pickup, Position) 

            # Remove Camera component from the item so that the screen disappears - item is picked
            try:
                self.world.remove_component(flag_is_about_to_pick_entity.entity_for_pickup, Camera) 
            except KeyError:
                pass

            # Assign NewFlagWasPickedBy component to the picked entity
            self.world.add_component(flag_is_about_to_pick_entity.entity_for_pickup, NewFlagWasPickedBy(picker=ent_picker))
            logger.debug(f'({self.cycle}) - Entity {ent_picker} has picked entity {flag_is_about_to_pick_entity.entity_for_pickup}.')

            # Assign NewFlagHasPicked component to the picker entity
            self.world.add_component(ent_picker, NewFlagHasPicked(entity=flag_is_about_to_pick_entity.entity_for_pickup))
            logger.debug(f'({self.cycle}) - Entity {flag_is_about_to_pick_entity.entity_for_pickup} was picked by entity {ent_picker}.')

            # Report that item was picked up - generate event
            pickup_event = Event('ITEM_PICKUP', flag_is_about_to_pick_entity.entity_for_pickup, ent_picker, params={'item' : flag_is_about_to_pick_entity.entity_for_pickup, 'picker' : ent_picker})
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

