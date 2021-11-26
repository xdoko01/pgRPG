__all__ = ['RenderMapProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.original.position import Position
from pyrpg.core.ecs.components.original.camera import Camera

import pyrpg.core.config.config as config # for MOVE_SPEED

class RenderMapProcessor(Processor):
    ''' For rendering maps on camera screen surfaces.

    Input parameters:
        -	debug
        -	window
        -	maps

    Involved components:
        -	Position
        -	Camera

    Related processors:
        -	UpdateCameraOffsetProcessor - for enabling of scrolling

    What if this processor is disabled?
        -	no map will be rendered on the camera screens

    Where the processor should be planned?
        -	before RenderWorldProcessor - so that entities are not overdrawn by map
        -	after UpdateCameraOffsetProcessor - so that map is properly scrolled
        -	after RenderBackgroundProcessor - so that the camera screen is cleared
    '''

    __slots__ = ['window', 'maps', 'debug']

    def __init__(self, window, maps, debug=False):
        ''' Initiation of RenderMapProcessor processor.

        Parameters:
            :param window: Reference to the main game surface
            :type window: pygame.Surface

            :param maps: Reference to dict of all maps
            :type maps: reference

            :param debug: Tag if processor should run in debug mode
            :type debug: bool
        '''

        super().__init__()

        self.window = window
        self.maps = maps
        self.debug = debug

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Process entities having Position and Camera components. Basically,
        blit the relevant part of the map on camera screen surface.
        '''

        # Find the entity with Camera and use its position
        # position - position and map of the object that is in camera's focus
        # camera - camera component itself
        for _, (position, camera) in self.world.get_components(Position, Camera):

            # Get map that is on the object in camera's focus
            map = self.maps.get(position.map)

            # Cycle through visible layers and display tiles
            for layer in map.tmxdata.visible_tile_layers:

                for x, y, tile in map.get_tile_images_by_rect(layer, camera.map_screen_rect):
                    camera.screen.blit(tile, camera.apply((x * config.TILE_RES, y * config.TILE_RES)))

            # Blit the camera screen on the main game window
            self.window.blit(camera.screen, (camera.screen_pos_x, camera.screen_pos_y))

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components (window, maps)
        '''
        self.window = None
        self.maps = None

    def post_load(self, window, maps):
        ''' Reconfigure the processor after de-serialization by attaching
        the reference to window and maps again
        '''
        self.window = window
        self.maps = maps
