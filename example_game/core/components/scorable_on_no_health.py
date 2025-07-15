''' Module "pyrpg.core.ecs.components.scorable_on_no_health" contains
ScorableOnNoHealth component implemented as a ScorableOnNoHealth class.

Use 'python -m pyrpg.core.ecs.components.scorable_on_no_health -v' to run
module tests.
'''

from pyrpg.core.ecs import Component


class ScorableOnNoHealth(Component):
    ''' Entity is generating score when 0 health.

    Used by:
        -   GenerateScoreOnNoHealthProcessor

    Examples of JSON definition:
        {"type" : "ScorableOnNoHealth", "params" : {"score" : 5}},
        {"type" : "ScorableOnNoHealth", "params" : {}}

    Tests:
        >>> c = ScorableOnNoHealth(**{"score" : 3})
        >>> c.score
        3
        >>> c = ScorableOnNoHealth()
        >>> c.score
        1
    '''

    __slots__ = ['score']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new ScorableOnNoHealth component.

        Parameters:
            :param score: Count of Score points.
            :type score: int

            :raise ValueError: In case score is not integer.
        '''
        super().__init__()

        # Get the score
        self.score = kwargs.get('score', 1)

        # Assert that score is int
        try:
            assert isinstance(self.score, int), f'Parameter score is not an int for {self.__class__} component.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
