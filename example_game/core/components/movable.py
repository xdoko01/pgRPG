''' Module "example_game.core.components.movable" contains
Movable component implemented as a Movable class.

Use 'python -m example_game.core.components.movable -v' to run
module tests.
'''

import pygame
from pgrpg.core.ecs import Component

class Movable(Component):
    ''' Entity can move.

    Used by:
        -   NewProcessMovementProcessor

    Examples of JSON definition:
        {"type" : "Movable", "params" : {"velocity" : 100}},
        {"type" : "Movable", "params" : {"velocity" : 100, "accelerate" : 10}},

    Tests:
        >>> c = Movable(**{"velocity" : 100, "accelerate" : 10})
        >>> c.velocity
        100
        >>> c.accelerate
        10
    '''

    __slots__ = ['velocity', 'accelerate', '_last_move_time', '_last_velocity', '_last_accelerate']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new Movable component.

        Parameters:
            :param accelerate: Pace of acceleration (optional).
            :type accelerate: int

            :param velocity: Speed of the movement (mandatory).
            :type velocity: int

            :raise: ValueError - in case movement params are not numbers.
        '''
        super().__init__()

        # Save the speed and acceleration
        self.velocity = kwargs.get('velocity')
        self.accelerate = kwargs.get('accelerate', 0)

        # Intit the last movement time and last velocity
        self._last_move_time = None
        self._last_velocity = None
        self._last_accelerate = None


        # Assert that velocity is integer
        try:
            assert isinstance(self.velocity, int), f'Movement velocity is not an integer for {self.__class__} component.'
            assert isinstance(self.accelerate, int), f'Movement acceleration is not an integer for {self.__class__} component.'

        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

    def stop_movement(self):
        ''' If some entity needs to freeze temporarily, this function is called
        and the original velocity is stored for later restoration by restore_movement
        function.
        '''

        # Store the original velocity for later restoration
        self._last_velocity = self.velocity
        self._last_accelerate = self.accelerate

        # Set velocity to 0
        self.velocity = 0
        self.accelerate = 0

        # Set last movement time
        self._last_move_time = pygame.time.get_ticks()

    def restore_movement(self):
        ''' Restore velocity to the last known value.
        '''

        # Set velocity to the previous value
        self.velocity = self._last_velocity
        self.accelerate = self._last_accelerate

        self._last_velocity = None
        self._last_accelerate = None

        self._last_move_time = pygame.time.get_ticks()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
