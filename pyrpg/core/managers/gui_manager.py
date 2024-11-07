""" Contains GUI components for the menus and the game.
"""

# Initiate logging
import logging

logger = logging.getLogger(__name__)

import pygame
import pygame.freetype
import pygame_gui

from pathlib import Path
from collections import namedtuple
from pyrpg.functions.load_animation import load_animation
from pyrpg.core.config.filepaths import FILEPATHS #MENU_BACKGROUND_PATH # MENU_BACKGROUND_PATH
from pyrpg.core.config.gui import GUI
#from pyrpg.core.config.config import MENU_BACKGROUND_ANIMATION_DELAY

#from pyrpg.utils.bitmap_font import BitmapFont
#from pyrpg.core.config.paths import FONT_PATH


Pos = namedtuple("Pos", ["x", "y"])
Dim = namedtuple("Dim", ["width", "height"])

####

class BackgroundAnimation:
    def __init__(self, path: Path, res: tuple, delay: int):
        self.animation = load_animation(background_folder_path=path, resize=res)
        self.delay = delay
        self.last_image = 0
        self.last_time = pygame.time.get_ticks()
        self.frames = len(self.animation)

# Font
from pyrpg.core.config.fonts import FONTS # for GUI_MANAGER_FONT
font = None

#_res: Dim
gui_dlg_dim: tuple
gui_dlg_start: Pos

window: pygame.Surface
clock = pygame.time.Clock()

screen_copy: pygame.Surface
window_manager: pygame_gui.UIManager

background_animation: BackgroundAnimation

INIT_DONE: bool = False

def init() -> None:
    # Initiate GUI manager
    from pyrpg.core.config import DISPLAY #WINDOW, WIDTH, HEIGHT, BITDEPTH, FULLSCREEN, GUI_WINDOW_RATIO 
    _init(
        win=DISPLAY["WINDOW"], 
        res=DISPLAY["RESOLUTION"],
        #width=WIDTH, height=HEIGHT, 
        full=DISPLAY["FULLSCREEN"], 
        ratio=DISPLAY["GUI_WINDOW_RATIO"]
    )
    global font
    font = FONTS["GUI_MANAGER_FONT"] #BitmapFont(FILEPATHS["FONT_PATH"] / "good_neighbours_font.json")


    logger.info(f"GUI Manager initiated.")

def _init(win: pygame.Surface, res: Dim, full: bool=False, ratio: float=1.5) -> None:

    global INIT_DONE

    # Dimensions of game window
    #_res = Dim(width, height)

    # Dimensions of GUI window
    global gui_dlg_dim
    gui_dlg_dim = Dim(
        res.width / ratio,
        res.height / ratio
    )

    # Start position of the GUI window - center on the screen
    global gui_dlg_start
    gui_dlg_start = Pos(
        (res.width - gui_dlg_dim.width) / 2,
        (res.height - gui_dlg_dim.height) / 2
    )

    # At this moment, display is already created during initial configuration
    global window
    window = win

    global screen_copy
    screen_copy = pygame.Surface(res)
    
    global window_manager

    if not INIT_DONE:
        window_manager = pygame_gui.UIManager(res)
    else:
        window_manager.set_window_resolution(res)

    global background_animation
    background_animation = BackgroundAnimation(
        path=FILEPATHS["MENU_BACKGROUND_PATH"], 
        res=res, 
        delay=GUI["MENU_BACKGROUND_ANIMATION_DELAY_MS"]
    )

    INIT_DONE = True

    logger.info(f"GUIManager initiated.")


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
    window.blit(font.render(text), pos)

def blit_background_animation():
    if pygame.time.get_ticks() >= background_animation.last_time + background_animation.delay:
        background_animation.last_time = pygame.time.get_ticks()
        # blit background image
        background_animation.last_image = (background_animation.last_image + 1) % background_animation.frames

    blit_image(background_animation.animation[background_animation.last_image])

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

'''
class GUIManager:

    def __init__(self, window: pygame.Surface, width: int, height: int, depth: int=32, full: bool=False, ratio: float=1.5) -> None:

        ##pygame.init()

        # Dimensions of game window
        self._res = Dim(width, height)

        # Dimensions of GUI window
        self._gui_dlg_dim = Dim(
            self._res.width / ratio,
            self._res.height / ratio
        )

        # Start position of the GUI window - center on the screen
        self._gui_dlg_start = Pos(
            (self._res.width - self._gui_dlg_dim.width) / 2,
            (self._res.height -  self._gui_dlg_dim.height) / 2
        )

        # At this moment, display is already created during initial configuration
        self.window = window
        ##self.window = pygame.display.set_mode(
        ##        self._res,
        ##        pygame.FULLSCREEN if full else 0,
        ##        depth
        ##)

        self.clock = pygame.time.Clock()

        self.screen_copy = pygame.Surface(self._res)
        self.window_manager = pygame_gui.UIManager(self._res)

        self.background_animation = load_animation(MENU_BACKGROUND_PATH, resize=self._res)
        self.background_animation_delay = GUI["MENU_BACKGROUND_ANIMATION_DELAY_MS"]
        self.background_animation_last_image = 0
        self.background_animation_last_time = pygame.time.get_ticks()
        self.background_animation_frames = len(self.background_animation)

        # Font
        from pyrpg.core.config.fonts import FONTS # for GUI_MANAGER_FONT
        self.font = FONTS["GUI_MANAGER_FONT"] #BitmapFont(FILEPATHS["FONT_PATH"] / "good_neighbours_font.json")

        logger.info(f"GUIManager initiated.")

    def process_events(self, event) -> None:
        self.window_manager.process_events(event)

    def update(self, time) -> None:
        self.window_manager.update(time) # in seconds

    def draw_gui(self) -> None:
        self.window_manager.draw_ui(self.window)

    def blit_background(self) -> None:
        self.window.blit(self.screen_copy, (0, 0))

    def blit_image(self, image: pygame.image=None):
        self.window.blit(image, (0, 0))
    
    def blit_text(self, text: str, pos=(0,0)):
        self.window.blit(self.font.render(text), pos)

    def blit_background_animation(self):
        if pygame.time.get_ticks() >= self.background_animation_last_time + self.background_animation_delay:
            self.background_animation_last_time = pygame.time.get_ticks()
            # blit background image
            self.background_animation_last_image = (self.background_animation_last_image + 1) % self.background_animation_frames

        self.blit_image(self.background_animation[self.background_animation_last_image])

    def flip(self):
        """ Trigger displaying on the screen.
        """
        pygame.display.flip()

    def save_screen(self, flip_before_copy=False):
        """ Parameter is used to force displaying everything on screen.
        Was prepared due to PHASE start of the first scene that was processed
        before anything was blitted on the screen.
        """

        if flip_before_copy: self.flip()

        self.screen_copy = self.window.copy()
        logger.info(f"Screen has been copied")

    def clear(self) -> None:
        pass
'''

if __name__ == '__main__':
    gui = init(640, 480, 32)