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
    print(f'Init called in GAME module. {engine=}')

    global _engine
    _engine = engine

    global _inited
    _inited = True

import pygame
from pyrpg.core.config import KEYS # for K_CONSOLE_TOGGLE

def run(key_events, key_pressed, dt, debug: bool=False) -> state_manager.State:
    logger.debug(f'Start of "run" function.')

    # Check for End Game
    for event in key_events:
        if event.type == pygame.QUIT:
            logger.info(f"Exiting the game")
            return state_manager.State.EXIT_GAME_DIALOG
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                #self.gui_manager.save_screen()
                logger.info(f"Leaving to main menu")
                return state_manager.State.MAIN_MENU
        elif event.type == pygame.KEYUP:
            if event.key == KEYS["K_CONSOLE_TOGGLE"]: 
                print(f'Game.py ... returning State.CONSOLE')
                return state_manager.State.CONSOLE


            ##elif event.key == KEYS["K_SAVE_GAME"]:
            ##    pass
            ##elif event.key == KEYS["K_LOAD_GAME"]:
            ##    pass

    # maps and scenes added in order that command can be informed about scene to change the phase
    _engine.ecs_manager.process(events=key_events, keys=key_pressed, dt=dt, debug=debug)

    return state_manager.State.GAME
