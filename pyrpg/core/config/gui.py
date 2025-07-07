# Init logging config
import logging
logger = logging.getLogger(__name__)

import pygame

#### BACKGROUND ANIMATION - START
from pathlib import Path
from pyrpg.functions.load_animation import load_animation

class BackgroundAnimation:
    def __init__(self, path: Path, res: tuple, delay: int):
        self.animation = load_animation(background_folder_path=path, resize=res)
        self.delay = delay
        self.last_image = 0
        self.last_time = pygame.time.get_ticks()
        self.frames = len(self.animation)

background_animation: BackgroundAnimation

def init_background_animation(display: dict, filepaths: dict, gui_conf: dict) -> None:

    global background_animation
    background_animation = BackgroundAnimation(
        path=filepaths["MENU_BACKGROUND_PATH"], 
        res=display["RESOLUTION"], 
        delay=gui_conf["MENU_BACKGROUND_ANIMATION_DELAY_MS"]
    )

def blit_background_animation():
    global background_animation
    if pygame.time.get_ticks() >= background_animation.last_time + background_animation.delay:
        background_animation.last_time = pygame.time.get_ticks()
        # blit background image
        background_animation.last_image = (background_animation.last_image + 1) % background_animation.frames

    blit_image(background_animation.animation[background_animation.last_image])
    
#### BACKGROUND ANIMATION - END

#### PROGRESS BAR - START
from threading import Thread
from pyrpg.core.config import DISPLAY

class ProgressBar():
    '''Class implementing the progress bar'''

    def __init__(self, header: str="Loading", text: str="", total: int=None) -> None:

        self.total = total
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
                self.total = len(iter) if self.total is None else self.total

            except TypeError: # is not iterator but for example generator
                self.total = None

        for i in iter:
            self.progress += 1
            yield i


    def run(self):
        '''Displays progress screen (running in separate thread)'''
        while not self.finished:

            blit_background_animation()

            percent = self.progress / self.total if self.total > 0 else 1
            blit_bar(percent=percent, color=pygame.Color('red'), height=10)

            blit_text(f'{self.header} - {self.text} ... {self.progress} / {self.total}')

            flip()

#### PROGRESS BAR - END

#### GUI - START
import pygame_gui
from pgbitmapfont import BitmapFont

from collections import namedtuple

Pos = namedtuple("Pos", ["x", "y"])
Dim = namedtuple("Dim", ["width", "height"])

window: pygame.Surface
clock = pygame.time.Clock()

screen_copy: pygame.Surface
window_manager: pygame_gui.UIManager

font: BitmapFont

def init_gui(display: dict, fonts: dict) -> None:
    '''Initiate the main variables on init or change of configuration'''
    global window
    window = display["WINDOW"]

    global screen_copy
    screen_copy = pygame.Surface(display["RESOLUTION"])
    
    global window_manager
    window_manager = pygame_gui.UIManager(display["RESOLUTION"])

    global font
    font = fonts["GUI_MANAGER_FONT_OBJ"] 

    logger.info(f"GUI initiated.")


def process_events(event) -> None:
    window_manager.process_events(event)

def update(time) -> None:
    window_manager.update(time) # in seconds

def draw_gui() -> None:
    window_manager.draw_ui(window)

def blit_background() -> None:
    window.blit(screen_copy, (0, 0))

def blit_image(image: pygame.image=None):
    window.blit(image, (0, 0))

def blit_text(text: str, pos=(0,0)):
    window.blit(font.render(text)[0], pos)

def blit_bar(percent: float, color: pygame.Color, height: int) -> None:
    '''Show the bar on the bottom of the screen'''
    pygame.draw.rect(window, color, (0, DISPLAY["RESOLUTION"][1] - height, int(percent * DISPLAY["RESOLUTION"][0]), height))

def flip():
    """ Trigger displaying on the screen.
    """
    pygame.display.flip()

def save_screen(flip_before_copy=False):
    """ Parameter is used to force displaying everything on screen.
    Was prepared due to PHASE start of the first scene that was processed
    before anything was blitted on the screen.
    """

    if flip_before_copy: flip()

    global screen_copy
    screen_copy = window.copy()
    logger.info(f"Screen has been copied")

def clear() -> None:
    pass

##### GUI - END