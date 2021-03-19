''' Input processor example
'''

# Example_method will not be part of the module nor package
__all__ = ['InputProcessor']

# This method will not be part of the processors package as it is not present in __all__
def example_method():
	print('Example method')

class InputProcessor:
	def __init__(self):
		print(f'Hello from {__name__}')