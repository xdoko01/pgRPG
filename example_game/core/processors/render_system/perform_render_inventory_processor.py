__all__ = ['PerformRenderInventoryProcessor']

import logging
import pygame   # for pygame.time, pygame.font and pygame.Color

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.camera import Camera
from core.components.has_inventory import HasInventory
from core.components.renderable_model import RenderableModel
from core.components.flag_show_inventory import FlagShowInventory
from core.components.weapon import Weapon
from core.components.ammo_pack import AmmoPack

from pgrpg.core.config import FONTS, FRAMES # for GAME_DEBUG_FONT 

# Logger init
logger = logging.getLogger(__name__)

class PerformRenderInventoryProcessor(Processor):
    ''' Draws the inventory onto the screen.
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Initiation of PerformRenderInventoryProcessor processor.
        '''
        super().__init__(*args, **kwargs)
        
    def process(self, *args, **kwargs):
        ''' Draw inventory slots on the screen.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        camera: Camera
        has_inventory: HasInventory
        flag_show_inventory: FlagShowInventory

        # Show only if entity has camera and inventory
        for ent, (camera, has_inventory, flag_show_inventory) in self.world.get_components(Camera, HasInventory, FlagShowInventory):

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
                    inv_item_model: RenderableModel
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
                inv_item_weapon: Weapon
                inv_item_weapon = self.world.try_component(has_inventory.slots[flag_show_inventory.selected_slot_id], Weapon)
                inv_item_info = inv_item_info + f'Weapon: {inv_item_weapon.type}' if inv_item_weapon else inv_item_info

                # If ammo pack, write the info from AmmoPack component
                inv_item_ammo_pack: AmmoPack
                inv_item_ammo_pack = self.world.try_component(has_inventory.slots[flag_show_inventory.selected_slot_id], AmmoPack)
                inv_item_info = inv_item_info +  f'For Weapon: {inv_item_ammo_pack.weapon}, Ammo: {inv_item_ammo_pack.type}' if inv_item_ammo_pack else inv_item_info

                # Concatenate the information
                text_surf = FONTS["GAME_INVENTORY_FONT_OBJ"].render(inv_item_info) # Text to Surface
                camera.screen.blit(text_surf[0], (flag_show_inventory.inv_win_rect.x,flag_show_inventory.inv_win_rect.y))


            mouse_x, mouse_y = pygame.mouse.get_pos()

            ###
            # On MOUSE HOVER - show info about the focused item (if not dragging item because it prevents nice showing of the dragged item model)
            ###

            if flag_show_inventory.mouse_focused_slot_id is not None and not flag_show_inventory.dragging:
                text_surf = FONTS["GAME_DEBUG_FONT_OBJ"].render(f'Slot ID: {flag_show_inventory.mouse_focused_slot_id}, Entity ID: {has_inventory.slots[flag_show_inventory.mouse_focused_slot_id]}')
                frame_surf = FRAMES["GAME_DEBUG_FRAME_OBJ"].render(text_surf[0]) # Frame the debug text to surface
                camera.screen.blit(frame_surf, (mouse_x, mouse_y))

            ###
            # On MOUSE DRAGGING in progress - show the dragged item's picture, hide the cursow while dragging
            ###
            if flag_show_inventory.dragging:
                camera.screen.blit(flag_show_inventory.drag_item_model, (mouse_x - flag_show_inventory.inv_slot_rect.width / 2, mouse_y - flag_show_inventory.inv_slot_rect.height / 2))

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
