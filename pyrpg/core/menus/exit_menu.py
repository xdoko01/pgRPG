import logging

from pygame_gui import UI_WINDOW_CLOSE, UI_CONFIRMATION_DIALOG_CONFIRMED
from pyrpg.core.config.states import State
from pygame_gui.windows import UIConfirmationDialog
from pygame import Rect
from .menu import Menu

# Initiate logging of module
logger = logging.getLogger(__name__)

class ExitMenu(Menu):
    '''Class implementing the exit dialog'''

    def __init__(self, gui_manager, state_manager) -> None:
        self.gui_manager = gui_manager
        self.state_manager = state_manager

        self.exit_dialog = None

        logger.info(f'Exit menu dialog initiated')

    def show(self) -> None:
        '''Each time the exit dialog must be created. When closed it is destroyed automatically. '''
        self.exit_dialog = UIConfirmationDialog(
                rect=Rect(self.gui_manager._gui_dlg_start, self.gui_manager._gui_dlg_dim),
                manager=self.gui_manager.window_manager,
                action_long_desc='Do you want to exit the game?',
                action_short_name='Exit')

        logger.info(f'Exit dialog created')

    def hide(self):
        '''Hiding is not needed as dialog is destroyed upon closing'''
        raise NotImplementedError

    def run(self, key_events, key_pressed, dt) -> State:

        # If exit menu accessed from other game state, create new exit dialog
        if self.state_manager.changed_game_state:
            self.show()

        for event in key_events:
            if event.type == UI_CONFIRMATION_DIALOG_CONFIRMED:
                logger.info(f'Exiting the game')
                return State.END_PROGRAM
            elif event.type == UI_WINDOW_CLOSE and self.state_manager.prev_game_state:
                logger.info(f'Closing the exit window')
                return self.state_manager.prev_game_state

            self.gui_manager.process_events(event)

        self.gui_manager.update(dt/1000)

        self.gui_manager.blit_background_animation()

        self.gui_manager.draw_gui()

        return State.EXIT_GAME_DIALOG
