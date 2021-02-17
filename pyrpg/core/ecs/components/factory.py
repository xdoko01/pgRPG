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

    __slots__ = ['prescription', 'units']

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

    """
    def create_entity(self, owner=None, pos=None, container=None, reg_at_engine=False):
        ''' Create entity from the prescription dictionary
        '''
        # If we want to register generated entity on engine level, we need to generate
        # an uniq name for it.
        if reg_at_engine:
            id_str = f'{self.prescription.get("id", "")}OWN{owner}ORD{self.units}TS{pygame.time.get_ticks()}'
            self.prescription.update({"id": id_str})

        new_entity = engine._create_entity(
            self.prescription,

            # Do not register in engine global variable alias_to_entity - not needed
            register=reg_at_engine
        )

        # Add position component pos = (pos_x, pos_y, pos_dir, pos_map)
        if pos:
            (pos_x, pos_y, pos_dir, pos_map) = pos
            engine.world.add_component(new_entity, Position(x=pos_x, y=pos_y, dir=pos_dir, map=pos_map))

        # Add container component
        if container:
            engine.world.add_component(new_entity, Container(contained_in=container))

        return new_entity
    """

if __name__ == '__main__':
    import doctest
    doctest.testmod()
