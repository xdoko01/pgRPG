__all__ = ['NewPerformBlitCameraProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)

class NewPerformBlitCameraProcessor(esper.Processor):
    ''' Blits all cameras onto game window.

    Input parameters:
        -	window - reference to main game screen

    Involved components:
        -   Camera

    Related processors:
        -   UpdateCameraOffsetProcessor - adjust camera position to enable scrolling effect

    What if this processor is disabled?
        -   Nothing displayed on the game screen
    
    Where the processor should be planned?
        -   after all render processors are finished
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = []

    def __init__(self, window):
        ''' Initiation of NewPerformBlitCameraProcessor processor.

        Parameters:
            :param window: Reference to the main game surface
            :type window: pygame.Surface

        '''
        super().__init__()

        self.window = window

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Blit Camera onto the screen.
        '''
        self.cycle += 1

        # For all camera screens - blit all in the game window
        for _, (camera) in self.world.get_component(components.Camera):

            self.window.blit(camera.screen, (camera.screen_pos_x, camera.screen_pos_y))


    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components.
        '''
        self.window = None

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization.
        '''
        self.window = window

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass