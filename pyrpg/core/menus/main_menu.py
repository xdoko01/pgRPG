import logging

from pygame_gui.elements import UIButton
from pygame_gui import UI_BUTTON_PRESSED, UI_WINDOW_CLOSE
from pygame import Rect
from pyrpg.core.config.states import State
from .menu import Menu

# Initiate logging of module
logger = logging.getLogger(__name__)

class MainMenu(Menu):
    '''Class implementing the main menu buttons'''

    def __init__(self, gui_manager, sound_manager, state_manager) -> None:
        self.gui_manager = gui_manager
        self.sound_manager = sound_manager
        self.state_manager = state_manager

        self.load_scene_button = UIButton(relative_rect=Rect((150, 175), (100, 50)), text='Load Scene', manager=self.gui_manager.window_manager, container=None)
        self.exit_game_button = UIButton(relative_rect=Rect((150, 275), (100, 50)), text='Exit', manager=self.gui_manager.window_manager, container=None)
        self.load_scene_button.hide()
        self.exit_game_button.hide()

        logger.info(f'Main menu window initiated')

    def show(self) -> None:
        self.load_scene_button.show()
        self.exit_game_button.show()
        logger.info(f'Main menu window showned')

    def hide(self) -> None:
        self.load_scene_button.hide()
        self.exit_game_button.hide()
        logger.info(f'Main menu window hidden')

    def run(self, key_events, key_pressed, dt) -> State:

        #if self.state_manager.changed_game_state:
        if self.state_manager.changed:
            self.show()

        for event in key_events:

            if event.type == UI_BUTTON_PRESSED:
                if event.ui_element == self.load_scene_button:
                    logger.info(f'Accessing load scene window')
                    self.hide()
                    return State.LOAD_QUEST_MENU
                if event.ui_element == self.exit_game_button:
                    logger.info(f'Accessing exit game window')
                    return State.EXIT_GAME_DIALOG

            self.gui_manager.process_events(event)

        self.gui_manager.update(dt/1000)

        self.gui_manager.blit_background_animation()

        self.gui_manager.draw_gui()

        return State.MAIN_MENU

    def clear(self) -> None:
        pass