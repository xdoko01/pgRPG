''' Module "pyrpg.core.ecs.components.has_score" contains
Score component implemented as a HasScore class.

Use 'python -m pyrpg.core.ecs.components.has_score -v' to run
module tests.
'''

from .component import Component

class HasScore(Component):
    ''' Entity can have score calculated.

    Used by:
        -   CalculateScoreProcessor

    Examples of JSON definition:
        {"type" : "HasScore", "params" : {"score" : 100}},
        {"type" : "HasScore", "params" : {"delegate" : 3}}

    Tests:
        >>> c = HasScore(**{"score" : 100})
        >>> c.score
        100
        >>> c.delegate
        None
    '''

    __slots__ = ['score', 'delegate']

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
        self.delegate = kwargs.get('delegate', None)

        # Assert that score is int
        try:
            assert isinstance(self.score, int), f'Parameter score is not an int for {self.__class__} component.'
            assert isinstance(self.delegate, int) or not self.delegate, f'Parameter delegate is not an int for {self.__class__} component.'

        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
