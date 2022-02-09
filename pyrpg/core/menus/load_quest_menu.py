import logging

from pyrpg.core.config.paths import QUEST_PATH
from pygame_gui import UI_FILE_DIALOG_PATH_PICKED, UI_WINDOW_CLOSE
from pyrpg.core.config.states import State
from pygame_gui.windows import UIFileDialog
from pygame import Rect
from .menu import Menu

# Initiate logging of module
logger = logging.getLogger(__name__)

class LoadQuestMenu(Menu):
    '''Class implementing the load quest dialog'''

    def __init__(self, gui_manager, state_manager, init_game_fnc) -> None:
        self.gui_manager = gui_manager
        self.state_manager = state_manager

        self.init_game_fnc = init_game_fnc

        self.last_quest_path = QUEST_PATH
        self.load_quest_window = None

        logger.info(f'Load quest menu window initiated')

    def show(self) -> None:
        self.load_quest_window = UIFileDialog(
                rect=Rect(self.gui_manager._gui_dlg_start, self.gui_manager._gui_dlg_dim),
                manager=self.gui_manager.window_manager,
                window_title='Load quest',
                initial_file_path=self.last_quest_path,
                allow_existing_files_only=False,
                allow_picking_directories=False)

        logger.info(f'Load quest menu window created')

    def hide(self):
        raise NotImplementedError

    def run(self, key_events, key_pressed, dt) -> State:

        # If load quest menu accessed from other game state, create new exit dialog
        if self.state_manager.changed_game_state:
            self.show()

        for event in key_events:
            if event.type == UI_FILE_DIALOG_PATH_PICKED:
                logger.info(f'Loading game file "{event.text}".')
                self.init_game_fnc(event.text)
                self.last_quest_path = event.text
                return State.GAME
            elif event.type == UI_WINDOW_CLOSE and self.state_manager.prev_game_state:
                logger.info(f'Closing load quest window')
                return self.state_manager.prev_game_state

            self.gui_manager.process_events(event)

        self.gui_manager.update(dt/1000)

        self.gui_manager.blit_background_animation()

        self.gui_manager.draw_gui()

        return State.LOAD_QUEST_MENU
