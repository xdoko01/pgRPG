from .component import Component

class Container(Component):
	''' Component containing back reference to the
	master component.
	'''

	__slots__ = ['contained_in']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the Container component.
		'''
		super().__init__()

		self.contained_in = kwargs.get("contained_in", None)
