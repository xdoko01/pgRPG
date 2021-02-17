from .component import Component
from .weapon import Weapon
from .factory import Factory
import core.engine as engine # For checking the engine.alias_to_entity - if component has entity as a str as a parameter (HasInventory)

class HasWeapon(Component):
	''' Entity can pickup and carry a Weapon 

	Used by:
		-	CollisionWeaponProcessor

	Tests:
		>>> c = HasWeapon()
	'''

	__slots__ = ['weapons', 'has_attacked', 'projectiles', 'weapon_in_use']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new HasWeapon component. 
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
				weapon_ent = engine.alias_to_entity.get(weapon_ent) if isinstance(weapon_ent, str) else weapon_ent

				# Translate entity id name to entity id number if needed
				generator_ent = w_value.get('generator')
				generator_ent = engine.alias_to_entity.get(generator_ent) if isinstance(generator_ent, str) else generator_ent

				# TODO - check that generator has factory component!!

				# Save the new values in weapons dictionary
				self.weapons.update({w_key : {"weapon" : weapon_ent, "generator" : generator_ent}})

			# Remember the projectiles - set of ints representing entities
			self.projectiles = set()

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

	def get_weapon_action_anim(self):
		''' Get the name of attack animation for the weapon that is currently 
		in possesion of the entity.
		'''
		# TODO - wouldnt it be easier to store action and idle action in weapons dictionary??
		return engine.world.component_for_entity(self.get_weapon_in_use(), Weapon).action
	
	def get_weapon_idle_anim(self):
		''' Get the name of idle animation for the weapon that is currently
		in possesion of the entity.
		'''
		return engine.world.component_for_entity(self.get_weapon_in_use(), Weapon).idle
	
	def remove_projectile(self, entity):
		''' Removes projectile from the list of projectiles
		that is implemented as a set.
		'''

		self.projectiles.remove(entity)
		print(f'Projectile {entity} deleted. List of projectiles {self.projectiles}')

	"""
	def create_projectile(self, owner_ent, pos_comp, coll_comp):
		''' Creates projectile - taking information from the generator of projectile - character entity position and collision
		closely coupled with GenerateProjectile processor
		'''
		
		# If no weapon ot generator do not create projectile
		try:
			# Get weapon component from the weapon
			weapon = engine.world.component_for_entity(self.get_weapon_in_use(), Weapon)
			factory = engine.world.component_for_entity(self.get_generator_in_use(), Factory)
		except KeyError:
			return None

		# Check if more projectiles can be created and continue, if yes
		if len(self.projectiles) < weapon.max_projectiles:
			
			# calculate position for the new projectile
			(ent_col_x, ent_col_y) = (coll_comp.x, coll_comp.y) if coll_comp else (0, 0)
			(pos_x, pos_y, pos_map) = (int(pos_comp.x + (pos_comp.direction[0] * (ent_col_x + 30))), int(pos_comp.y + (pos_comp.direction[1] * (ent_col_y + 30))), pos_comp.map)
			
			# Calculate collision zone for the new projectile - OBSOLETE - collision component is created by the factory
			#(col_x, col_y) = (weapon.projectile_collision_zones.get(pos_comp.dir_name)[0], weapon.projectile_collision_zones.get(pos_comp.dir_name)[1])

			# Create new entity for the new projectile - TODO the parameters of projectile need to be taken from the weapon
			#new_projectile = engine._create_entity(
			#	{
			#		"id" : "projectile_" + "owner_" + str(owner_ent),
			#		"components" : [
			#			{"type" : "Temporary", "params" : {"ttl" : 100}},
			#			{"type" : "Collidable", "params" : {"x" : col_x, "y" : col_y}},
			#			{"type" : "Position", "params" : {"x" : pos_x, "y" : pos_y, "map" : pos_map}},
			#			{"type" : "Damaging", "params" : {"damage" : 10}},
			#			{"type" : "Debug", "params" : {}},
			#			{"type" : "Container", "params" : {"contained_in" : self}} # reference to has_weapon instance
			#		]
			##	# Do not register in engine global variable alias_to_entity - not needed
			#	register=False)
			
			new_projectile = factory.create_entity(owner=owner_ent, pos=(pos_x, pos_y, pos_comp.dir_name, pos_map), container=self, reg_at_engine=False)

			# Increase count of active projectiles
			self.projectiles.add(new_projectile)
			print(f'Projectile {new_projectile} created. List of projectiles {self.projectiles}')
			
			return new_projectile
