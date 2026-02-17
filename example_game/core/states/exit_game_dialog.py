''' Module implementing the behavior wher program is in EXIT_GAME_DIALOG state 

For tests call `python -m pgrpg.core.states.exit_date_dialog -v`

State module represents one state only. The name of the module must be the same as the name of the
state in lower case.

State module must consists of following functions:

    - initialize() ... Function that registers the state with the state manager.
    - init() ... Function that passes all the necessary parameters to the state module so it can operate.
'''

######## INIT PART

######## INIT PART

### DO NOT REMOVE
import logging
logger = logging.getLogger(__name__)

import sys
import pgrpg.core.config.states as state_manager # for switching between game states - game <> console <> menu etc.
from pgrpg.core.config.states import State

# Globals
_initialized: bool = False
_init: bool = False

### DO NOT REMOVE - Mandatory registration function
def initialize(state: State, register_fnc) -> None:
    '''State registers itself at state manager.
    Called from state_manager.
    
    Parameters:
        :param register_fnc: Function of state manager to register state module.
        :type register_fnc: func ref
    '''
    register_fnc(state=state, module=sys.modules[__name__])  # mandatory, register the module by state manager
    
    global _initialized
    _initialized = True # mark as initialized

### DO NOT REMOVE - Mandatory init function
def init(*args, **kwargs) -> None:
    '''Pass the parameters necessary for flawless function to the module.
    '''

    # Put any assignments here
    # ...

    global _init
    _init = True

    logger.info(f'State module {sys.modules[__name__]} init done.')

### DO NOT REMOVE - Mandatory clear function
def clear() -> None:
    '''Called when ending the program.
    '''
    # Put anything what needs to be derefferenced here
    # ...

    global _init
    _init = False

    logger.info(f'State module {sys.modules[__name__]} cleared.')

### PUT ALL YOUR OPTIONAL IMPORTS HERE
import pygame
from pygame_gui import UI_WINDOW_CLOSE, UI_CONFIRMATION_DIALOG_CONFIRMED
from pygame_gui.windows import UIConfirmationDialog
from pygame import Rect

import pgrpg.core.config.gui as gui_manager
from pgrpg.core.config import GUI

_exit_dialog: UIConfirmationDialog = None

def _show() -> None:
    '''Each time the exit dialog must be created.
    When closed it is destroyed automatically.
    '''
    global _exit_dialog
    _exit_dialog = UIConfirmationDialog(
            #rect=Rect(self.gui_manager.gui_dlg_start, self.gui_manager.gui_dlg_dim),
            rect=Rect(GUI["DLG_START_PX"], GUI["DLG_DIM_PX"]),
            manager=gui_manager.window_manager,
            action_long_desc='Do you want to exit the game?',
            action_short_name='Exit')

    logger.info(f'Exit dialog created')

### DO NOT REMOVE - Mandatory execution function called every cycle when engine in the State
def run(key_events, key_pressed, dt) -> State:
    '''The main loop for the given state.
    '''

    # If exit menu accessed from other game state, create new exit dialog
    if state_manager.changed: _show()

    # Process the events
    for event in key_events:

        # On closing of the game window -> end the program
        if event.type == pygame.QUIT:
            return State.END_PROGRAM

        # On closing of the dialog window -> revert back to the previous state
        # On cancelation of the dialog -> revert back to the previous state
        if event.type == UI_WINDOW_CLOSE and state_manager.prev_state:
            state_manager.revert_state()
            return state_manager.state

        # On confirmation of the dialog -> end the program
        elif event.type == UI_CONFIRMATION_DIALOG_CONFIRMED:
            return State.END_PROGRAM

        gui_manager.process_events(event)

    gui_manager.update(dt/1000)

    gui_manager.blit_background_animation()

    gui_manager.draw_gui()

    return State.EXIT_GAME_DIALOG
