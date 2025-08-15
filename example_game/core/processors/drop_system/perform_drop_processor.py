__all__ = ['PerformDropProcessor']

import logging
import random

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.position import Position
from core.components.collidable import Collidable

from core.components.has_inventory import HasInventory
from core.components.flag_was_dropped_by import FlagWasDroppedBy
from core.components.flag_has_dropped import FlagHasDropped
from core.components.flag_is_about_to_drop_entity import FlagIsAboutToDropEntity

from pyrpg.functions.dict_utils import add_dict_value, get_dict_value

# For creation of events
from pyrpg.core.events.event import Event

# Logger init
logger = logging.getLogger(__name__)

class PerformDropProcessor(Processor):
    ''' Detects entities that are about to be dropped and performs
    the actual drop if possible.

    Involved components:
        -   Position
        -   Camera
        -   HasInventory
        -   FlagWasDroppedBy
        -   FlagHasDropped
        -   FlagIsAboutToDropEntity

    Related processors:
        -   RemoveFlagIsAboutToDropEntityProcessor
        -   RemoveFlagWasDroppedByProcessor
        -   RemoveFlagHasDroppedProcessor

    What if this processor is disabled?
        -   entities are not being dropped

    Where the processor should be planned?
        -   before RemoveFlagDroppedByProcessor
        -   before RemoveFlagIsAboutToDropEntityProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc


    def process(self, *args, **kwargs):
        '''  Detects entities that are about to be dropped and performs
        the actual drop, if possible.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Inventory and FlagIsAboutToDropEntity - those are candidates for successful droppers
        for ent_dropper, (has_inventory, position, flag_is_about_to_drop_entity, collidable) in self.world.get_components_opt(HasInventory, Position, FlagIsAboutToDropEntity, optional=Collidable):

            # Remove the item from HasInventory
            has_inventory.remove_by_entity_id(entity_id=flag_is_about_to_drop_entity.entity_for_drop)

            '''Find free space to drop the entity
                - 8 positions for drop - randomly select one from it - sort them randomly
                - iterate all entities with Position component and Collidable component.
                - for all those check if the candidate position is colliding with some entity
                - additionally check if colliding with some tile
                - if all above is ok, place drop the entity there
                - if one of above is wrong, select from the next 7 positions and return the above
                - if you are at the last posiition and it cannot be used, place it there anyways.
            '''
            # Get the Collidable component for dropped entity if there is any
            collidable_dropped = self.world.try_component(flag_is_about_to_drop_entity.entity_for_drop, Collidable)
            collidable_dropped_x = (collidable_dropped.x + collidable_dropped.dx) if collidable_dropped is not None else 0
            collidable_dropped_y = (collidable_dropped.y + collidable_dropped.dy) if collidable_dropped is not None else 0

            # Get the Collidable component for dropper entity if there is any
            collidable_dropper_x = (collidable.x + collidable.dx) if collidable is not None else 0
            collidable_dropper_y = (collidable.y + collidable.dy) if collidable is not None else 0

            # 8 possible positions for drop - shuffle them randomly
            drop_pos_dirs = [
                (-1,-1), #TopLeft
                (0,-1), #TopCenter
                (1,-1), #TopRight
                (-1,0), # CenterLeft
                (1,0), # CenterRight
                (-1,1), #BottomLeft
                (0,1), #BottomCenter
                (1,1), #BottomRight
            ]

            # Shuffle the positions randomly
            random.shuffle(drop_pos_dirs)

            # Initiate search for the non problematic position
            drop_pos_x = None
            drop_pos_y = None
            drop_pos_map = None
            
            # Try if the possition in given direction is available, if not continue with next one
            for drop_pos_dir in drop_pos_dirs:

                # Calculate the candidate position
                drop_pos_x = position.x + (drop_pos_dir[0] * collidable_dropper_x) + (drop_pos_dir[0] * collidable_dropped_x)
                drop_pos_y = position.y + (drop_pos_dir[1] * collidable_dropper_y) + (drop_pos_dir[1] * collidable_dropped_y)
                drop_pos_map = position.map

                # Iterate all entities with Position component and Collidable component.
                for ent_col, (position_col, collidable_col) in self.world.get_components(Position, Collidable):

                    # Check if the dropped item position might be colliding with some other collidable entity
                    # AABB comaprison - if Collision happened - try another direction
                    if (drop_pos_map == position_col.map and
                        drop_pos_x + collidable_dropped.dx - collidable_dropped.x < position_col.x + collidable_col.dx + collidable_col.x and
                        drop_pos_x + collidable_dropped.dx + collidable_dropped.x > position_col.x + collidable_col.dx - collidable_col.x and
                        drop_pos_y + collidable_dropped.dy - collidable_dropped.y < position_col.y + collidable_col.dy + collidable_col.y and
                        drop_pos_y + collidable_dropped.dy + collidable_dropped.y > position_col.y + collidable_col.dy - collidable_col.y):

                        logger.debug(f'({self.cycle}) - Entity {flag_is_about_to_drop_entity.entity_for_drop} has collided with Entity {ent_col}.')
                        break # try next direction

                    # Check if additionally colliding with some tile
                
                # If everything went ok, end
                break
            
            # Create Position on the found non problematic coordinates or the last coordinates
            self.world.add_component(
                flag_is_about_to_drop_entity.entity_for_drop, 
                Position(
                    x=drop_pos_x, 
                    y=drop_pos_y, 
                    map=drop_pos_map
                )
            )

            '''
            # Find some free area for drop
            drop_coord_x = int(position.x + random.randint(64, 128))
            drop_coord_y = int(position.y + random.randint(64, 128))
            drop_coord_map = position.map

            # Drop by creating Position component for the dropped item
            self.world.add_component(
                flag_is_about_to_drop_entity.entity_for_drop, 
                Position(
                    x=drop_coord_x, 
                    y=drop_coord_y, 
                    map=drop_coord_map
                )
            )
            '''

            # Assign FlagWasDroppedBy component to the dropped entity
            self.world.add_component(flag_is_about_to_drop_entity.entity_for_drop, FlagWasDroppedBy(dropper=ent_dropper))
            logger.debug(f'({self.cycle}) - Entity {ent_dropper} has dropped entity {flag_is_about_to_drop_entity.entity_for_drop}.')

            # Assign FlagHasDropped component to the dropper entity
            self.world.add_component(ent_dropper, FlagHasDropped(entity=flag_is_about_to_drop_entity.entity_for_drop))
            logger.debug(f'({self.cycle}) - Entity {flag_is_about_to_drop_entity.entity_for_drop} was dropped by entity {ent_dropper}.')

            # Report that item was dropped - generate event
            pickup_event = Event(
                'ITEM_DROP', 
                flag_is_about_to_drop_entity.entity_for_drop, 
                ent_dropper, 
                params={
                    'item' : flag_is_about_to_drop_entity.entity_for_drop, 
                    'dropper' : ent_dropper
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

