__all__ = ['GenerateCommandFromMouseProcessor']

import logging
import pygame   # for pygame.time, pygame.font and pygame.Color

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_show_inventory import FlagShowInventory
from core.components.has_inventory import HasInventory
from core.components.renderable_model import RenderableModel


from pyrpg.core.config import FONTS, FRAMES # for GAME_DEBUG_FONT 

# Logger init
logger = logging.getLogger(__name__)

class GenerateCommandFromMouseProcessor(Processor):
    ''' Generates the commands based on mouse input
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = ['dragging', 'drag_item_id', 'drag_start_slot_id', 'drag_stop_slot_id']

    def __init__(self, FNC_ADD_COMMAND, *args, **kwargs):
        ''' Initiation of GenerateCommandFromMouseProcessor processor.

        Parameters:
            :param add_command_fnc: Reference to the function that adds command to the command queue.
            :param add_command_fnc: reference
        '''
        super().__init__(*args, **kwargs)

        # Reference to function for adding to command queue
        self.add_command_fnc = FNC_ADD_COMMAND

        # Keep dragging information - moved to flag_show_inventory in order to keep info for rendering
        '''
        self.dragging = False
        self.drag_item_id = None
        self.drag_start_slot_id = None
        self.drag_stop_slot_id = None
        self.drag_item_model = None
        '''

    def process(self, *args, **kwargs):
        ''' Trigger commands based on the mouse input.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Specify the component results for hinting parameters in VS studio
        flag_show_inventory: FlagShowInventory
        has_inventory: HasInventory
        
        # For handling mouse INVENTORY MANIPULATION commands
        for ent, (has_inventory, flag_show_inventory) in self.world.get_components(HasInventory, FlagShowInventory):

            # Mouse coordinates within the displayable game window
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Keep track about the slot that is in focus of the mouse
            flag_show_inventory.mouse_focused_slot_id = None

            # Determine which inventory slot is focused with tne mouse cursor and remember it
            for inv_slot_id, inv_slot_rect in enumerate(flag_show_inventory.inv_slot_rects):

                # Focus slot id can be also empty slot
                if inv_slot_rect.collidepoint(mouse_x, mouse_y): 
                    flag_show_inventory.mouse_focused_slot_id = inv_slot_id
                    break

            # PROCESS the mouse events
            for event in kwargs.get('events'):

                # Mouse button down (start drag if inside the rect)
                if event.type == pygame.MOUSEBUTTONDOWN:

                    # Start drag if inside the rect
                    if flag_show_inventory.mouse_focused_slot_id is not None:
    
                        # Mark the slot id as selected
                        flag_show_inventory.selected_slot_id = flag_show_inventory.mouse_focused_slot_id

                        # Mark Start dragging if the focused slot id contains some item
                        if has_inventory.slots[flag_show_inventory.mouse_focused_slot_id] is not None:
                            flag_show_inventory.dragging = True
                            flag_show_inventory.drag_start_slot_id = flag_show_inventory.mouse_focused_slot_id
                            flag_show_inventory.drag_item_id = has_inventory.slots[flag_show_inventory.mouse_focused_slot_id]

                            drag_item_model_comp: RenderableModel
                            drag_item_model_comp = self.world.try_component(flag_show_inventory.drag_item_id, RenderableModel)
                            if drag_item_model_comp is not None:
                                flag_show_inventory.drag_item_model = drag_item_model_comp.model.get_idle_image()

                        logger.debug(f"Mouse pressed, initiate dragging from slot {flag_show_inventory.drag_start_slot_id} with item {flag_show_inventory.drag_item_id} and model {flag_show_inventory.drag_item_model}")

                # Mouse button up while dragging (stop drag)
                elif event.type == pygame.MOUSEBUTTONUP and flag_show_inventory.dragging:

                    # If released above some slot
                    if flag_show_inventory.mouse_focused_slot_id is not None:

                        # Change the selected slot id to the dragging destination slot id
                        flag_show_inventory.selected_slot_id = flag_show_inventory.mouse_focused_slot_id
                        logger.debug(f"New slot id was selected - target of dragging")

                        # Remember to finish location of the drag
                        flag_show_inventory.drag_stop_slot_id = flag_show_inventory.mouse_focused_slot_id
                        logger.debug(f"Mouse released, drop complete on slot {flag_show_inventory.drag_stop_slot_id} with item {flag_show_inventory.drag_item_id}")

                        # Exchange start slot and stop slot ids
                        has_inventory.slots[flag_show_inventory.drag_start_slot_id] = has_inventory.slots[flag_show_inventory.drag_stop_slot_id]
                        has_inventory.slots[flag_show_inventory.drag_stop_slot_id] = flag_show_inventory.drag_item_id
                        logger.debug(f"Exchange of items done")

                    # If mouse button released out of inventory slots areas - drop the item out of the inventory
                    else:
                        from pyrpg.core.commands import Command

                        # add DROP_ITEM command to the command queue
                        self.add_command_fnc(cmd=Command('drop_item', {'item_entity_id': flag_show_inventory.drag_item_id}, ent), orig_entity_id=ent)
                        logger.debug(f'({self.cycle}) - Entity {ent} - drop_item sent to the command manager - from mouse. {flag_show_inventory.drag_item_id}')

                        
                    # Show the mouse cursor again after dropping is done
                    pygame.mouse.set_visible(True)

                    # Stop dragging
                    flag_show_inventory.dragging = False
                    flag_show_inventory.drag_stop_slot_id = None
                    flag_show_inventory.drag_start_slot_id = None
                    flag_show_inventory.drag_item_id = None
                    flag_show_inventory.drag_item_model = None
                    logger.debug(f"Mouse released, stopping dragging.")


    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components.
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
