from pyrpg.core.states.state import State

# Init logging config
import logging
logger = logging.getLogger(__name__)

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
