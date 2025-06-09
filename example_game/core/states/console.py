''' Module implementing the behavior wher program is in START_PROGRAM state 

For tests call `python -m pyrpg.core.states.start_program -v`

State module represents one state only. The name of the module must be the same as the name of the
state in lower case.

State module must consists of following functions:

    - initialize() ... Function that registers the state with the StateManager.
    - init() ... Function that passes all the necessary parameters to the state module so
                it can operate.
'''

######## INIT PART

### DO NOT REMOVE - Support of command logging
import logging
logger = logging.getLogger(__name__)

import pyrpg.core.config.gui as gui_manager # for manipulation with game screen
import pyrpg.core.config.sound as sound_manager # for menu sounds
import pyrpg.core.config.states as state_manager # for switching between game states - game <> console <> menu etc.

_initialized = False
_inited = False
_engine = None

### DO NOT REMOVE - Mandatory registration function
#def initialize(register, module_name):
#    '''State registers itself at StateManager under specific name
#    that will be used to call the command. More then one name can 
#    be used for the same command if needed.
#    '''
#    register(fnc=process, alias=module_name)  # mandatory, register the process under the name of the module
#    register(fnc=init, alias=module_name+'_init')  # mandatory, register the init under module_init name

def init(engine) -> None:
    print(f'Init called in CONSOLE module. {engine=}')

    global _engine
    _engine = engine

    global _inited
    _inited = True


import pygame
from pyrpg.core.config import cons # handler for manipulation with the game console
from pyrpg.core.config import KEYS # for K_CONSOLE_TOGGLE


def _show() -> None:
    cons.toggle(enable=True)
    gui_manager.save_screen()
    logger.info(f'Entering console')


def run(key_events, key_pressed, dt) -> state_manager.State:

    # Show console when switched from another state to CONSOLE state
    if state_manager.changed:
        print(f'Showing console')
        _show()

    # Necessary for animation
    gui_manager.blit_background()

    for event in key_events:

        # Check for closing the main program window
        if event.type == pygame.QUIT:
            return state_manager.State.EXIT_GAME_DIALOG

        # Hide console
        if event.type == pygame.KEYUP:
            if event.key == KEYS["K_CONSOLE_TOGGLE"]: 
                cons.toggle(enable=False)
                logger.info(f'Exiting console')
                state_manager.revert_state()
                print(f'Console.py ... exiting console back to {state_manager.state=}')
                return state_manager.state

    return state_manager.State.CONSOLE

