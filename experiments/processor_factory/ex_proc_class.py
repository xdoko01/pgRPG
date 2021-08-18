class ExampleProcessor:

	def __init__(self, ex_fnc=None):

		self.ex_fnc = ex_fnc
	
	def process(self):

		# Execute function passed in the parameter
		self.ex_fnc()

