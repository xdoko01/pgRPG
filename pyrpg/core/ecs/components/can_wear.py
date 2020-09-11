from .component import Component
import pyrpg.core.engine as engine # For checking the engine.alias_to_entity - if component has entity as a str as a parameter (HasInventory) 

class CanWear(Component):
	''' Entity can pickup and wear Wearable entities

	Used by:
		-	CollisionWearableProcessor

	Tests:
		>>> c = CanWear()
	'''

	__slots__ = ['wearables']

	BODYPARTS = ['head', 'hands', 'feet', 'belt', 'legs', 'torso']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new CanWear component. 
		'''

		super().__init__()

		# Initiate the wardrobe
		self.wearables = {
			'head' : None,
			'hands' : None,
			'feet' : None,
			'belt' : None,
			'legs' : None,
			'torso' : None
		}

		# Try to wear the entity
		try:
			for w_key, w_value in kwargs.items():
				
				# Translate the value (Wearable) to Entity instance if necessary
				wearable_entity = engine.alias_to_entity.get(w_value) if isinstance(w_value, str) else w_value

				# If it is possible to wear the entity (known bodypart and empty slot for wearable) then wear it
				if w_key in CanWear.BODYPARTS and not self.wearables.get(w_key):
					self.wearables.update({w_key : wearable_entity})

		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Problem with wearing of the entity')
			raise ValueError
