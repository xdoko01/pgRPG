__all__ = ['NewPerformClearWindowProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Logger init
logger = logging.getLogger(__name__)

class NewPerformClearWindowProcessor(Processor):
    ''' For clearing of the game window at the beginning of every
    drawing cycle.

    Input parameters:
        -   window

    Involved components:

    Related processors:
        -   NewPerformClearCameraProcessor - for clearing of cameras

    What if this processor is disabled?
        -   overdraws can occur on the game screen

    Where the processor should be planned?
        -   before NewPerformRenderMapProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = ['window', 'clear_color']

    def __init__(self, window, clear_color=(0, 0, 0)):
        ''' Initiation of NewPerformClearWindowProcessor processor.

        Parameters:

            :param window: Reference to the game window
            :type window: reference

            :param clear_color: Solid color used for clearing.
            :type clear_color: tuple
        '''
        super().__init__()

        self.window = window
        self.clear_color = clear_color

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Fill the game window with one solid color.
        '''
        self.cycle += 1
        self.window.fill(self.clear_color)

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components
        '''
        self.window = None

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the reference to window again
        '''
        self.window = window

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
