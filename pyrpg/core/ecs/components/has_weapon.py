''' Module "pyrpg.core.ecs.components.has_weapon" contains
HasWeapon component implemented as a HasWeapon class.

Use 'python -m pyrpg.core.ecs.components.has_weapon -v' to run
module tests.
'''

from .component import Component

class HasWeapon(Component):
    ''' Entity can pickup and carry a Weapon.

    Used by:
        - CollisionWeaponProcessor

    Examples of JSON definition:
        {"type" : "HasWeapon", "params" : {}}
        {"type" : "HasWeapon", "params" : {
            "weapons" : {
                "sword" : {"weapon" : "long_sword", "generator" : None},
                "bow" : {"weapon" : "wooden_bow", "generator" : "pack_of_arrows"}
            },
            "weapon_in_use" : "sword"
        }}

    Tests:
        >>> c = HasWeapon()
    '''

    __slots__ = ['weapons', 'has_attacked', 'weapon_in_use']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new HasWeapon component.

        Parameters:
            :param weapon_in_use: Which weapon is armed (optional, default None)
            :type weapon_in_use: str

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

        # By default no weapon is selected
        self.weapon_in_use = kwargs.get('weapon_in_use', None)

        # Is set to True if attack action is in progress (command Attack was triggered)
        self.has_attacked = False

        try:
            # Join input parameters with default weapons
            self.weapons = { **default_weapons, **kwargs.get('weapons', {}) }

            # Translate the values (Weapon, generator) to Entity instance if necessary
            for w_key, w_value in self.weapons.items():

                # Translate entity id name to entity id number if needed
                weapon_ent = w_value.get('weapon')
                # Below is OBSOLETE as translation from alias to id is done before creation of component
                #weapon_ent = engine.alias_to_entity.get(weapon_ent) if isinstance(weapon_ent, str) else weapon_ent

                # Translate entity id name to entity id number if needed
                generator_ent = w_value.get('generator')
                # Below is OBSOLETE as translation from alias to id is done before creation of component
                #generator_ent = engine.alias_to_entity.get(generator_ent) if isinstance(generator_ent, str) else generator_ent

                # TODO - check that generator has factory component!!

                # Save the new values in weapons dictionary
                self.weapons.update({w_key : {"weapon" : weapon_ent, "generator" : generator_ent}})

        except KeyError:
            # Notify component factory that initiation has failed
            print(f'Problem with initiating a weapon for the entity')
            raise ValueError

    def set_weapon_in_use(self, type):
        ''' Switches to weapon that is used
        '''
        self.weapon_in_use = type if type in self.weapons.keys() else None

    def get_weapon_in_use(self):
        ''' Returns currently used weapon entity
        '''
        return self.weapons.get(self.weapon_in_use, {}).get('weapon', None)

    def get_generator_in_use(self):
        ''' Returns currently used generator entity
        '''
        return self.weapons.get(self.weapon_in_use, {}).get('generator', None)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
