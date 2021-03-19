from .component import Component
import core.models as model

class Weapon(Component):
	''' Entity is a weapon if having this component.
	Weapon has its parameters determined by weapon type.
	'''

	WEAPONS = {
		'bow' : { 'action' : 'shoot', 'idle' : 'idle_shoot' },
		'spear' : { 'action' : 'stab', 'idle' : 'idle_stab' },
		'sword' : { 'action' : 'swing', 'idle' : 'idle_swing' },
		'spell' : { 'action' : 'cast', 'idle' : 'idle_cast' }
	}
 
	__slots__ = ['action', 'idle', 'type']

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
			
			#self.projectile_collision_zones = kwargs.get('projectiles', {}).get('projectile_collision_zones', {})

			# Weapon causes damage - default 10 points
			#self.damage = kwargs.get('projectiles', {}).get('damage', 1)

			#self.projectile_ttl =  kwargs.get('projectiles', {}).get('ttl', 100)

			#self.projectile_speed =  kwargs.get('projectiles', {}).get('speed', 100)

		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Mandatory parameters are missing.')
			raise ValueError

		# Assert that weapon type exists in list of WEAPONS
		try:
			assert isinstance(self.type, str) and self.type in Weapon.WEAPONS, f'Unknown weapon type "{self.type}" for {self.__class__} component.'
			assert isinstance(self.action, str) and self.action in model.Model.ACTIONS, f'Unknown animation action "{self.action}" for {self.__class__} component.'
			assert isinstance(self.idle, str) and self.action in model.Model.ACTIONS, f'Unknown idle animation "{self.idle}" for {self.__class__} component.'
			assert isinstance(self.max_projectiles, int), f'Max no. of projectiles must be an integer "{self.max_projectiles}" for {self.__class__} component.'
			#assert isinstance(self.damage, int), f' Damage must be an integer "{self.damage}" for {self.__class__} component.'
			#assert isinstance(self.projectile_ttl, int), f' Projectile ttl must be an integer "{self.projectile_ttl}" for {self.__class__} component.'
			#assert isinstance(self.projectile_speed, int), f' Projectile speed must be an integer "{self.projectile_speed}" for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError
