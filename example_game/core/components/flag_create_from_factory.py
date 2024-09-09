''' Module "pyrpg.core.ecs.components.flag_create_from_factory" contains
FlagCreateFromFactory component implemented as a FlagCreateFromFactory class.

Use 'python -m pyrpg.core.ecs.components.flag_create_from_factory -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagCreateFromFactory(Component):
    ''' Flag to create new entity from Factory component
    based on additional data contained in this component.

    Used by:
        - GenerateProjectileFactoryDataProcessor
        - RemoveFlagCreateFromFactoryProcessor

    Examples of JSON definition:
        {"type" : "FlagCreateFromFactory", 
         "params" : { 
             "position" : {
                 "x" : 20,
                 "y" : 20,
                 "dir" : "left",
                 "map" : "test_map"
             }
          }
        }

    Tests:
        >>> c = FlagCreateFromFactory(position=(5, 5, 'left', 'new_map'))
        >>> c.position
        (5, 5, 'left', 'new_map')
    '''

    __slots__ = ['adjust_position', 'register', 'id_suffix', 'ignore_collision_with']

    def __init__(
        self, 
        adjust_position=None, 
        adjust_collision=None, 
        adjust_movement=None, 
        adjust_damaging=None, 
        register=False, 
        id_suffix='from_factory'
    ):
        ''' Initiate values for the FlagCreateFromFactory component.

        Parameters:
            :param adjust_position: Position where the new entity must be generated
            :type adjust_position: dir

            :param adjust_collision: Parameters to adjust existing Collidable component
            :type adjust_collision: dir

            :param adjust_movement: Parameters to adjust existing Movable component
            :type adjust_movement: dir

            :param adjust_damaging: Parameters to adjust existing Damaging component
            :type adjust_damaging: dir

            :param register: Should the entity be globally registered with engine
            :type register: bool

            :param id_suffix: Text that is added to Factory prescription entity ID during generation.
            :type id_suffix: str

            :raise: ValueError - in case of incorrect position
        '''
        super().__init__()

        self.adjust_position = adjust_position
        self.adjust_collision = adjust_collision
        self.adjust_movement = adjust_movement
        self.adjust_damaging = adjust_damaging


        self.register = register
        self.id_suffix = id_suffix

if __name__ == '__main__':
    import doctest
    doctest.testmod()

