''' Module "pyrpg.core.ecs.components.debug" contains
Debug component implemented as a Debug class.

Use 'python -m pyrpg.core.ecs.components.debug -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class Debug(Component):
    ''' Entity shows debug information.

    Used by:
        - PerformRenderDebugInfoProcessor

    Examples of JSON definition:
        {"type" : "Debug", "params" : {"collision" : {"color" : [125, 125, 125], "width" : 1}, "movement" : {"color" : [0,0,0], "width" : 2}}}

    Tests:
        >>> c = Debug(**{"collision" : {"color" : [125, 125, 125], "width" : 1}, "movement" : {"color" : [0,0,0], "width" : 2}})
        >>> c.collision["color"]
        [125, 125, 125]
        >>> c.movement["width"]
        2
    '''

    __slots__ = ['collision', 'movement']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the Debug component.

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

