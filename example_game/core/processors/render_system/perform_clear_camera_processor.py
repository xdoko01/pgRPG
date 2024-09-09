__all__ = ['PerformClearCameraProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.new.camera import Camera

# Logger init
logger = logging.getLogger(__name__)

class PerformClearCameraProcessor(Processor):
    ''' For clearing of the cameras at the beginning of every
    drawing cycle.

    Input parameters:
        -   clear_color (optional)

    Involved components:
        -   Camera

    Related processors:
        -   PerformClearWindowProcessor - for clearing of game window

    What if this processor is disabled?
        -   overdraws can occur on the cameras

    Where the processor should be planned?
        -   before PerformRenderMapProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = ['clear_color']

    def __init__(self, *args, clear_color=(0, 0, 0),  **kwargs):
        ''' Initiation of PerformClearCameraProcessor processor.

        Parameters:

            :param clear_color: Solid color used for clearing.
            :type clear_color: tuple
        '''
        super().__init__(*args, **kwargs)

        self.clear_color = clear_color

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Fill the cameras with one solid color.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Clear the game camera window surfaces
        for _, (camera) in self.world.get_component(Camera):
            camera.screen.fill(self.clear_color)

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components.
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization by attaching
        the reference again.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
