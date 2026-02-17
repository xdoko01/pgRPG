''' Module implementing the behavior wher program is in END_PROGRAM state 

For tests call `python -m pgrpg.core.states.end_program -v`

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

import pygame
from pgrpg.core import engine
from pgrpg.core.config import gui as gui_manager

### DO NOT REMOVE - Mandatory execution function called every cycle when engine in the State
def run(key_events, key_pressed, dt) -> State:
    '''The main loop for the given state.
    '''

    # End engine
    if engine.get_init(): engine.exit_game()
    logger.info(f'Game closed')

    # End state modules
    for s in state_manager.state_modules:
        state_manager.state_modules[s].clear()

    # Clear Managers
    gui_manager.clear()
    state_manager.clear()

    logger.info(f'Managers closed')

    # Exit the program
    pygame.quit()
    sys.exit()

    return State.END_PROGRAM

