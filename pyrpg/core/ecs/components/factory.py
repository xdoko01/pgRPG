''' Module "pyrpg.core.ecs.components.factory" contains
Factory component implemented as a Factory class.

Use 'python -m pyrpg.core.ecs.components.factory -v' to run
module tests.
'''

from .component import Component

class Factory(Component):
    ''' Factory component enables creation of new entity based
    on prescription given by the parameters.

    Used by:
        - HasWeapon component

    Examples of JSON definition:
        {"type" : "Factory", "params" : {
                "prescription" : {
                    "templates" : ["sword_swing"],
                    "components" : [
                        {"type" : "Debug", "params" : {}}
                    ]
                },
                "units" : 5
            }
        }

    Tests:
        >>> c = Factory(**{"prescription" : {\
                    "templates" : ["sword_swing"],\
                    "components" : [\
                        {"type" : "Debug", "params" : {}}\
                    ]\
                },\
                "units" : 5\
            })
    '''

    __slots__ = ['prescription', 'units', 'list_of_entities']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the Factory component.

            Parameters:
                :param prescription: Dictionary with prescription describing new entity (mandatory)
                :type prescription: dict

                :param units: Number of units to be generated (optional, default None=unlimited)
                :type units: int
        '''

        super().__init__()

        # Either define prescription as a json text or as a json entity file
        self.prescription = kwargs.get('prescription')

        # Unlimited number of units in case no units passed in the argument
        self.units = kwargs.get('units', None)

        try:
            assert isinstance(self.prescription, dict), f'Prescription must be in a form of dictionary'
            assert isinstance(self.units, int) or self.units is None, f'Units must be integer or None(unlimited)'
        except AssertionError:
            raise ValueError

        # Remember the created child entities - set of ints representing entities
        self.list_of_entities = set()

    def remove_entity(self, entity):
        ''' Removes child entity from the list of entities
        that is implemented as a set.
        '''
        self.list_of_entities.remove(entity)
        print(f'Entity {entity} deleted. List of entities {self.list_of_entities}')

if __name__ == '__main__':
    import doctest
    doctest.testmod()
