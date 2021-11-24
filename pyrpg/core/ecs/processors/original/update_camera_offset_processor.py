__all__ = ['UpdateCameraOffsetProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components


class UpdateCameraOffsetProcessor(esper.Processor):
    '''Updates Camera offset based on position (Position) of the entity. Updated
    camera offset is necessary later for RenderProcessor component to correctly display
    the screen.

    Input parameters:
        -	debug

    Involved components:
        -	Position
        -	Camera

    Related processors:
        -	RenderMapProcessor
        -	RenderWorldProcessor
        -	RenderDebugProcessor

    What if this processor is disabled?
        -	scrolling will not work

    Where the processor should be planned?
        -	before RenderXXXProcessor - camera must be updated before graphics is drawn
        -	after MovementProcessor - the position of the object in camera focus must be final
    '''

    __slots__ = ['maps', 'debug']

    def __init__(self, maps, debug=False):
        ''' Initiation of UpdateCameraOffsetProcessor processor.
        
        Parameters:
            :param maps: Reference to the global dict with maps
            :type maps: reference

            :param debug: Tag if processor should run in debug mode
            :type debug: bool
        '''

        super().__init__()

        self.debug = debug
        self.maps = maps

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Process entities having Camera and Position components. Check
        the following video for more details about camera implementation
        https://youtu.be/3zV2ewk-IGU.
        '''

        for _, (position, camera) in self.world.get_components(components.Position, components.Camera):

            # Updates camera offset based on position of the Position (component that the camera follows).

            # Offset moves opposite direction than the object + we need to keep it in the centre of the screen
            x = -position.x + camera.screen_width_half
            y = -position.y + camera.screen_height_half

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

            # Top-left corner - initial values (camera in the centre of the screen)
            x1 = position.x - camera.screen_width_half
            y1 = position.y - camera.screen_height_half

            # Bottom-right corner - initial values (camera in the centre of the screen)
            x2 = position.x + camera.screen_width_half
            y2 = position.y + camera.screen_height_half

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
