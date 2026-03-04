__all__ = ['PerformRenderMapProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.position import Position
from core.components.camera import Camera

from pgrpg.core.config import GAME # for TILE_RES_PX

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
        ''' Process entities having Position and Camera components.

        For each visible layer, blits the pre-rendered static surface slice
        (one Surface.blit call) and then overlays only the animated tiles that
        fall within the visible area. This replaces the previous per-tile loop
        that called get_tile_image() for every tile every frame.

        Layer order is preserved so that higher layers correctly composite over
        lower ones, including the edge case where an animated tile in a lower
        layer is partially covered by a static tile in a higher layer.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        tile_px = GAME["TILE_RES_PX"]

        for _, (position, camera) in self.world.get_components(Position, Camera):

            map_obj = self.maps.get(position.map)
            x1, y1, x2, y2 = camera.map_screen_rect

            # Tile-coordinate bounds of the visible area (for animated tile culling)
            vtx1 = int(x1 // tile_px)
            vty1 = int(y1 // tile_px)
            vtx2 = int(x2 // tile_px) + 1
            vty2 = int(y2 // tile_px) + 1

            for layer in map_obj.tmxdata.visible_tile_layers:

                # Single blit of the pre-rendered static surface slice for this layer
                camera.screen.blit(map_obj.static_surfaces[layer], (0, 0), (x1, y1, x2 - x1, y2 - y1))

                # Overlay only animated tiles in view on top of the static slice
                for tx, ty in map_obj.anim_tile_positions.get(layer, []):
                    if vtx1 <= tx <= vtx2 and vty1 <= ty <= vty2:
                        tile = map_obj.get_tile_image(tx, ty, layer)
                        if tile:
                            camera.screen.blit(tile, camera.apply((tx * tile_px, ty * tile_px)))

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
