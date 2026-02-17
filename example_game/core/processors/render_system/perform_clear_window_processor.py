__all__ = ['PerformClearWindowProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Logger init
logger = logging.getLogger(__name__)

class PerformClearWindowProcessor(Processor):
    ''' For clearing of the game window at the beginning of every
    drawing cycle.

    Input parameters:
        -   window

    Involved components:

    Related processors:
        -   PerformClearCameraProcessor - for clearing of cameras

    What if this processor is disabled?
        -   overdraws can occur on the game screen

    Where the processor should be planned?
        -   before PerformRenderMapProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = ['window', 'clear_color']

    def __init__(self, window, *args, clear_color=(0, 0, 0), **kwargs):
        ''' Initiation of PerformClearWindowProcessor processor.

        Parameters:

            :param window: Reference to the game window
            :type window: reference

            :param clear_color: Solid color used for clearing.
            :type clear_color: tuple
        '''
        super().__init__(*args, **kwargs)

        self.window = window
        self.clear_color = clear_color


    def process(self, *args, **kwargs):
        ''' Fill the game window with one solid color.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return
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
