from .component import Component

class Wearable(Component):
	''' Entity is wearable by other entity that has CanWear component

	Used by:
		-	CollisionWearableProcessor

	Tests:
		>>> c = Wearable()
	'''

	__slots__ = ['bodypart']

	BODYPARTS = ['head', 'hands', 'feet', 'belt', 'legs', 'torso']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Wearable component. Component has
		one arguments describing on which part of body the entity should be weared.
		'''

		super().__init__()

		# Read the bodypart
		try:
			self.bodypart = kwargs.get('bodypart')
		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Mandatory parameters are missing.')
			raise ValueError

		# Assert that bodypart exists in list of BODYPARTS
		try:
			assert isinstance(self.bodypart, str) and self.bodypart in Wearable.BODYPARTS, f'Unknown bodypart "{self.bodypart}" for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError
