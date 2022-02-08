import logging

from pygame_gui.elements import UIButton
from pygame_gui import UI_BUTTON_PRESSED, UI_WINDOW_CLOSE
from pygame import Rect
from pyrpg.core.config.states import State

# Initiate logging of module
logger = logging.getLogger(__name__)

class MainMenu:

    def __init__(self, gui_manager, state_manager) -> None:
        self.gui_manager = gui_manager
        self.state_manager = state_manager
        #self.main_menu_window = UIWindow(rect=Rect((10,10), (500,500)), manager=self.gui_manager.window_manager)
        #self.load_quest_button = UIButton(relative_rect=Rect((150, 175), (100, 50)), text='Load Quest', manager=self.gui_manager.window_manager, container=self.main_menu_window)
        #self.exit_game_button = UIButton(relative_rect=Rect((150, 275), (100, 50)), text='Exit', manager=self.gui_manager.window_manager, container=self.main_menu_window)
        #self.main_menu_window.hide()

        self.load_quest_button = UIButton(relative_rect=Rect((150, 175), (100, 50)), text='Load Quest', manager=self.gui_manager.window_manager, container=None)
        self.exit_game_button = UIButton(relative_rect=Rect((150, 275), (100, 50)), text='Exit', manager=self.gui_manager.window_manager, container=None)
        self.load_quest_button.hide()
        self.exit_game_button.hide()

        logger.info(f'Main menu window initiated')

    def show(self) -> None:
        #self.main_menu_window.show()
        self.load_quest_button.show()
        self.exit_game_button.show()

        logger.info(f'Main menu window showned')

    def hide(self) -> None:
        self.load_quest_button.hide()
        self.exit_game_button.hide()

        logger.info(f'Main menu window hidden')

    def run(self, key_events, key_pressed, dt) -> State:

        # If first time coming from the game to the loop, generate the gui window again
        if self.state_manager.changed_game_state:
            #self.gui_manager.save_screen()
            self.show()

        for event in key_events:
            if event.type == UI_BUTTON_PRESSED:
                if event.ui_element == self.load_quest_button:
                    logger.info(f'Accessing load quest window')
                    #Hide the main menu window
                    self.hide()
                    logger.info(f'Main menu window hidden')
                    return State.LOAD_QUEST_MENU
                if event.ui_element == self.exit_game_button:
                    logger.info(f'Accessing exit game window')
                    return State.EXIT_GAME_DIALOG
            elif event.type == UI_WINDOW_CLOSE:
                # if MAIN_MENU is accessed from other existing state other than None
                self.hide()
                logger.info(f'Main menu window hidden')
                return State.EXIT_GAME_DIALOG

            self.gui_manager.process_events(event)

        self.gui_manager.update(dt/1000)

        #logger.info(f'Blitting background animation from the MAIN_MENU')
        self.gui_manager.blit_background_animation()
        
        self.gui_manager.draw_gui()

        return State.MAIN_MENU
