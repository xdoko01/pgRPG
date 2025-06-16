''' Module implementing the behavior wher program is in CONSOLE state 

For tests call `python -m pyrpg.core.states.console -v`

State module represents one state only. The name of the module must be the same as the name of the
state in lower case.

State module must consists of following functions:

    - initialize() ... Function that registers the state with the state manager.
    - init() ... Function that passes all the necessary parameters to the state module so it can operate.
'''

######## INIT PART

### DO NOT REMOVE
import logging
logger = logging.getLogger(__name__)

import sys
import pyrpg.core.config.states as state_manager # for switching between game states - game <> console <> menu etc.
from pyrpg.core.config.states import State

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

import pygame
from pyrpg.core.config import gui as gui_manager # for manipulation with game screen
from pyrpg.core.config import cons # handler for manipulation with the game console
from pyrpg.core.config import KEYS # for K_CONSOLE_TOGGLE

def _show() -> None:
    '''Show console when entering the CONSOLE state.
    '''
    cons.toggle(enable=True)
    gui_manager.save_screen()
    logger.info(f'Entering console')

### DO NOT REMOVE - Mandatory execution function called every cycle when engine in the State
def run(key_events, key_pressed, dt) -> State:
    '''The main loop for the given state.
    '''

    # Show console when switched from another state to CONSOLE state
    if state_manager.changed: _show()

    # Necessary for background animation
    gui_manager.blit_background()

    # Process the events
    for event in key_events:

        # Check for closing the main program window
        if event.type == pygame.QUIT:
            cons.toggle(enable=False)
            state_manager.revert_state()
            return State.EXIT_GAME_DIALOG

        # Hide console
        if event.type == pygame.KEYUP:
            if event.key == KEYS["K_CONSOLE_TOGGLE"]: 
                cons.toggle(enable=False)
                logger.info(f'Exiting console')
                state_manager.revert_state()
                return state_manager.state

    return State.CONSOLE

