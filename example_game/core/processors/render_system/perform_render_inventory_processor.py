__all__ = ['PerformRenderInventoryProcessor']

import logging
import pygame   # for pygame.time, pygame.font and pygame.Color
import random

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.camera import Camera
from core.components.has_inventory import HasInventory
from core.components.renderable_model import RenderableModel
from core.components.flag_show_inventory import FlagShowInventory
from core.components.position import Position
from core.components.weapon import Weapon
from core.components.ammo_pack import AmmoPack

from pyrpg.core.config import FONTS, FRAMES # for GAME_DEBUG_FONT 

# Logger init
logger = logging.getLogger(__name__)

class PerformRenderInventoryProcessor(Processor):
    ''' Draws the inventory onto the screen.
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = ['dragging', 'drag_item_id', 'drag_start_slot_id', 'drag_stop_slot_id']

    def __init__(self, *args, **kwargs):
        ''' Initiation of PerformRenderInventoryProcessor processor.
        '''
        super().__init__(*args, **kwargs)
        
        # Keep dragging information
        self.dragging = False
        self.drag_item_id = None
        self.drag_start_slot_id = None
        self.drag_stop_slot_id = None
        self.drag_item_model = None

    def process(self, *args, **kwargs):
        ''' Draw inventory slots on the screen.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Show only if entity has camera and inventory
        for ent, (camera, has_inventory, position, flag_show_inventory) in self.world.get_components(Camera, HasInventory, Position, FlagShowInventory):

            ###
            # Draw the inventory window
            ###
            pygame.draw.rect(
                camera.screen,
                pygame.Color('grey'),
                flag_show_inventory.inv_win_rect
            ) 

            ###
            # Draw the empty slots
            ###
            for inv_slot_rect in flag_show_inventory.inv_slot_rects:
                pygame.draw.rect(
                    camera.screen,
                    pygame.Color('black'),
                    inv_slot_rect
                ) 

            ####
            # Draw the items in the slots
            ####
            for inv_slot_id, inv_slot_rect in enumerate(flag_show_inventory.inv_slot_rects):
                
                # If there is something in the inventory slot, try to print its idle model
                inv_item_entity_id = has_inventory.slots[inv_slot_id]

                if inv_item_entity_id is not None:

                    # Try to get image from model and show it
                    inv_item_model = self.world.try_component(inv_item_entity_id, RenderableModel)

                    if inv_item_model is not None:

                        image = inv_item_model.model.get_idle_image()
                        camera.screen.blit(image, (inv_slot_rect.x, inv_slot_rect.y))

            ####
            # Draw the selection box over the selected item
            ####
            pygame.draw.rect(
                camera.screen,
                pygame.Color('red'),
                flag_show_inventory.inv_slot_border_rects[flag_show_inventory.selected_slot_id],
                2
            ) 

            ####
            # Write the information about the selected item - at least tne entity_alias
            ####
            if has_inventory.slots[flag_show_inventory.selected_slot_id] is not None:
                
                # Gather the information about inventory item
                inv_item_info = ''

                # If weapon, write the info from Weapon component
                inv_item_weapon = self.world.try_component(has_inventory.slots[flag_show_inventory.selected_slot_id], Weapon)
                inv_item_info = inv_item_info + f'Weapon: {inv_item_weapon.type}' if inv_item_weapon else inv_item_info

                # If ammo pack, write the info from AmmoPack component
                inv_item_ammo_pack = self.world.try_component(has_inventory.slots[flag_show_inventory.selected_slot_id], AmmoPack)
                inv_item_info = inv_item_info +  f'For Weapon: {inv_item_ammo_pack.weapon}, Ammo: {inv_item_ammo_pack.type}' if inv_item_ammo_pack else inv_item_info

                # Concatenate the information
                text_surf = FONTS["GAME_INVENTORY_FONT_OBJ"].render(inv_item_info) # Text to Surface
                camera.screen.blit(text_surf[0], (flag_show_inventory.inv_win_rect.x,flag_show_inventory.inv_win_rect.y))


            ###
            # MOUSE CONTROL
            ###

            # Mouse coordinates within the displayable game window
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Keep track about the slot that is in focus of the mouse
            focused_slot_id: int = None

            for inv_slot_id, inv_slot_rect in enumerate(flag_show_inventory.inv_slot_rects):

                # Focus_slot Id is obly slot with some real item
                #if inv_slot_rect.collidepoint(mouse_x, mouse_y) and has_inventory.slots[inv_slot_id] is not None: 

                # Focus slot id can be also empty slot
                if inv_slot_rect.collidepoint(mouse_x, mouse_y): 
                    focused_slot_id = inv_slot_id
                    break


            ###
            # On MOUSE HOVER - show info about the focused item (if not dragging item because it prevents nice showing of the dragged item model)
            ###

            if focused_slot_id is not None and not self.dragging:
                text_surf = FONTS["GAME_DEBUG_FONT_OBJ"].render(f'{inv_slot_id=}, {has_inventory.slots[inv_slot_id]}')
                frame_surf = FRAMES["GAME_DEBUG_FRAME_OBJ"].render(text_surf[0]) # Frame the debug text to surface
                camera.screen.blit(frame_surf, (mouse_x, mouse_y))

            ###
            # On MOUSE DRAGGING in progress - show the dragged item's picture, hide the cursow while dragging
            ###
            if self.dragging:
                # Hide the mouse cursor
                pygame.mouse.set_visible(False)
                camera.screen.blit(self.drag_item_model, (mouse_x - flag_show_inventory.inv_slot_rect.width / 2, mouse_y - flag_show_inventory.inv_slot_rect.height / 2))

            ###
            # On MOUSE CLICK select the slot and process the dragging
            ###

            for event in kwargs.get('events'):

                # Mouse button down (start drag if inside the rect)
                if event.type == pygame.MOUSEBUTTONDOWN:

                    # Start drag if inside the rect
                    if focused_slot_id is not None:
    
                        # Mark the slot id as selected
                        flag_show_inventory.selected_slot_id = focused_slot_id

                        # Mark Start dragging if the focused slot id contains some item
                        if has_inventory.slots[focused_slot_id] is not None:
                            self.dragging = True
                            self.drag_start_slot_id = focused_slot_id
                            self.drag_item_id = has_inventory.slots[focused_slot_id]

                            drag_item_model_comp = self.world.try_component(self.drag_item_id, RenderableModel)
                            if drag_item_model_comp is not None:
                                self.drag_item_model = drag_item_model_comp.model.get_idle_image()

                        print(f"Mouse pressed, initiate dragging from slot {self.drag_start_slot_id} with item {self.drag_item_id} and model {self.drag_item_model}")

                # Mouse button up while dragging (stop drag)
                elif event.type == pygame.MOUSEBUTTONUP and self.dragging:

                    # If released above some slot
                    if focused_slot_id is not None:

                        # Change the selected slot id to the dragging destination slot id
                        flag_show_inventory.selected_slot_id = focused_slot_id
                        print(f"New slot id was selected - target of dragging")

                        # Remember to finish location of the drag
                        self.drag_stop_slot_id = focused_slot_id
                        print(f"Mouse released, drop complete on slot {self.drag_stop_slot_id} with item {self.drag_item_id}")

                        # Exchange start slot and stop slot ids
                        has_inventory.slots[self.drag_start_slot_id] = has_inventory.slots[self.drag_stop_slot_id]
                        has_inventory.slots[self.drag_stop_slot_id] = self.drag_item_id
                        print(f"Exchange of items done")

                    # If mouse button released out of inventory slots areas - drop the item out of the inventory
                    else:
                        
                        # Find some free area for drop
                        drop_coord_x = int(position.x + random.randint(64, 128))
                        drop_coord_y = int(position.y + random.randint(64, 128))
                        drop_coord_map = position.map

                        # Drop by creating Position component for the dropped item
                        inv_item_model = self.world.add_component(
                            self.drag_item_id, 
                            Position(
                                x=drop_coord_x, 
                                y=drop_coord_y, 
                                map=drop_coord_map
                            )
                        )

                        # Safely remove the dragged entity from the HasInventory component
                        has_inventory.remove_by_entity_id(entity_id=self.drag_item_id)

                        # Log the result
                        print(f"Putting {self.drag_item_id} out of inventory")

                    # Show the mouse cursor again
                    pygame.mouse.set_visible(True)

                    # Stop dragging
                    self.dragging = False
                    self.drag_stop_slot_id = None
                    self.drag_start_slot_id = None
                    self.drag_item_id = None
                    self.drag_item_model = None
                    print(f"Mouse released, stopping dragging.")


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
