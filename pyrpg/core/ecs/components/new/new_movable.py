''' Module "pyrpg.core.ecs.components.new_movable" contains
NewMovable component implemented as a NewMovable class.

Use 'python -m pyrpg.core.ecs.components.new_movable -v' to run
module tests.
'''

import pygame
from pyrpg.core.ecs.components.component import Component

class NewMovable(Component):
    ''' Entity can move.

    Used by:
        -   NewProcessMovementProcessor

    Examples of JSON definition:
        {"type" : "NewMovable", "params" : {"velocity" : 100}},
        {"type" : "NewMovable", "params" : {"velocity" : 100, "accelerate" : 10}},

    Tests:
        >>> c = NewMovable(**{"velocity" : 100, "accelerate" : 10})
        >>> c.velocity
        100
        >>> c.accelerate
        10
    '''

    __slots__ = ['velocity', 'accelerate', '_last_move_time', '_last_velocity', '_last_accelerate']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new NewMovable component.

        Parameters:
            :param accelerate: Pace of acceleration.
            :type accelerate: int

            :param velocity: Speed of the movement.
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
