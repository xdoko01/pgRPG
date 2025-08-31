''' Module "example_game.core.components.ammo_pack" contains
AmmoPack component implemented as a AmmoPack class.

Use 'python -m example_game.core.components.ammo_pack -v' to run
module tests.
'''

from pyrpg.core.ecs import Component
from .weapon import Weapon

class AmmoPack(Component):
    ''' Entity is an ammo pack if having this component.

    Used by:
        - HasWeapon component
        - CollisionAmmoPackProcessor

    Examples of JSON definition:
        {"type" : "AmmoPack", "params" : {"weapon" : "bow", "type" : "wooden_arrows_pack"}}
        {"type" : "AmmoPack", "params" : {"weapon" : "sword", "type" : "sword_swings_pack"}}

   Tests:
        >>> c = AmmoPack(**{"weapon" : "bow", "type" : "wooden_arrows_pack"})
    '''

    __slots__ = ['weapon', 'type']

    def __init__(self, *args, **kwargs):

        super().__init__()

        # Read the weapon attributes
        try:

            # Weapon type to which the AmmoPack belongs
            self.weapon = kwargs['weapon']

            # AmmoPack type to distinguish among different ammo for the same weapon
            self.type = kwargs['type']

        except KeyError:
            # Notify component factory that initiation has failed
            print(f'Mandatory parameter for component AmmoPack is missing.')
            raise ValueError

        # Assert that ammo pack type exists in list of WEAPONS.keys
        try:
            assert isinstance(self.weapon, str) and self.weapon in Weapon.WEAPONS, f'Unknown weapon type "{self.weapon}" for {self.__class__} component.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
