__all__ = ['RenderMapProcessorFullScan']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

class RenderMapProcessorFullScan(esper.Processor):
    ''' For rendering maps on camera surfaces. 
    
    For ALL maps ALL TILES are blitted - even those that are out of visible area.
    
    Hence this is not optimal version of the RenderMapProcessor.
    '''

    def __init__(self, window, maps, tile_res=64, debug=False):
        '''
        '''
        super().__init__()
        self.window = window
        self.maps = maps
        self.tile_res = tile_res
        self.debug = debug

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' 
        '''
        
        # Find the entity with Camera and use its position
        # cam_pos - position and map of the object that is in camera's focus
        # cam_cam - camera component itself
        for _ , (cam_pos, cam_cam) in self.world.get_components(components.Position, components.Camera):

            # Clear the camera surface
            cam_cam.screen.fill((0,0,0))

            # Get map that is on the object in camera's focus
            map = self.maps.get(cam_pos.map)

            # Blit the map ground layer			
            for i in range(len(map.ground_layer)): # Y axis	
                for j in range(len(map.ground_layer[0])): # X axis
                    if map.ground_layer[i][j] != 0:
                        #cam_cam.screen.blit(map.get_tile('ground', j, i), self.apply_camera(cam_cam, (j * self.tile_res, i * self.tile_res)))
                        cam_cam.screen.blit(map.get_tile_image(j, i, 'ground'), cam_cam.apply((j * self.tile_res, i * self.tile_res)))

            # Blit the map wall layer
            for i in range(len(map.wall_layer)): # Y axis	
                for j in range(len(map.wall_layer[0])): # X axis
                    if map.wall_layer[i][j] != 0:
                        #cam_cam.screen.blit(map.get_tile('wall', j, i), self.apply_camera(cam_cam, (j * self.tile_res, i * self.tile_res)))
                        cam_cam.screen.blit(map.get_tile_image(j, i, 'wall'), cam_cam.apply((j * self.tile_res, i * self.tile_res)))
        
                        

            # Blit the camera screen on the main game window
            self.window.blit(cam_cam.screen, (cam_cam.screen_pos_x, cam_cam.screen_pos_y))

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
