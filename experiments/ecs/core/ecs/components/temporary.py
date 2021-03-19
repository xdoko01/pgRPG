from .component import Component
import pygame

class Temporary(Component):
	''' Component that can be assigned to the entity that has
	limited timespan. After that entity disappears. For example, 
	projectile is temporary (arrow).
	'''

	__slots__ = ['ttl', 'creation_time']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the Temporary component.
		'''
		super().__init__()

		# How long the entity with this components should live
		# default is 5 seconds.
		self.ttl = kwargs.get("ttl", 5000)

		# When was the component created - in order to determine 
		# destruction time
		self.creation_time = pygame.time.get_ticks()
