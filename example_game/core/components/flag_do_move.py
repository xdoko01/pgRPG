''' Module "example_game.core.components.flag_do_move" contains
FlagDoMove component implemented as a FlagDoMove class.

Use 'python -m example_game.core.components.flag_do_move -v' to run
module tests.
'''
from dataclasses import dataclass
from pyrpg.core.ecs import Component

class FlagDoMove(Component):
    ''' Entity can move.

    Used by:
        -   NewProcessMovementProcessor

    '''

    __slots__ = ['moves', 'vector', 'dt_on', 'absolute']

    def __init__(self, moves=[], vector=None, dt_on=True, absolute=False):
        ''' Initiate values for the new FlagDoMove component.

        Parameters:
            :param moves: Listof moves done by the entity.
            :type moves: list

            :param vector: List/tuple (dx, dy) to store the movement vector.
            :type vector: list

            :param dt_on: Flag if the delta time dt should be take into 
                account in processor for movement compensation.
            :type dt_on: bool

            :param absolute: True if entity should be moved by exactly the vector
                without taking into acount the Movable velocity/acceleration.
            :type absolute: bool

                            '''
        super().__init__()

        # Intit the list of moves and vector
        self.moves = moves
        self.vector = vector
        self.dt_on = dt_on
        self.absolute = absolute

    def add_moves(self, moves_list):
        ''' Adds more moves to the FlagDoMove
        '''
        self.moves = [*self.moves, *moves_list]

    def calc_vector(self):
        ''' Calculate the UNIT vector based on the list of moves.
        Only calculate if no vector is present. Important for usage
        of move command that has vector on input.
        '''
        self.vector = [0, 0]

        for move in self.moves:
            if move == 'left': self.vector[0] -= 1
            elif move == 'right': self.vector[0] += 1
            elif move == 'up': self.vector[1] -= 1
            elif move == 'down': self.vector[1] += 1

        # Compensate the speed of the diagonal movement - division by sqrt(2)
        if self.vector[0] != 0 and self.vector[1] != 0:
            self.vector[0] *= 0.7071
            self.vector[1] *= 0.7071

# Mock component for usage in tests
@dataclass
class FlagDoMoveMock:
    moves: list = None
    vector: tuple = None
    dt_on: bool = True
    absolute: bool = False
    add_moves = lambda self, m: None
    calc_vector = lambda: None


if __name__ == '__main__':
    import doctest
    doctest.testmod()
