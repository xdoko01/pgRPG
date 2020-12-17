''' Module "pyrpg.core.ecs.components.state" contains
State component implemented as a State class.

Use 'python -m pyrpg.core.ecs.components.state -v' to run
module tests.
'''

from .component import Component

class State(Component):
    ''' Represent state of the entity for animation.

    Used by:
        - RenderModelWorldProcessorFullScan
        - RenderModelWorldProcessor

    Examples of JSON definition:
        {"type" : "State", "params" : {}}
        {"type" : "State", "params" : {"state" : "walk"}}

    Tests:
        >>> c = State(**{"state" : "walk"})
    '''

    __slots__ = ['state']

    STATES = ['idle', 'walk', 'idle_stab', 'idle_swing']

    def __init__(self, *args, **kwargs):
        ''' Initiate State component

        Parameters:
            :param state: State of the entity (optional, default = idle)
            :type state: str

            :raise: ValueError - in case state is not defined/allowed
        '''

        try:
            self.state = kwargs.get('state', 'idle') 
            assert isinstance(self.state, str) and self.state in State.STATES, f'State {self.state} is not allowed state'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
