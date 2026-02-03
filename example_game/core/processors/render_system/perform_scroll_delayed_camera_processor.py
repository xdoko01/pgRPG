__all__ = ['PerformScrollDelayedCameraProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.camera import Camera
from core.components.position import Position

# Logger init
logger = logging.getLogger(__name__)

class PerformScrollDelayedCameraProcessor(Processor):
    '''Updates Camera offset based on position (Position) of the entity. Updated
    camera offset is necessary later in render system to correctly display
    the screen. Camera's reaction is delayed towards the actual change of position.

    Input parameters:

    Involved components:
        -   Position
        -   Camera

    Related processors:
        -   PerormRenderMapProcessor
        -   PerformRenderModelProcessor
        -   PerformBlitCameraProcessor

    What if this processor is disabled?
        -   scrolling will not work

    Where the processor should be planned?
        -   before PerformRenderXXXProcessor - camera must be updated before graphics is drawn
        -   after MovementProcessor - the position of the object in camera focus must be final
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = ['maps']

    def __init__(self, maps, *args, debug=False, **kwargs):
        ''' Initiation of PerformScrollCameraProcessor processor.

        Parameters:
            :param maps: Reference to the global dict with maps
            :type maps: reference
        '''
        super().__init__(*args, **kwargs)

        self.maps = maps
        self.delay = kwargs.get('delay', 0.005)


    def process(self, *args, **kwargs):
        ''' Process entities having Camera and Position components. Check
        the following video for more details about camera implementation
        https://youtu.be/3zV2ewk-IGU.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for _, (position, camera) in self.world.get_components(Position, Camera):

            # camera offset ... number that we need to add to real entity position in order to get coordinates on the computer screen where we can draw an entity
            # Eg. position of entity is (2000, 2000) but camera is only window 500,500. In order to draw the entity in the centre of 500x500 window we need to
            # calculate the offset. Offset x = -2000 + 250 = -1750, Offset Y = -2000 + 250 = -1750. So the entity with real world position 2000,2000 needs to be
            # drawn on the 500x500 screen on Position = real position + offset, i.e. Position X = 2000 + (-1750) = 250, Position Y = 2000 + (-1750) = 250. Right 
            # in the centre of 500x500 screen.
            
            # Updates camera offset based on position of the Position (component that the camera follows).
            # Unlike the PerformScrollCameraProcessor this processor implements the delayed reaction of the camera
            # based on the DELAY_FACTOR constant. Camera behaves like 'on a spring'.
          
            # Calculate vector between new camera offset (where camera should be centered based on position) and old camera offset.
            # Btw it is the same as vector between old position  and new (actual) position - heading from new towards old position
            diffx = (-position.x + camera.screen_width_half) - camera.offset_x
            diffy = (-position.y + camera.screen_height_half) - camera.offset_y

            # New camera offset is old camera offset + a little bit of the vector towards the correct (perfectly centered) camera offset
            x = camera.offset_x + self.delay*diffx
            y = camera.offset_y + self.delay*diffy

            # Correction - do not centre while entity is at the edge of the map

            # In case centred camera is required then skip all corrections
            if not camera.always_center:
                # Get the reference to the map from the global dict of maps
                try:
                    pos_map_ref = self.maps.get(position.map)
                except KeyError:
                    raise

                # Do the corrections
                x = min(0, x)
                y = min(0, y)
                x = max(-(pos_map_ref.width - camera.screen_width), x)
                y = max(-(pos_map_ref.height - camera.screen_height), y)

            # Update the Camera offset
            camera.offset_x, camera.offset_y = x, y

            # Update camera.map_screen_rect - rectancle that specifies in pixel coordinates what part of
            # map area is displayed on the camera.screen - area should not exceed map edges, that is
            # why the correction is applied

            # tl means top-left, br means bottom-right. These are supportive variables that are added to
            # corners of the area in case that camera is at the border of the map. In those cases there
            # was a problem that the area was incorrectly calculated because the position
            # was not in the centre of the camera. Those variables are correcting this.

            # Top-left corner - initial values (camera in the centre of the screen) - compensate the current new position by the diff vector to be at the centre of the camera
            x1 = position.x - camera.screen_width_half + (1-self.delay)*diffx
            y1 = position.y - camera.screen_height_half + (1-self.delay)*diffy

            # Bottom-right corner - initial values (camera in the centre of the screen) - compensate the current new position by the diff vector to be at the centre of the camera
            x2 = position.x + camera.screen_width_half + (1-self.delay)*diffx
            y2 = position.y + camera.screen_height_half + (1-self.delay)*diffy

            # In case centred camera is required then skip all corrections
            if not camera.always_center:

                # If the camera is freezed on top or left map edge, calculate correction
                # that is later added to bottom-right corner.
                tl_dx = -x1 if x1 < 0 else 0
                tl_dy = -y1 if y1 < 0 else 0

                # If the camera is freezed on bottom or right map edge, calculate correction
                # that is later added to top-left corner.
                br_dx = -(x2 - pos_map_ref.width) if x2 > pos_map_ref.width else 0
                br_dy = -(y2 - pos_map_ref.height) if y2 > pos_map_ref.height else 0

                # Top-left corner is never negative
                x1 = max(0, x1 + br_dx)
                y1 = max(0, y1 + br_dy)

                # Bottom-right corner cannot exceed map borders
                x2 = min(pos_map_ref.width, x2 + tl_dx)
                y2 = min(pos_map_ref.height, y2 + tl_dy)

            # Update the part of map that is displayed on camera.screen
            camera.map_screen_rect = (x1, y1, x2, y2)

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