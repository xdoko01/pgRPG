''' Module "pyrpg.core.ecs.components.linear_motion" contains
LinearMotion component implemented as a LinearMotion class.

Use 'python -m pyrpg.core.ecs.components.linear_motion -v' to run
module tests.
'''

from .component import Component

class LinearMotion(Component):
    ''' Component marking entity to move at certain speed.

    Used by:
        - MovementProcessor

    Examples of JSON definition:
        {"type" : "LinearMotion", "params" : {"speed" : 10}}

    Tests:
        >>> c = LinearMotion(**{"speed" : 10})
    '''

    __slots__ = ['speed']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new LinearMotion component.

            Parameters:
                :param speed: Speed of the entity (mandatory)
                :type speed: int
        '''

        super().__init__()

        # Change of position
        self.speed = kwargs.get('speed')

        # Assert that speed is a numbers
        try:
            assert isinstance(self.speed, int), f'Movement speed is not a number for {self.__class__} component.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
