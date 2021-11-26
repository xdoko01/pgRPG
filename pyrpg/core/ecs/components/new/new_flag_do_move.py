''' Module "pyrpg.core.ecs.components.new_flag_do_move" contains
NewFlagDoMove component implemented as a NewFlagDoMove class.

Use 'python -m pyrpg.core.ecs.components.new_flag_do_move -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class NewFlagDoMove(Component):
    ''' Entity can move.

    Used by:
        -   NewProcessMovementProcessor

    '''

    __slots__ = ['moves', 'vector']

    def __init__(self, moves=[], vector=None):
        ''' Initiate values for the new NewFlagDoMove component.

        Parameters:
            :param moves: Listof moves done by the entity.
            :type moves: list

            :param vector: List/tuple (dx, dy) to store the movement vector.
            :type vector: list
        '''
        super().__init__()

        # Intit the list of moves and vector
        self.moves = moves
        self.vector = vector

    def add_moves(self, moves_list):
        ''' Adds more moves to the NewFlagDoMove
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
