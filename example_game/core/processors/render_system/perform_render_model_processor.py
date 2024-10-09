__all__ = ['PerformRenderModelProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.position import Position
from core.components.camera import Camera
from core.components.renderable_model import RenderableModel

from ..functions import filter_only_visible_on_camera # for filtering only entities with position on the cameras

# Logger init
logger = logging.getLogger(__name__)

class PerformRenderModelProcessor(Processor):
    ''' Draws the entities in the world.

    It draws only those entities that are displayable on the screen
    by using filter function.
    
    Input parameters:
        -	window - reference to main game screen

    Involved components:
        -   Position
        -   Camera
        -   RenderableModel

    Related processors:
        -	UpdateCameraOffsetProcessor - adjust camera position to enable scrolling effect

    What if this processor is disabled?
        -	entities will be not shown in the game window
    
    Where the processor should be planned?
        -   before RenderDebugProcessor - in order not to overwrite the debug info
        -   after UpdateCameraOffsetProcessor - in order to display scrolling
        -   after RenderMapProcessor - in order to display map below the characters
        -   before NewPerformRenderWearablesProcessor - in order to properly wear clothes
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Initiation of PerformRenderModelProcessor processor.
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Blit RenderableModel onto the screen.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # For all camera screens in the game window
        for _, (camera) in self.world.get_component(Camera):

            # Blit all the Entities that have Renderable and Position components + only visible entities + are not picked up
            for ent, (position, renderable) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(Position, RenderableModel)):
                camera.screen.blit(renderable.get_current_frame(position.dir_name), camera.apply(renderable.topleft((position.x, position.y))))

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
