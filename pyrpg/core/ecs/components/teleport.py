''' Module "pyrpg.core.ecs.components.teleport" contains
Teleport component implemented as a Teleport class.

Use 'python -m pyrpg.core.ecs.components.teleport -v' to run
module tests.
'''

import pyrpg.core.engine as engine # For checking the engine.alias_to_entity - if component has entity as a str as a parameter (HasInventory)
from .component import Component

class Teleport(Component):
    ''' Entity is a teleport - i.e. on collision it changes position of
    the object that collided with the entity.

    Used by:
        - CollisionTeleportProcessor

    Examples of JSON definition:
        {"type" : "Teleport", "params" : {"dest_x" : 0, "dest_y" : 0, "dest_map" : "test_map"}}

    Tests:
        >>> c = Teleport(**{"dest_x" : 0, "dest_y" : 0, "dest_map" : "test_map"})
    '''

    __slots__ = ['dest_x', 'dest_y', 'dest_map', 'key']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new Teleport component.

        Parameters:
            :param dest_x: X-axis position in pixels on the target map (mandatory).
            :type dest_x: int

            :param dest_y: Y-axis position in pixels on the target map (mandatory).
            :type dest_y: int

            :param dest_map: Name of the target map where entity is teleported (mandatory).
            :type dest_map: str

            :param key: Entity representing key that is necessary to be in the inventory in order to teleport (optional).
            :type key: str or int

            :raise: ValueError - in case mandatory parameters are missing.
        '''

        super().__init__()
        
        # Teleport destination - mandatory
        try:
            self.dest_map = kwargs.get('dest_map')
            self.dest_x = kwargs.get('dest_x')
            self.dest_y = kwargs.get('dest_y')
            self.key = kwargs.get('key', None)
        except KeyError:
            # Notify component factory that initiation has failed
            print(f'Mandatory parameters are missing')
            raise ValueError

        # Assert correct data types
        try:
            assert isinstance(self.dest_map, str), f'Map "{self.dest_map}" is not a string for {self.__class__} component.'
            assert isinstance(self.dest_x, int), f'Position x is not an integer for {self.__class__} component.'
            assert isinstance(self.dest_y, int), f'Position y is not an integer for {self.__class__} component.'
            assert isinstance(self.key, int) or self.key is None, f'Teleport key is not an integer for {self.__class__} component.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
