import logging

import pygame

# Initiate logging of module
logger = logging.getLogger(__name__)

class ProgressBar():
    '''Class implementing the progress bar'''

    def __init__(self, gui_manager) -> None:
        self.gui_manager = gui_manager

        self.total = 0
        self.progress = 0
        self.header = "Progress"
        self.text = 'text'

        self.progress_bar = pygame.Surface((100,100))
        self.progress_bar.fill((255,0,0))

        self.finished = False

        logger.info(f'Load Game Progress Bar initiated')

    def update(self, progress=None, total=None, header=None, text=None, finished=False):
        '''Set values for rendering of progress bar. It is called from different
        places of the code. The reference to this particular function is passed to
        those parts of the code that manage loading of the resources.'''
        
        self.total = total if total else self.total
        self.progress = progress if progress else self.progress
        self.header = header if header else self.header
        self.text = text if text else self.text
        self.finished = finished

    def run(self):
        '''Displays progress screen (running in separate thread)'''

        while not self.finished:

            self.gui_manager.blit_background_animation()

            self.gui_manager.blit_text(f'{self.header} - {self.text} ... {self.progress} / {self.total}')

            self.gui_manager.flip()
