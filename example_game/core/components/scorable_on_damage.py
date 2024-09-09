''' Module "pyrpg.core.ecs.components.scorable_on_damage" contains
ScorableOnDamage component implemented as a ScorableOnDamage class.

Use 'python -m pyrpg.core.ecs.components.scorable_on_damage -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component


class ScorableOnDamage(Component):
    ''' Entity is generating score when damaged.

    Used by:
        -   CollisionScoreDamageProcessor

    Examples of JSON definition:
        {"type" : "ScorableOnDamage", "params" : {"score" : 5}},
        {"type" : "ScorableOnDamage", "params" : {}}

    Tests:
        >>> c = ScorableOnDamage(**{"score" : 4})
        >>> c.score
        4
        >>> c = ScorableOnDamage()
        >>> c.score
        1
    '''

    __slots__ = ['score']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new ScorableOnDamage component.

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