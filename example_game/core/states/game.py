''' Module implementing the behavior wher program is in GAME state 

For tests call `python -m pyrpg.core.states.game -v`

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

### PUT ALL YOUR OPTIONAL IMPORTS HERE
import pygame
from pyrpg.core import engine
from pyrpg.core.config import KEYS # for K_CONSOLE_TOGGLE, K_SAVE_GAME, K_LOAD_GAME

# Global switch for the processors groups
proc_group_id: str = 'default'

### DO NOT REMOVE - Mandatory execution function called every cycle when engine in the State
def run(key_events, key_pressed, dt, debug: bool=False) -> State:
    '''The main loop for the given state.
    '''

    # Process the events
    for event in key_events:
        
        # On closing of the game window -> show the exit confirmation dialog
        if event.type == pygame.QUIT:
            return State.EXIT_GAME_DIALOG
    
        elif event.type == pygame.KEYDOWN:

            # On pushing the ESC button -> go back to main menu
            if event.key == pygame.K_ESCAPE:
                #self.gui_manager.save_screen()
                return State.MAIN_MENU

            # On pushing the INVENTORY button ->
            elif event.key == KEYS["K_INVENTORY_TOGGLE"]:
                # Toggle between inventory and default process group
                global proc_group_id
                proc_group_id = 'inventory' if proc_group_id == 'default' else 'default'

            # On pushing the SAVE GAME button -> not implemented yet
            elif event.key == KEYS["K_SAVE_GAME"]:
                raise NotImplementedError

            # On pushing the LOAD GAME button -> not implemented yet
            elif event.key == KEYS["K_LOAD_GAME"]:
                raise NotImplementedError

        elif event.type == pygame.KEYUP:
            
            # On pushing the CONSOLE_TOGGLE button -> go to console
            if event.key == KEYS["K_CONSOLE_TOGGLE"]: 
                return State.CONSOLE

    # Run all the game processors
    engine.ecs_manager.process(proc_group_id=proc_group_id, events=key_events, keys=key_pressed, dt=dt, debug=debug)

    # Repeat the cycle next time, if State was not changed by above events
    return State.GAME
