''' Module "pyrpg.core.ecs.components.flag_add_score" contains
FlagAddScore component implemented as a FlagAddScore class.

Use 'python -m pyrpg.core.ecs.components.flag_add_score -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagAddScore(Component):
    ''' Flag/tag to mark entity(generator) which has scored
    some points.

    Used by:
        - GenerateScoreOnDestroyProcessor
        - GenerateScoreOnDamageProcessor
        - CalculateScoreProcessor

    Examples of JSON definition:
        {"type" : "FlagAddScore", "params" : {score : 5}}

    Tests:
        >>> c = FlagAddScore(**{"score" : 5})
        >>> c.score
        5
    '''

    __slots__ = ['score']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new FlagAddScore component.

        Parameters:
            :param score: Count of Score points to be added
            :type score: int
        '''
        super().__init__()

        # Get the score
        self.score = kwargs.get('score')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
