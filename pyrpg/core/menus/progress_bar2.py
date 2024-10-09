import logging
from threading import Thread


# Initiate logging of module
logger = logging.getLogger(__name__)

class ProgressBar2():
    '''Class implementing the progress bar'''

    def __init__(self, gui_manager, header="Loading", text="") -> None:
        self.gui_manager = gui_manager

        self.total = None
        self.progress: int
        self.header = header
        self.text = text
        self.finished: bool

        logger.info(f'Load Game Progress Bar initiated')

    def __enter__(self):
        self.progress = 0
        self.finished = False

        Thread(target=self.run).start()

        return self.update
 
    def __exit__(self, *args):
        self.finished = True # effectivelly finishes the Thread

    def update(self, iter):
        '''Set values for rendering of progress bar. It is called from different
        places of the code. The reference to this particular function is passed to
        those parts of the code that manage loading of the resources.'''

        if self.progress == 0: #First call of the update function

            try:
                self.total = len(iter)

            except TypeError: # is not iterator but for example generator
                self.total = None

        for i in iter:
            self.progress += 1
            yield i


    def run(self):
        '''Displays progress screen (running in separate thread)'''
        while not self.finished:

            self.gui_manager.blit_background_animation()

            self.gui_manager.blit_text(f'{self.header} - {self.text} ... {self.progress} / {self.total}')

            self.gui_manager.flip()
