import sys 				# for getting size of instance object and sys path

class Component(object):
	''' Parent class for all components. Inheritance from object is a must
	because __slots__ are used in inherited component classes.
	'''

	def __init__(self): 
		pass

	def __str__(self):
		''' Print representation of the component instance
		'''
		return f"Component '{self.__class__.__name__}' at {hex(id(self))} ({sys.getsizeof(self)}): {self.__dict__}"

	def pre_save(self):
		''' Prepare component for saving - remove all references to
		non-serializable objects.
		'''
		pass

	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		pass
