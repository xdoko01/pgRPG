__all__ = ['RenderWorldProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.original.camera import Camera
from pyrpg.core.ecs.components.original.position import Position
from pyrpg.core.ecs.components.original.renderable import Renderable
from pyrpg.core.ecs.components.original.can_talk import CanTalk

class RenderWorldProcessor(Processor):
    ''' Draws the entities in the world. Entity is represented just by
    the picture stored in Renderable component.

    This is substituted by RenderModelWorldProcessor which supports 
    animated entities by using RenderModel component.

    Also this component does not use filter to draw only entities that 
    are currently displayable on the screen.
    
    Input parameters:
        -	window - reference to main game screen
        -	debug

    Involved components:
        -	Position
        -	Camera
        -	Renderable
        -	CanTalk
    
    Related processors:
        -	UpdateCameraOffsetProcessor - adjust camera position to enable scrolling effect

    What if this processor is disabled?
        -	entities will be not shown on the game window
    
    Where the processor should be planned?
        -	before RenderDebugProcessor - in order not to overwrite the debug info
        -	after UpdateCameraOffsetProcessor - in order to display scrolling
        -	after RenderMapProcessor - in order to display map
    '''

    __slots__ = ['window', 'debug']

    def __init__(self, window, *args, debug=False, **kwargs):
        ''' Initiation of RenderProcessor processor.
        
        Parameters:
            :param window: Reference to the main game surface
            :type window: pygame.Surface

            :param debug: Tag if processor should run in debug mode
            :type debug: bool
        '''

        super().__init__(*args, **kwargs)
        
        self.window = window
        self.debug = debug

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Draws screen for every camera. Every screen draws entities
        and dialog texts. Check the following video for more details about camera 
        implementation of scrolling https://youtu.be/3zV2ewk-IGU.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # For all camera screens in the game window
        for _, (camera) in self.world.get_component(Camera):

            # Blit all the Entities that have Renderable and Position components
            for _ , (renderable, position) in self.world.get_components(Renderable, Position):
                camera.screen.blit(renderable.image, camera.apply(renderable.topleft((position.x, position.y))))

            # Blit all Texts that are entities saying (CanSpeak + Position component)
            for _, (can_talk, renderable, position) in self.world.get_components(CanTalk, Renderable, Position):

                # If there is something to say
                if can_talk.text:
                    
                    # Blit the text bubble on the position offset specified by CanTalk component
                    
                    if position.direction == (1,0): # RIGHT
                        camera.screen.blit(can_talk.text_surf, 
                            camera.apply((position.x - renderable.d_w - can_talk.text_rect[2], position.y - can_talk.text_rect[3])))
                    
                    elif position.direction == (-1,0): # if direction is (-1, 0) LEFT
                        camera.screen.blit(can_talk.text_surf, 
                            camera.apply((position.x + renderable.d_w, position.y - can_talk.text_rect[3])))

                    elif position.direction == (0,-1): # if direction is (0,-1) UP
                        camera.screen.blit(can_talk.text_surf, 
                            camera.apply((position.x - can_talk.text_rect[2] / 2, position.y + renderable.d_h )))

                    else: # if direction is (0,1) DOWN
                        camera.screen.blit(can_talk.text_surf, 
                            camera.apply((position.x - can_talk.text_rect[2] / 2, position.y - renderable.d_h - can_talk.text_rect[3])))


            # Blit the camera screen on the main game window
            self.window.blit(camera.screen, (camera.screen_pos_x, camera.screen_pos_y))

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components (window).
        '''
        self.window = None

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the reference to window again.
        '''
        self.window = window
