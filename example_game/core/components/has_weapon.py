''' Module "pyrpg.core.ecs.components.has_weapon" contains
HasWeapon component implemented as a HasWeapon class.

Use 'python -m pyrpg.core.ecs.components.has_weapon -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class HasWeapon(Component):
    ''' Entity can pickup and arm a Weapon.

    Used by:
        - PerformArmWeaponProcessor

    Examples of JSON definition:
        {"type" : "HasWeapon", "params" : {}}
        {"type" : "HasWeapon", "params" : {
            "weapons" : {
                "sword" : {"weapon" : "long_sword", "generator" : None},
                "bow" : {"weapon" : "wooden_bow", "generator" : "pack_of_arrows"}
            }
        }}

    Tests:
        >>> c = HasWeapon()
    '''

    __slots__ = ['weapons']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the HasWeapon component.

        Parameters:
            :param weapons: Dictionary containing weapons available for entity (optional, default {})
            :type weapons: dict
        '''
        super().__init__()

        # By default component does not store any weapons
        default_weapons = {
            "sword" : {"weapon" : None, "generator" : None},
            "spear" : {"weapon" : None, "generator" : None},
            "bow" : {"weapon" : None, "generator" : None},
            "spell" : {"weapon" : None, "generator" : None}
        }

        # Join input parameter weapons with default weapons
        self.weapons = { **default_weapons, **kwargs.get('weapons', {}) }


if __name__ == '__main__':
    import doctest
    doctest.testmod()
