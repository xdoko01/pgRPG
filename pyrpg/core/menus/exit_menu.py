import logging

from pygame_gui import UI_WINDOW_CLOSE, UI_CONFIRMATION_DIALOG_CONFIRMED
from pyrpg.core.config.states import State
from pygame_gui.windows import UIConfirmationDialog
from pygame import Rect

# Initiate logging of module
logger = logging.getLogger(__name__)

class ExitMenu:

    def __init__(self, gui_manager, state_manager) -> None:
        self.gui_manager = gui_manager
        self.state_manager = state_manager
        self.exit_dialog = None

        logger.info(f'Exit menu dialog initiated')

    def show(self) -> None:
        self.exit_dialog = UIConfirmationDialog(
                rect=Rect(self.gui_manager._gui_dlg_start, self.gui_manager._gui_dlg_dim),
                manager=self.gui_manager.window_manager,
                action_long_desc='Do you want to exit the game?',
                action_short_name='Exit')

        logger.info(f'Exit dialog created')

    def run(self, key_events, key_pressed, dt) -> State:

        # If first time coming from the game to the loop, generate the gui window again
        if self.state_manager.changed_game_state:
            #self.gui_manager.save_screen()
            self.show()

        for event in key_events:
            if event.type == UI_CONFIRMATION_DIALOG_CONFIRMED:
                logger.info(f'Exiting the game')
                return State.END_PROGRAM
            elif event.type == UI_WINDOW_CLOSE and self.state_manager.prev_game_state: # if MAIN_MENU is accessed from other existing state other than None
                logger.info(f'Closing load quest window')
                return self.state_manager.prev_game_state

            self.gui_manager.process_events(event)

        self.gui_manager.update(dt/1000)
        #self.gui_manager.blit_background()
        self.gui_manager.blit_background_animation()

        self.gui_manager.draw_gui()

        return State.EXIT_GAME_DIALOG
