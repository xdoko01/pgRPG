''' Module "pyrpg.core.ecs.components.flag_ammo_pack_armed" contains
FlagAmmoPackArmed component implemented as a FlagAmmoPackArmed class.

Use 'python -m pyrpg.core.ecs.components.flag_ammo_pack_armed -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagAmmoPackArmed(Component):
    ''' Flag/tag to mark that AmmoPack is assign to some
    weapon.

    Used by:
        - DisarmDepletedAmmoPackProcessor
        - CollisionAmmoPackProcessor

    Examples of JSON definition:
        {"type" : "FlagAmmoPackArmed", "params" : { "armed_entity" : 2}}
        {"type" : "FlagAmmoPackArmed", "params" : { "armed_entity" : "player01"}}

    Tests:
        >>> c = FlagAmmoPackArmed(armed_entity=2)
        >>> c.armed_entity
        2
    '''

    __slots__ = ['armed_entity']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new FlagAmmoPackArmed component.
        '''

        super().__init__()

        # Store armed entity - entity with HasWeapon component
        self.armed_entity = kwargs.get('armed_entity')


if __name__ == '__main__':
    import doctest
    doctest.testmod()