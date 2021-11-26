__all__ = ['RenderDebugProcessorFullScan']

import pygame

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.original.position import Position
from pyrpg.core.ecs.components.original.debug import Debug
from pyrpg.core.ecs.components.original.renderable import Renderable
from pyrpg.core.ecs.components.original.has_inventory import HasInventory
from pyrpg.core.ecs.components.original.labeled import Labeled
from pyrpg.core.ecs.components.original.brain import Brain
from pyrpg.core.ecs.components.original.collidable import Collidable

class RenderDebugProcessorFullScan(Processor):
    ''' Information displayed only on visible entities
    using the filter_only_visible function.
    '''

    def __init__(self, window):

        super().__init__()
        self.window = window
        self.font = pygame.font.Font(None, 14)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):

        # Get information about required debug information
        debug = kwargs.get('debug', {})

        # Show debug information on all cameras
        for _, (cam_cam) in self.world.get_component(Camera):

            # Show debug information only for displayable entities with Debug flag - only for visible entities
            for debug_entity, (pos_comp, deb_comp, render_comp) in self.world.get_components(Position, Debug, Renderable):

                # Print inventory
                if debug.get('show_inventory', False):
                    try:
                        inventory_debug = self.world.component_for_entity(debug_entity, HasInventory)
                        text = f'Inventory: {inventory_debug.inventory}'
                        pos = deb_comp.font.render(text, True, pygame.Color('black'))
                        cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 20))))
                    except KeyError:
                        pass

                # Print labels
                if debug.get('show_labels', False):
                    try:
                        label_debug = self.world.component_for_entity(debug_entity, Labeled)
                        text = str(debug_entity) + ', ' + str(label_debug.id) + ', ' + str(label_debug.name)
                        pos = deb_comp.font.render(text, True, pygame.Color('black'))
                        cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 10))))
                    except KeyError:
                        pass

                
                # Print position
                if debug.get('show_position', False):
                    try:
                        pos_debug = self.world.component_for_entity(debug_entity, Position)
                        text = 'Pos: (' + str(int(pos_debug.x)) + ', ' + str(int(pos_debug.y)) + ')' + str(pos_comp.dir_name)
                        pos = deb_comp.font.render(text, True, pygame.Color('white'))
                        cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y))))
                    except KeyError:
                        pass

                # Print brain
                if debug.get('show_brain', False):
                    try:
                        brain_debug = self.world.component_for_entity(debug_entity, Brain)
                        for cmd_idx, cmd_txt in enumerate(brain_debug.commands):
                            color = pygame.Color('red') if cmd_idx == brain_debug.current_cmd_idx else pygame.Color('white')
                            cmd = deb_comp.font.render(str(cmd_idx) + ' -> ' + str(cmd_txt), True, color)
                            cam_cam.screen.blit(cmd, cam_cam.apply(render_comp.topleft((pos_comp.x, 10 + pos_comp.y + (cmd_idx * 10)))))
                    except KeyError:
                        pass

                # Print collision area
                if debug.get('show_collision', False):
                    try:
                        coll_debug = self.world.component_for_entity(debug_entity, Collidable)
                        pygame.draw.rect(cam_cam.screen, pygame.Color('blue'), pygame.Rect(cam_cam.apply((pos_comp.x - coll_debug.x,pos_comp.y - coll_debug.y)), (2 * coll_debug.x, 2 *coll_debug.y)),1)
                    except KeyError:
                        pass

                # Print direction of entity
                if debug.get('show_direction', False):
                    try:
                        pygame.draw.line(cam_cam.screen, pygame.Color('red'), 
                            cam_cam.apply((pos_comp.x, pos_comp.y)),
                            cam_cam.apply((pos_comp.x + pos_comp.direction[0] * 20, pos_comp.y + pos_comp.direction[1] * 20)),
                            2)
                    except KeyError:
                        pass

            if debug.get('show_map_screen_area', False):
                map_display_area = self.font.render(str(cam_cam.map_screen_rect), True, pygame.Color('white'))
                cam_cam.screen.blit(map_display_area, (0,0))

            # Blit the camera screen on the main game window
            self.window.blit(cam_cam.screen, (cam_cam.screen_pos_x, cam_cam.screen_pos_y))

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components (window).
        '''
        self.window = None
        self.font = None


    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the reference to window again.
        '''
        self.window = window
        self.font = pygame.font.Font(None, 14)