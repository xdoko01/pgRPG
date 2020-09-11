from .component import Component
from .position import Position
from .container import Container

import pyrpg.core.engine as engine # For checking the engine.alias_to_entity - if component has entity as a str as a parameter (HasInventory)


class Factory(Component):
	'''
	- Factory component
		- prescription for the new entity
		- muze si pamatovat kolik muze vygenerovat entit
		- position of the new component??? doda funkce create entity HasWeapon
		- reference to projectile container??? doda funkce create entity HasWeapon
		- factory component by mohla mit metodu generate
		- vstupem pro uspesne vygenerovani musi byt pozice (volitelna) a kontainer(volitelny)

	{"type" : "Factory", "params" : {"prescription" : "arrow.json", "units" : 5}},

	'''

	__slots__ = ['prescription', 'units']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the Factory component.
		'''
		super().__init__()

		# Either define prescription as a json text or as a json entity file
		self.prescription = kwargs.get('prescription')
		
		# Unlimited number of units in case no units passed in the argument
		self.units = kwargs.get('units', None) 
	
		try:
			assert isinstance(self.prescription, dict), f'Prescription must be in a form of dictionary'
			assert isinstance(self.units, int) or self.units == None, f'Units must be integer or None(unlimited)'
		except AssertionError:
			raise ValueError

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
