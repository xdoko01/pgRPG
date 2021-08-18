''' Module "pyrpg.core.ecs.components.flag_add_score" contains
FlagAddScore component implemented as a FlagAddScore class.

Use 'python -m pyrpg.core.ecs.components.flag_add_score -v' to run
module tests.
'''

from .component import Component

class FlagAddScore(Component):
    ''' Flag/tag to mark entity(generator) which has scored
    some points.

    Used by:
        - CollisionScoreProcessor
        - CalculateScoreProcessor

    Examples of JSON definition:
        {"type" : "FlagAddScore", "params" : {add_score : 5}}

    Tests:
        >>> c = FlagAddScore(**{"add_score" : 5})
        >>> c.add_score
        5
    '''

    __slots__ = ['add_score']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new FlagAddScore component.

        Parameters:
            :param add_score: Count of Score points to be added
            :type score: int
        '''
        super().__init__()

        # Get the score
        self.add_score = kwargs.get('add_score')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
