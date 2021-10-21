__all__ = ['NewPerformRenderDebugInfoProcessor']

import logging
import pygame	# for pygame.time, pygame.font and pygame.Color
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

from ..functions import filter_only_visible # for filtering only entities with position on the cameras
from ..functions import get_arrow_points # for drawing of arrows

from pyrpg.core.config.fonts import GAME_DEBUG_FONT # for the debug font
from pprint import pformat # Nice formating of dictionaries for debug output


# Logger init
logger = logging.getLogger(__name__)

class NewPerformRenderDebugInfoProcessor(esper.Processor):
    ''' Draws the debug information onto the game cameras.

    Input parameters:

    Involved components:
        -   Position
        -   Camera
        -   NewDebug

    Related processors:
        -   whole render system

    What if this processor is disabled?
        -	entities will be not show debug information
    
    Where the processor should be planned?
        -   before NewPerformBlitCameraProcessor - in order to blit debug information from cameras to game window
        -   after NewPerformRenderXXXProcessor - in order to overdraw all rendered graphics
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = []

    def __init__(self):
        ''' Initiation of NewPerformRenderDebugInfoProcessor processor.
        '''
        super().__init__()

    def process(self, *args, **kwargs):
        ''' Draw all sorts of debug information on the screen. The category of information
        is specified in the NewDebug component.
        '''
        self.cycle += 1

        # Show debug information on all cameras
        for _, (camera) in self.world.get_component(components.Camera):

            # Show COLLISION information
            # Show debug information to all entities with Position and NewDebug and NewCollidable component
            for _, (position, debug, collidable) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.NewDebug, components.NewCollidable)):

                pygame.draw.rect(
                    camera.screen,
                    debug.collision.get('color', pygame.Color('blue')), # Color of zone taken from NewDebug component
                    pygame.Rect(
                        camera.apply((position.x + collidable.dx - collidable.x, position.y + collidable.dy - collidable.y)), 
                        (2 * collidable.x, 2 * collidable.y)
                        ),
                    debug.collision.get('width', 1) # Thickness of line taken from NewDebug component
                ) 


            # Show MOVEMENT information
            # Show debug information to all entities with Position, NewDebug and NewMoveable components
            for _, (position, debug, moveable) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.NewDebug, components.NewMovable)):

                pygame.draw.lines(
                    camera.screen,
                    debug.movement.get('color', pygame.Color('red')),
                    False,
                    # list of connected points - add using map the start coordinates to all arrow points and draw it
                    tuple(map(camera.apply, get_arrow_points(position.dir_name, moveable.velocity // 5, (position.x, position.y)))),
                    debug.movement.get('width', 1) # Thickness of movement arrow taken from NewDebug component
                )

            # Experiment with mouse hoover
            # Show debug information to all entities with Position, NewDebug and NewMoveable components
            for _, (position, debug) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.NewDebug)):

                x, y = pygame.mouse.get_pos()

                # if the mouse coursor is near
                if abs(x-position.x) < 30 and abs(y-position.y) < 30:
                    pygame.draw.rect(
                        camera.screen,
                        pygame.Color('red'),
                        pygame.Rect(
                            camera.apply((position.x - 5, position.y + 5)), 
                            (2 * 5, 2 * 5)
                            ),
                        2
                    )


            '''
                # Show position info
                if debug.get('show_position', False):
                    try:
                        pos_debug = self.world.component_for_entity(debug_entity, components.Position)
                        debug_text += f'Pos:({int(pos_debug.x)}, {int(pos_debug.y)})\nDir: {pos_comp.dir_name}\n'
                    except KeyError:
                        pass

                # Show model status info
                if debug.get('show_state', False):
                    try:
                        state_debug = self.world.component_for_entity(debug_entity, components.RenderableModel)
                        debug_text += f'State: {state_debug.action}\n'
                    except KeyError:
                        pass

                # Show health info
                if debug.get('show_health', False):
                    try:
                        damageable_debug = self.world.component_for_entity(debug_entity, components.Damageable)
                        debug_text += f'Health: {damageable_debug.health}\n'
                    except KeyError:
                        pass

                # Show inventory info
                if debug.get('show_inventory', False):
                    try:
                        inventory_debug = self.world.component_for_entity(debug_entity, components.HasInventory)
                        debug_text += f'Inventory: {pformat(inventory_debug.inventory)}\n'
                    except KeyError:
                        pass

                # Show new inventory info
                if debug.get('show_inventory', False):
                    try:
                        inventory_debug = self.world.component_for_entity(debug_entity, components.NewHasInventory)
                        debug_text += f'Inventory: {pformat(inventory_debug.inventory)}\n'
                    except KeyError:
                        pass

                # Show wearables info
                if debug.get('show_wearables', False):
                    try:
                        wearables_debug = self.world.component_for_entity(debug_entity, components.CanWear)
                        debug_text += f'Wearables:\n{pformat(wearables_debug.wearables, width=50)}\n'
                    except KeyError:
                        pass

                # Show weapons info
                if debug.get('show_weapons', False):
                    try:
                        weapons_debug = self.world.component_for_entity(debug_entity, components.HasWeapon)
                        debug_text += f'Weapon in use: {weapons_debug.get_weapon_in_use()}\nAll weapons:\n{pformat(weapons_debug.weapons, width=50)}\n'
                    except KeyError:
                        pass

                
                # Blit debug text info gathered above - except brain process
                text_surf = GAME_DEBUG_FONT.render(debug_text) # Text to Surface
                cam_cam.screen.blit(
                    text_surf,
                    cam_cam.apply(
                        (pos_comp.x - text_surf.get_width() // 2, pos_comp.y - text_surf.get_height())
                        )
                    )

                
                # Show brain processing
                if debug.get('show_brain', False):
                    try:
                        brain_debug = self.world.component_for_entity(debug_entity, components.Brain)
                        for cmd_idx, cmd_txt in enumerate(brain_debug.commands):
                            color = pygame.Color('red') if cmd_idx == brain_debug.current_cmd_idx else pygame.Color('white')
                            cmd_surf = GAME_DEBUG_FONT.render(f'{cmd_idx} -> {cmd_txt}', color=color)
                            cam_cam.screen.blit(
                                cmd_surf, 
                                cam_cam.apply(
                                    (pos_comp.x, pos_comp.y + (cmd_idx * GAME_DEBUG_FONT._get_text_height()))
                                    )
                                )
                    except KeyError:
                        pass
                

            # Show the area of the displayed map
            if debug.get('show_map_screen_area', False):
                map_display_area = GAME_DEBUG_FONT.render(f'({int(cam_cam.map_screen_rect[0])}, {int(cam_cam.map_screen_rect[1])})', color=pygame.Color('white'))
                cam_cam.screen.blit(map_display_area, (0,0))
            

            # Blit the camera screen on the main game window
            self.window.blit(cam_cam.screen, (cam_cam.screen_pos_x, cam_cam.screen_pos_y))
            '''

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