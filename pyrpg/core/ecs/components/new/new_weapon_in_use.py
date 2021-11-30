''' Module "pyrpg.core.ecs.components.new_weapon_in_use" contains
NewWeaponInUse component implemented as a NewWeaponInUse class.

Use 'python -m pyrpg.core.ecs.components.new_weapon_in_use -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component
from .weapon import Weapon

class NewWeaponInUse(Component):
    ''' Entity has armed the weapon and is using this weapon type for
    attack.

    Used by:
        - PerformArmWeaponProcessor
        - PerformActionAnimationProcessor

    Examples of JSON definition:
        {"type" : "NewWeaponInUse", "params" : {"type" : "bow"}}

    Tests:
        >>> c = NewWeaponInUse(type="bow")
        >>> t = (c.type, c.action, c.idle_action)
        >>> t
        ('bow', 'shoot', 'idle_shoot')
    '''

    __slots__ = ['type', 'action', 'idle_action']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new NewWeaponInUse component.

        Parameters:
            :param type: Type of weapon in use (bow, sword, spell, spear)
            :type type: str

            :param action: Animation action value for usage in animation processor (optional)
            :type action: str

            :param idle_action: Animation idle action value for usage in animation processor (optional)
            :type idle_action: str
        '''
        super().__init__()

        self.type = kwargs.get('type')

        # Get the action and idle action for weapon type from
        try:
            self.action = kwargs.get('action', Weapon.WEAPONS.get(self.type).get('action'))
            self.idle_action = kwargs.get('idle_action', Weapon.WEAPONS.get(self.type).get('idle'))
        except KeyError:
            raise ValueError(f'Weapon type "{self.type}" does not have specified "action" and/or "idle_action".') 


if __name__ == '__main__':
    import doctest
    doctest.testmod()
