''' Module "pyrpg.core.ecs.components.scorable_on_pickup" contains
ScorableOnPickup component implemented as a ScorableOnPickup class.

Use 'python -m pyrpg.core.ecs.components.scorable_on_pickup -v' to run
module tests.
'''

from pyrpg.core.ecs import Component


class ScorableOnPickup(Component):
    ''' Entity is generating score when picked up.

    Used by:
        -   GenerateScoreOnPickupProcessor

    Examples of JSON definition:
        {"type" : "ScorableOnPickup", "params" : {"score" : 5}},
        {"type" : "ScorableOnPickup", "params" : {}}

    Tests:
        >>> c = ScorableOnPickup(**{"score" : 4})
        >>> c.score
        4
        >>> c = ScorableOnPickup()
        >>> c.score
        1
    '''

    __slots__ = ['score']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new ScorableOnPickup component.

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