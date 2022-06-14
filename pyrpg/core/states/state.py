from enum import Enum

class State(Enum):
    START_PROGRAM = None
    MAIN_MENU = 1
    GAME = 2
    PAUSE_GAME = 3
    CONSOLE = 4
    END_PROGRAM = 5
    LOAD_QUEST_MENU = 6
    EXIT_GAME_DIALOG = 7