''' Module "pyrpg.core.ecs.components.new_flag_create_from_factory" contains
NewFlagCreateFromFactory component implemented as a NewFlagCreateFromFactory class.

Use 'python -m pyrpg.core.ecs.components.new_flag_create_from_factory -v' to run
module tests.
'''

from .component import Component

class NewFlagCreateFromFactory(Component):
    ''' Flag to create new entity from Factory component
    based on additional data contained in this component.

    Used by:
        - NewGenerateProjectileFactoryDataProcessor
        - NewRemoveFlagCreateFromFactoryProcessor

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
        >>> c = NewFlagCreateFromFactory(position=(5, 5, 'left', 'new_map'))
        >>> c.position
        (5, 5, 'left', 'new_map')
    '''

    __slots__ = ['position', 'register', 'id_suffix']

    def __init__(self, position=False, register=False, id_suffix='from_factory'):
        ''' Initiate values for the NewFlagCreateFromFactory component.

        Parameters:
            :param position: Position where the new entity must be generated
            :type position: tuple

            :param register: Should the entity be globally registered with engine
            :type register: bool

            :param id_suffix: Text that is added to Factory prescription entity ID during generation.
            :type id_suffix: str

            :raise: ValueError - in case of incorrect position
        '''
        super().__init__()

        self.position = position
        self.register = register
        self.id_suffix = id_suffix

if __name__ == '__main__':
    import doctest
    doctest.testmod()

