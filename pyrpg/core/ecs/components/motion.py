from .component import Component
import pygame

class Motion(Component):
    ''' Entity can move.

    Used by:
        -   MovementProcessor

    Examples of JSON definition:
        {"type" : "Motion", "params" : {"dx" : 0, "dy" : 0}},

    Tests:
        >>> c = Motion()
    '''

    __slots__ = ['dx', 'dy', 'enabled', 'last_move']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new Motion component.

        Parameters:
            :param dx: X-axis delta movement component.
            :type dx: float

            :param dy: Y-axis delta movement component.
            :type dy: float

            :raise: ValueError - in case movement params are not numbers.
        '''
        super().__init__()

        # Change of position
        self.dx = kwargs.get('dx', 0.0)
        self.dy = kwargs.get('dy', 0.0)

        # Assert that dx, dy are numbers
        try:
            assert isinstance(self.dx, int) or isinstance(self.dx, float), f'Movement dx is not a number for {self.__class__} component.'
            assert isinstance(self.dy, int) or isinstance(self.dy, float), f'Movement dy is not a number for {self.__class__} component.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

        # Entity movement can be freezed by command - used in scripted cinematics
        self.enabled = True

        # Remember if entity has moved
        self.has_moved = False

        # Remember time when the entity last moved
        # Necessary to know when to reset the direction of the entity due to rendering
        self.last_move = pygame.time.get_ticks()
