''' Module "pyrpg.core.ecs.components.new_debug" contains
NewDebug component implemented as a NewDebug class.

Use 'python -m pyrpg.core.ecs.components.new_debug -v' to run
module tests.
'''

from .component import Component

class NewDebug(Component):
    ''' Entity shows debug information.

    Used by:
        - NewPerformRenderDebugInfoProcessor

    Examples of JSON definition:
        {"type" : "NewDebug", "params" : {"collision" : {"color" : [125, 125, 125], "width" : 1}, "movement" : {"color" : [0,0,0], "width" : 2}}}

    Tests:
        >>> c = NewDebug(**{"collision" : {"color" : [125, 125, 125], "width" : 1}, "movement" : {"color" : [0,0,0], "width" : 2}})
        >>> c.collision["color"]
        [125, 125, 125]
        >>> c.movement["width"]
        2
    '''

    __slots__ = ['collision', 'movement']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the NewDebug component.

        Parameters:
            :param collision: Properties for displaying debug information about collision zone
            :type collision: dict

            :param movement: Properties for displaying debug information about movement
            :type movement: dict
        '''

        super().__init__()

        self.collision = kwargs.get('collision', {'color' : [0, 0, 255], 'width' : 1})
        self.movement = kwargs.get('movement', {'color' : [255, 0, 0], 'width' : 1})
        
        # Dictionary of information that we want to display about the entity.
        # It is filled by debug processor and also displayed there.
        self.info = {}

        try:
            assert isinstance(self.collision, dict), f'Collision must be passed as a dictionary'
            assert isinstance(self.movement, dict), f'Movement must be passed as a dictionary.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()

