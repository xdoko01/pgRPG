__all__ = ['PerformRenderMapProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.position import Position
from core.components.camera import Camera

from pyrpg.core.config import GAME # for TILE_RES_PX

# Logger init
logger = logging.getLogger(__name__)

class PerformRenderMapProcessor(Processor):
    ''' For rendering maps on camera screen surfaces.

    Input parameters:
        -   maps

    Involved components:
        -   Position
        -   Camera

    Related processors:
        -   PerformScrollCameraProcessor - for enabling of scrolling

    What if this processor is disabled?
        -   no map will be rendered on the camera screens

    Where the processor should be planned?
        -   before PerformRenderModelProcessor - so that entities are not overdrawn by map
        -   after PerformScrollCameraProcessor - so that map is properly scrolled
        -   after NewPerformRenderBackgroundProcessor - so that the camera screen is cleared
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = ['maps']

    def __init__(self, window, maps, *args, **kwargs):
        ''' Initiation of PerformRenderMapProcessor processor.

        Parameters:

            :param maps: Reference to dict of all maps
            :type maps: reference
        '''
        super().__init__(*args, **kwargs)

        self.maps = maps


    def process(self, *args, **kwargs):
        ''' Process entities having Position and Camera components. Basically,
        blit the relevant part of the map on camera screen surface.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Find the entity with Camera and use its position
        # position - position and map of the object that is in camera's focus
        # camera - camera component itself
        for _, (position, camera) in self.world.get_components(Position, Camera):

            # Get map that is on the object in camera's focus
            map = self.maps.get(position.map)

            # Cycle through visible layers and display tiles
            for layer in map.tmxdata.visible_tile_layers:

                for x, y, tile in map.get_tile_images_by_rect(layer, camera.map_screen_rect): # is this needed - can we simplify this?
                    camera.screen.blit(tile, camera.apply((x * GAME["TILE_RES_PX"], y * GAME["TILE_RES_PX"])))

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components (maps)
        '''
        self.maps = None

    def post_load(self, maps):
        ''' Reconfigure the processor after de-serialization by attaching
        the reference to maps again
        '''
        self.maps = maps

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
