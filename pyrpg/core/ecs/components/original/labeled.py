''' Module "pyrpg.core.ecs.components.labeled" contains
Labeled component implemented as a Labeled class.

Use 'python -m pyrpg.core.ecs.components.labeled -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class Labeled(Component):
    ''' Entity has some id and name that is used in configuration files (json)
    to refer to the entity.

    Used by:
        - RenderDebugProcessor

    Examples of JSON definition:
        {"type" : "Labeled", "params" : {"id" : "player01", "name" : "First Player"}}

    Tests:
        >>> c = Labeled(**{"id" : "player01", "name" : "First Player"})
        >>> c.id
        'player01'
    '''

    __slots__ = ['id', 'name']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the  Labeled component.

        Parameters:
            :param id: Game ID of the entity. Can differ from ECS entity id
            :type id: str

            :param name: Game name of the entity
            :type name: str
        '''
        super().__init__()

        self.id = kwargs.get("id", None)
        self.name = kwargs.get("name", None)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
