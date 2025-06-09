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

def run(key_events, key_pressed, dt) -> state_manager.State:

    # End engine
    if _engine: _engine.exit_game()
    logger.info(f'Game closed')

    # End state modules
    for s in state_manager.state_modules:
        state_manager.state_modules[s].clear()

    # Clear Managers
    gui_manager.clear()
    state_manager.clear()

    logger.info(f'Managers closed')

    pygame.quit()


    return state_manager.State.END_PROGRAM

