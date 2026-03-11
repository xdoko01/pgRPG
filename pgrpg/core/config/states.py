"""State machine managing game states (MAIN_MENU, GAME, CONSOLE, etc.).

Dynamically creates a ``State`` enum from config, maintains the state graph
for allowed transitions, and registers per-state Python modules.

Module Globals:
    state: Current State enum value.
    prev_state: Previous State value (for revert).
    game_state: Current game-specific state (None if in a non-game state).
    changed: True if a state transition occurred this frame.
    state_modules: Dict mapping State -> state module instance.
    state_graph: Dict mapping State -> list of allowed next States.
"""

import logging
logger = logging.getLogger(__name__)

from pgrpg.core.config import STATES

from enum import Enum
State = Enum("State", STATES["ALL_STATES"])
STATES["START_STATE"] = State[STATES["START_STATE"]]
STATES["ALL_STATES"] = [State[s] for s in STATES["ALL_STATES"].copy()]
STATES["NON_GAME_STATES"] = [State[s] for s in STATES["NON_GAME_STATES"].copy()]

new_states_graph = dict()
for k, v in STATES["STATES_GRAPH"].items():
    new_states_graph[State[k]] = [State[s] for s in v.copy()]
STATES["STATES_GRAPH"] = new_states_graph

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
    """Initialize the state machine from the config STATES dict.

    Args:
        states: Dict with keys ALL_STATES, STATES_GRAPH, NON_GAME_STATES,
            START_STATE (all already converted to State enum values).
    """
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

    # Register all state modules in the state_modules dictionary where keys are the states
    _initialize_state_modules()

def _initialize_state_modules() -> None:
    """Import and register a Python module for each defined state."""
    from pgrpg.core.config import MODULEPATHS
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
    """Register a state module (callback invoked by the module itself)."""
    state_modules[state] = module


def get_avail_states() -> list:
    """Return the list of states reachable from the current state."""
    try:
        return state_graph[state]
    except KeyError:
        raise ValueError(f"No available states for State '{state}'.")

def change_state(new_state: str) -> None:
    """Transition to a new state if allowed by the state graph.

    Args:
        new_state: The target State enum value.
    """

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
    """Return to the previous game state."""
    change_state(prev_state)

def clear() -> None:
    pass