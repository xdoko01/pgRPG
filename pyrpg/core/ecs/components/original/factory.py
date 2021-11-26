''' Module "pyrpg.core.ecs.components.factory" contains
Factory component implemented as a Factory class.

Use 'python -m pyrpg.core.ecs.components.factory -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

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
                "max_units" : 5
            }
        }

    Tests:
        >>> c = Factory(**{"prescription" : {\
                    "templates" : ["sword_swing"],\
                    "components" : [\
                        {"type" : "Debug", "params" : {}}\
                    ]\
                },\
                "max_units" : 5\
            })
    '''

    __slots__ = ['prescription', 'max_units', 'current_units']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the Factory component.

            Parameters:
                :param prescription: Dictionary with prescription describing new entity (mandatory)
                :type prescription: dict

                :param max_units: Number of units to be generated (optional, default None=unlimited)
                :type max_units: int

                :param current_units: Number of units already generated
                :type current_units: int

        '''

        super().__init__()

        # Either define prescription as a json text or as a json entity file
        self.prescription = kwargs.get('prescription')

        # Unlimited number of units in case no units passed in the argument
        self.max_units = kwargs.get('max_units', None)

        # At the start no units are generated
        self.current_units = 0

        try:
            assert isinstance(self.prescription, dict), f'Parameter "prescription" must be in a form of a dictionary'
            assert isinstance(self.max_units, int) or self.max_units is None, f'Parameter "max_units" must be integer or None(unlimited)'
        except AssertionError:
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
