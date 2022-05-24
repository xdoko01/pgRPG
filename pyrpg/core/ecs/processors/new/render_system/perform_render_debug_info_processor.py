__all__ = ['PerformRenderDebugInfoProcessor']

import logging
import pygame   # for pygame.time, pygame.font and pygame.Color

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.camera import Camera
from pyrpg.core.ecs.components.new.debug import Debug
from pyrpg.core.ecs.components.new.has_inventory import HasInventory
from pyrpg.core.ecs.components.new.renderable_model import RenderableModel
from pyrpg.core.ecs.components.new.movable import Movable
from pyrpg.core.ecs.components.new.collidable import Collidable
from pyrpg.core.ecs.components.new.damageable import Damageable
from pyrpg.core.ecs.components.new.has_score import HasScore


from ..functions import filter_only_visible # for filtering only entities with position on the cameras
from ..functions import get_arrow_points # for drawing of arrows

from pyrpg.core.config.fonts import GAME_DEBUG_FONT # for the debug font
from pyrpg.core.config.frames import GAME_DEBUG_FRAME # for the debug frame

from pprint import pformat # Nice formating of dictionaries for debug output

# Logger init
logger = logging.getLogger(__name__)

class PerformRenderDebugInfoProcessor(Processor):
    ''' Draws the debug information onto the game cameras.

    Input parameters:

    Involved components:
        -   Position
        -   Camera
        -   Debug
        -   RenderableModel
        -   HasInventory
        -   Movable
        -   Collidable
        -   Damageable
        -   HasScore

    Related processors:
        -   whole render system

    What if this processor is disabled?
        -   entities will be not show debug information
    
    Where the processor should be planned?
        -   before PerformBlitCameraProcessor - in order to blit debug information from cameras to game window
        -   after NewPerformRenderXXXProcessor - in order to overdraw all rendered graphics
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = []

    def __init__(self):
        ''' Initiation of PerformRenderDebugInfoProcessor processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Draw all sorts of debug information on the screen. The category of information
        is specified in the Debug component.
        '''
        self.cycle += 1

        # Show debug information on all cameras
        for _, (camera) in self.world.get_component(Camera):

            # Get position and model status info
            for _, (position, debug, renderable) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(Position, Debug, RenderableModel)):
                debug.info.update({'position' : (int(position.x), int(position.y), position.dir_name)})
                debug.info.update({'action' : renderable.action})

            # Get inventory info
            for _, (position, debug, inventory) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(Position, Debug, HasInventory)):
                debug.info.update({'inventory' : inventory.inventory})

            # Get health info
            for _, (position, debug, damageable) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(Position, Debug, Damageable)):
                debug.info.update({'Health' : damageable.health})

            # Get score info
            for _, (position, debug, has_score) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(Position, Debug, HasScore)):
                debug.info.update({'Score' : has_score.score})

            # Show COLLISION information
            # Show debug information to all entities with Position and Debug and Collidable component
            for _, (position, debug, collidable) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(Position, Debug, Collidable)):

                pygame.draw.rect(
                    camera.screen,
                    debug.collision.get('color', pygame.Color('blue')), # Color of zone taken from Debug component
                    pygame.Rect(
                        camera.apply((position.x + collidable.dx - collidable.x, position.y + collidable.dy - collidable.y)), 
                        (2 * collidable.x, 2 * collidable.y)
                        ),
                    debug.collision.get('width', 1) # Thickness of line taken from Debug component
                ) 

            # Show MOVEMENT information
            # Show debug information to all entities with Position, Debug and NewMoveable components
            for _, (position, debug, moveable) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(Position, Debug, Movable)):

                pygame.draw.lines(
                    camera.screen,
                    debug.movement.get('color', pygame.Color('red')),
                    False,
                    # list of connected points - add using map the start coordinates to all arrow points and draw it
                    tuple(map(camera.apply, get_arrow_points(position.dir_name, moveable.velocity // 5, (position.x, position.y)))),
                    debug.movement.get('width', 1) # Thickness of movement arrow taken from Debug component
                )

            # Experiment with mouse hoover
            # Show debug information to all entities with Position, Debug and NewMoveable components
            for _, (position, debug) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(Position, Debug)):

                # Mouse coordinates within the displayable game window
                x, y = pygame.mouse.get_pos()

                # Position transformed to the game window based on camera
                pos_cam_x, pos_cam_y = camera.apply((position.x, position.y))

                # if the mouse coursor is near
                if abs(x - pos_cam_x) < 30 and abs(y - pos_cam_y) < 30:

                    # Blit debug text info gathered above - except brain process
                    text_surf = GAME_DEBUG_FONT.render(pformat(debug.info)) # Text to Surface
                    frame_surf = GAME_DEBUG_FRAME.render(text_surf) # Frame the debug text to surface
                    
                    camera.screen.blit(
                        frame_surf,
                        (x, y)
                    )

                    pygame.draw.rect(
                        camera.screen,
                        pygame.Color('red'),
                        pygame.Rect(
                            camera.apply((position.x - 5, position.y + 5)), 
                            (2 * 5, 2 * 5)
                            ),
                        2
                    )

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
