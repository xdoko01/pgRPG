__all__ = ['PerformBlitPictureProcessor']

import logging
import pygame

from pgrpg.core.config import FILEPATHS, DISPLAY

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Logger init
logger = logging.getLogger(__name__)

class PerformBlitPictureProcessor(Processor):
    ''' Blits picture onto game window.

    Input parameters:
        -	window - reference to main game screen

    Involved components:

    Related processors:

    What if this processor is disabled?
        -   Nothing displayed on the game screen

    Where the processor should be planned?
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = []

    def __init__(self, window, filepath: str, resize: bool=True, pos: tuple=(0,0), *args, **kwargs):
        ''' Initiation of PerformBlitCameraProcessor processor.

        Parameters:
            :param window: Reference to the main game surface
            :type window: pygame.Surface

            :param filepath: Path to the files
            :type filepath: str

            :param resize: Should the picture be resized to the game window
            :type resize: bool

            :param pos: Top-left corner position of the picture on the screen
            :type pos: tuple
        '''
        super().__init__(*args, **kwargs)

        self.window = window
        self.filepath = filepath
        self.picture = pygame.image.load(FILEPATHS["IMAGE_PATH"] / self.filepath)
        self.pos = pos
        self.resize = resize
        if self.resize: self.picture = pygame.transform.scale(self.picture, DISPLAY["RESOLUTION"])
        self.picture = self.picture.convert_alpha()  # or .convert() if no transparency

    def reinit(self):
        '''Used for repetitive initiation after change of configuration.
        '''
        if self.resize: 
            self.picture = pygame.image.load(FILEPATHS["IMAGE_PATH"] / self.filepath)
            self.picture = pygame.transform.scale(self.picture, DISPLAY["RESOLUTION"])
            self.picture = self.picture.convert_alpha()  # or .convert() if no transparency


    def process(self, *args, **kwargs):
        ''' Blit Camera onto the screen.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Blit picture on the window
        self.window.blit(self.picture, self.pos)

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