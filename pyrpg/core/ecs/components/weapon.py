from .component import Component
import pyrpg.core.models as model

class Weapon(Component):
    ''' Entity is a weapon if having this component. Weapon has its parameters
    determined by weapon type.

    Used by:
        - TBD

    Examples of JSON definition:
        {"type" : "Weapon", "params" : {"type" : "bow",	"max_projectiles" : 5}}
        {"type" : "Weapon", "params" : {"type" : "sword"}}

   Tests:
        >>> c = Weapon()
    '''

    WEAPONS = {
        'bow' : { 'action' : 'shoot', 'idle' : 'idle_shoot' },
        'spear' : { 'action' : 'stab', 'idle' : 'idle_stab' },
        'sword' : { 'action' : 'swing', 'idle' : 'idle_swing' },
        'spell' : { 'action' : 'cast', 'idle' : 'idle_cast' }
    }

    __slots__ = ['action', 'idle', 'type', 'max_projectiles']

    def __init__(self, *args, **kwargs):

        super().__init__()

        # Read the weapon attributes
        try:

            # Weapon type
            self.type = kwargs.get('type')

            # Weapon animation for attack action
            self.action = Weapon.WEAPONS.get(self.type).get('action')

            # Weapon animation for idle action
            self.idle  = Weapon.WEAPONS.get(self.type).get('idle')

            # Weapon can generate max projectiles
            self.max_projectiles = kwargs.get('max_projectiles', 1)

        except KeyError:
            # Notify component factory that initiation has failed
            print(f'Mandatory parameter weapon type is missing.')
            raise ValueError

        # Assert that weapon type exists in list of WEAPONS
        try:
            assert isinstance(self.type, str) and self.type in Weapon.WEAPONS, f'Unknown weapon type "{self.type}" for {self.__class__} component.'
            assert isinstance(self.action, str) and self.action in model.Model.ACTIONS, f'Unknown animation action "{self.action}" for {self.__class__} component.'
            assert isinstance(self.idle, str) and self.action in model.Model.ACTIONS, f'Unknown idle animation "{self.idle}" for {self.__class__} component.'
            assert isinstance(self.max_projectiles, int), f'Max no. of projectiles must be an integer "{self.max_projectiles}" for {self.__class__} component.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError
