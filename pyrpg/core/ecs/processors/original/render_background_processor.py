__all__ = ['RenderBackgroundProcessor', 'RenderCameraBackgroundProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.original.camera import Camera

class RenderCameraBackgroundProcessor(Processor):
    def __init__(self, clear_color=(0, 0, 0), debug=False):

        super().__init__()
        self.clear_color = clear_color
        self.debug = debug

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        
        # Clear the game camera window surfaces
        for _, (camera) in self.world.get_component(Camera):
            camera.screen.fill(self.clear_color)
    
    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components (window)
        '''
        pass

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the reference to window again
        '''
        pass


class RenderBackgroundProcessor(Processor):
    def __init__(self, window, clear_color=(0, 0, 0), debug=False):

        super().__init__()
        self.window = window
        self.clear_color = clear_color
        self.debug = debug

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        # Clear the main game window surface
        self.window.fill(self.clear_color)
    
    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components (window)
        '''
        self.window = None

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the reference to window again
        '''
        self.window = window
