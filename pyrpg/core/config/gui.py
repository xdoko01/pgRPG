# Init logging config
import logging
logger = logging.getLogger(__name__)

import pygame

#### BACKGROUND ANIMATION
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
    if pygame.time.get_ticks() >= background_animation.last_time + background_animation.delay:
        background_animation.last_time = pygame.time.get_ticks()
        # blit background image
        background_animation.last_image = (background_animation.last_image + 1) % background_animation.frames

    blit_image(background_animation.animation[background_animation.last_image])


##### GUI
import pygame.freetype
import pygame_gui

from collections import namedtuple

Pos = namedtuple("Pos", ["x", "y"])
Dim = namedtuple("Dim", ["width", "height"])

window: pygame.Surface
clock = pygame.time.Clock()

screen_copy: pygame.Surface
window_manager: pygame_gui.UIManager


def init_gui(display: dict, fonts: dict) -> None:
    # Initiate GUI manager
    _init_gui(
        win=display["WINDOW"], 
        res=display["RESOLUTION"]
    )
    global font
    font = fonts["GUI_MANAGER_FONT_OBJ"] 

    logger.info(f"GUI Manager initiated.")

def _init_gui(win: pygame.Surface, res: Dim) -> None:

    # At this moment, display is already created during initial configuration
    global window
    window = win

    global screen_copy
    screen_copy = pygame.Surface(res)
    
    global window_manager
    window_manager = pygame_gui.UIManager(res)

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
    window.blit(font.render(text)[0], pos)

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
