from pyrpg.core.states.state import State

# Init logging config
import logging
logger = logging.getLogger(__name__)

# Get STATES and translate STATES_GRAPH,NON_GAME_STATES, START_STATE to State Enum variables
#from pyrpg.core.states.state import State
#from pyrpg.core.config.states import STATES_GRAPH, NON_GAME_STATES, START_STATE

from pyrpg.core.config import STATES

from enum import Enum
State = Enum("State", STATES["ALL_STATES"])
STATES["START_STATE"] = State[STATES["START_STATE"]]
STATES["ALL_STATES"] = [State[s] for s in STATES["ALL_STATES"].copy()]
STATES["NON_GAME_STATES"] = [State[s] for s in STATES["NON_GAME_STATES"].copy()]

new_states_graph = dict()
for k, v in STATES["STATES_GRAPH"].items():
    new_states_graph[State[k]] = [State[s] for s in v.copy()]
STATES["STATES_GRAPH"] = new_states_graph

#print(f'{STATES=}')

# Globals
state_graph: dict | None = None
all_states: list | None = None
non_game_states: list | None = None
game_states: list | None = None

state: State | None = None
prev_state: State | None = None
game_state: State | None = None
prev_game_state: State | None = None

changed: bool = False # If the change happened in current loop, set to True else false
changed_game_state: bool = False

state_modules: dict = None

def init(states: dict) -> None:

    print(f'{STATES=}')

    global all_states
    all_states = states["ALL_STATES"]

    global state_graph
    state_graph = states["STATES_GRAPH"]

    global non_game_states
    non_game_states = states["NON_GAME_STATES"]

    global game_states
    game_states = [state for state in all_states if state not in non_game_states]

    global state
    try:
        # Current state
        assert states["START_STATE"] in all_states, logger.error(f'State {states["START_STATE"]} is not within the list of possible states "{all_states}".')

        state = states["START_STATE"]

        logger.info(f'StateManager initialized into state "{state}".')
    except AssertionError:
        raise

    global game_state
    game_state = state if state in game_states else None

    ### NEW - initialize module for every state
    ##from pyrpg.core.config import MODULEPATHS
    ##from importlib import import_module

    # Here all state modules are stored
    ##global state_modules
    ##state_modules = {}

    ##for s in STATES["ALL_STATES"]:
    ##    print(s.name.lower())
    ##    try:
    ##        state_module = import_module(f'{MODULEPATHS["STATE_MODULE_PATH"]}.{s.name.lower()}')
    ##        state_modules[s] = state_module
    ##        logger.info(f'State module registered {state_modules[s]=}.')
    ##    except ModuleNotFoundError:
    ##        logger.info(f'State module not found for {s=}.')

    # Register all state modules in the state_modules dictionary where keys are the states
    _initialize_state_modules()

def _initialize_state_modules() -> None:
    """Initialize and register all state modules with the state manager.
    """
    from pyrpg.core.config import MODULEPATHS
    from importlib import import_module

    global state_modules
    state_modules = {}

    for s in STATES["ALL_STATES"]:
        try:
            state_module = import_module(f'{MODULEPATHS["STATE_MODULE_PATH"]}.{s.name.lower()}')
            state_module.initialize(state=s, register_fnc=_register_state_module)
        except ModuleNotFoundError:
            logger.info(f'State module not found for {s=}.')


def _register_state_module(state: State, module) -> None:
    """Register the state module. Called by the state module.
    """
    #global state_modules
    state_modules[state] = module


def get_avail_states() -> list:
    """Return allowed states for continuation.
    """
    #global state_graph
    try:
        return state_graph[state]
    except KeyError:
        raise ValueError(f"No available states for State '{state}'.")

def change_state(new_state: str) -> None:
    '''Changes the game state and saves the previous state.'''

    global changed
    global changed_game_state
    global prev_state, state, game_state, prev_game_state

    if new_state == state: 
        changed = False
        changed_game_state = False
        return

    if new_state in get_avail_states():
        changed = True

        prev_state, state = state, new_state

        logger.info(f'State changed from "{prev_state}" to "{state}".')

        if new_state in game_states:

            if new_state == game_state:
                changed_game_state = False
                return

            changed_game_state = True

            prev_game_state, game_state = game_state, new_state
            logger.info(f'Game state changed from "{prev_game_state}" to "{game_state}".')

        logger.info(f'GAME STATE variables: prev_game_state={prev_game_state}, game_state={game_state}, changed_game_state={changed_game_state}')
        logger.info(f'STATE variables: prev_state={prev_state}, state={state}, changed_state={changed}')
    else:
        logger.warning(f'Cannot change from "{state}" to state "{new_state}". Available states are "{get_avail_states()}".')

def revert_state() -> None:
    '''Return to the previous game state.'''
    change_state(prev_state)

def clear() -> None:
    pass


'''
STATES_GRAPH = {
    State.START_PROGRAM    : [State.MAIN_MENU,  State.GAME],
    State.MAIN_MENU        : [State.LOAD_QUEST_MENU, State.EXIT_GAME_DIALOG, State.CONSOLE],
    State.LOAD_QUEST_MENU  : [State.MAIN_MENU, State.GAME, State.CONSOLE],
    State.GAME             : [State.MAIN_MENU, State.PAUSE_GAME, State.CONSOLE, State.EXIT_GAME_DIALOG],
    State.PAUSE_GAME       : [State.GAME, State.CONSOLE],
    State.CONSOLE          : [State.MAIN_MENU, State.LOAD_QUEST_MENU, State.GAME],
    State.EXIT_GAME_DIALOG : [State.END_PROGRAM, State.GAME, State.MAIN_MENU],
    State.END_PROGRAM      : []
}

NON_GAME_STATES = [State.CONSOLE, State.START_PROGRAM, State.END_PROGRAM]

START_STATE = State.START_PROGRAM

logger.debug(f"States config initiated.")
'''