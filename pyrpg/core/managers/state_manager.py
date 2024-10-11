'''Persists the game state and manages the transitions'''

# Initiate logging
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.states.state import State

class StateManager:

    def __init__(self, states_graph: dict, start: State, non_game_states: list=None) -> None:
        try:
            self._state_graph = states_graph  # Oriented graph of states represented as a dict
            self._all_states = self._state_graph.keys() # List of all states
            self._non_game_states = non_game_states # List of non-game states
            self._game_states = [state for state in self._all_states if state not in self._non_game_states] # List of game states

            # Current state
            assert start in self._all_states, logger.error(f'State "{start}" is not within the list of possible states "{self._all_states}".')
            self.state = start

            # Previous state - none at the init
            self.prev_state = None

            # Current game state
            self.game_state = self.state if self.state in self._game_states else None
            # Previous game state is none at the init
            self.prev_game_state = None

            self.changed = False # If the change happened in current loop, set to True else false
            self.changed_game_state = False

            logger.info(f'StateManager initialized into state "{self.state}".')
        except AssertionError:
            raise

    def get_avail_states(self) -> list:
        return self._state_graph.get(self.state)

    def change_state(self, new_state: str) -> None:
        '''Changes the game state and saves the previous state.'''

        if new_state == self.state: 
            self.changed = False
            self.changed_game_state = False
            return

        if new_state in self.get_avail_states():
            self.changed = True

            self.prev_state, self.state = self.state, new_state

            logger.info(f'State changed from "{self.prev_state}" to "{self.state}".')

            if new_state in self._game_states:

                if new_state == self.game_state:
                    self.changed_game_state = False
                    return

                self.changed_game_state = True

                self.prev_game_state, self.game_state = self.game_state, new_state
                logger.info(f'Game state changed from "{self.prev_game_state}" to "{self.game_state}".')

            logger.info(f'GAME STATE variables: prev_game_state={self.prev_game_state}, game_state={self.game_state}, changed_game_state={self.changed_game_state}')
            logger.info(f'STATE variables: prev_state={self.prev_state}, state={self.state}, changed_state={self.changed}')
        else:
            logger.warning(f'Cannot change from "{self.state}" to state "{new_state}". Available states are "{self.get_avail_states()}".')

    def revert_state(self) -> None:
        '''Return to the previous game state.'''

        self.change_state(self.prev_state)

    def clear(self) -> None:
        pass

if __name__ == '__main__':
    
    from ...config.states import State, STATES_GRAPH, NON_GAME_STATES, START_STATE

    '''
    STATES_GRAPH = {
        'START_PROGRAM' : ['MAIN_MENU', 'CONSOLE'],
        'MAIN_MENU'     : ['GAME', 'END_PROGRAM', 'CONSOLE'],
        'GAME'          : ['MAIN_MENU', 'PAUSE_GAME', 'CONSOLE'],
        'PAUSE_GAME'    : ['GAME', 'MAIN_MENU', 'CONSOLE'],
        'CONSOLE'       : ['MAIN_MENU', 'GAME'],
        'END_PROGRAM'   : []
    }
    

    NON_GAME_STATES = ['CONSOLE', 'START_PROGRAM', 'END_PROGRAM']
    '''

    state_manager = StateManager(states_graph=STATES_GRAPH, start=START_STATE, non_game_states=NON_GAME_STATES)
    state_manager.change_state(State.MAIN_MENU)
    state_manager.change_state(State.GAME)
    state_manager.change_state(State.CONSOLE)
    state_manager.change_state(State.GAME)
    state_manager.change_state(State.MAIN_MENU)
    state_manager.change_state(State.CONSOLE)
    state_manager.change_state(State.MAIN_MENU)
    state_manager.change_state(State.GAME)
    state_manager.change_state(State.END_PROGRAM)
