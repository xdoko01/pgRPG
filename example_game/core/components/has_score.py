''' Module "example_game.core.components.has_score" contains
Score component implemented as a HasScore class.

Use 'python -m example_game.core.components.has_score -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

class HasScore(Component):
    ''' Entity can have score calculated.

    Used by:
        -   CalculateScoreProcessor

    Examples of JSON definition:
        {"type" : "HasScore", "params" : {"score" : 100}},

    Tests:
        >>> c = HasScore(**{"score" : 100})
        >>> c.score
        100
        >>> c.delegate
        None
    '''

    __slots__ = ['score']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new HasScore component.

        Parameters:
            :param score: Count of HasScore points.
            :type score: int

            :param delegate: Entity Id of the entity to which score should be added
            :type delegate: int

            :raise ValueError: In case 'score' or 'delegate' is not integer.
        '''
        super().__init__()

        # Get the score and delegate
        self.score = kwargs.get('score', 0)

        # Assert that score is int
        try:
            assert isinstance(self.score, int), f'Parameter score is not an int for {self.__class__} component.'

        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
