'''Contains GUI components for the menus and the game'''

# Initiate logging
import logging

logger = logging.getLogger(__name__)

import pygame
import pygame.freetype
import pygame_gui

from pathlib import Path
from collections import namedtuple
from pyrpg.functions.load_animation import load_animation
from pyrpg.core.config.paths import MENU_BACKGROUND_PATH
from pyrpg.core.config.config import MENU_BACKGROUND_ANIMATION_DELAY

Dim = namedtuple('Dim', ['width', 'height'])
Pos = namedtuple('Pos', ['x', 'y'])

class GUIManager:

    def __init__(self, width: int, height: int, depth: int=32, full: bool=False, ratio: float=1.5) -> None:

        pygame.init()

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

        self.window = pygame.display.set_mode(
                self._res,
                pygame.FULLSCREEN if full else 0,
                depth
        )

        self.clock = pygame.time.Clock()
        self.screen_copy = pygame.Surface(self._res)
        self.window_manager = pygame_gui.UIManager(self._res)

        self.background_animation = load_animation(MENU_BACKGROUND_PATH, resize=self._res)
        self.background_animation_delay = MENU_BACKGROUND_ANIMATION_DELAY
        self.background_animation_last_image = 0
        self.background_animation_last_time = pygame.time.get_ticks()
        self.background_animation_frames = len(self.background_animation)

        logger.info(f'GUIManager initiated.')

    def show_file_select(self, title: str, path: Path) -> None:
        '''Obsolete, it will be on the level of Menu classes'''

        _ = pygame_gui.windows.UIFileDialog(
                rect=pygame.Rect(self._gui_dlg_start, self._gui_dlg_dim),
                manager=self.window_manager,
                window_title=title,
                initial_file_path=path,
                allow_existing_files_only=False,
                allow_picking_directories=False)

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

    def blit_background_animation(self):
        if pygame.time.get_ticks() >= self.background_animation_last_time + self.background_animation_delay:
            self.background_animation_last_time = pygame.time.get_ticks()
            # blit background image
            self.background_animation_last_image = (self.background_animation_last_image + 1) % self.background_animation_frames

        self.blit_image(self.background_animation[self.background_animation_last_image])

    def save_screen(self, flip_before_copy=False):
        ''' Parameter is used to force displaying everything on screen.
        Was prepared due to PHASE start of the first quest that was processed
        before anything was blitted on the screen
        '''

        if flip_before_copy: pygame.display.update()

        self.screen_copy = self.window.copy()
        logger.info(f'Screen has been copied')


if __name__ == '__main__':

    gui = GUIManager(640, 480, 32)