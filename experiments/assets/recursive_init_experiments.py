import json

class TileModel:

	def __init__(self, path, model):

		self.name = None
		self.id = None
		self.path = None
		self.collision = []
		self.text= None

		self._load_model(path, model)

	def _load_model(self, path, model, child_ref=None):

		try:
			with open(path + model + '.json', 'r') as model_file:
				json_model_data = model_file.read()
		except FileNotFoundError:
			print(f"Model file {path + model + '.json'} not found.")
			raise

		model_data = json.loads(json_model_data)
			
		prototype = str(model_data.get('prototype',''))

		if prototype != '':
			# Create or read existing model, if already exists
			self._load_model(path, prototype, child_ref=self)

		# Store all the model data except textures and prototype		
		for meta_key, meta_value in model_data.items():
			if meta_key not in ['prototype']: setattr(child_ref if child_ref != None else self, meta_key, meta_value)

		# Print self
		print(self)


	def __str__(self):
		return f'\n*Instance ({hex(id(self))}) [{ctypes.c_long.from_address(id(self)).value}]:\t{self.__class__.__name__}\
            \n\tCol ({hex(id(self.collision))}) [{ctypes.c_long.from_address(id(self.collision)).value}]:\t{self.collision}\
			\n\tTex ({hex(id(self.text))}) [{ctypes.c_long.from_address(id(self.text)).value}]:\t{self.text}\
			\n\tId ({hex(id(self.id))}) [{ctypes.c_long.from_address(id(self.id)).value}]:\t{self.id}\
			\n\tPath ({hex(id(self.path))}) [{ctypes.c_long.from_address(id(self.path)).value}]:\t{self.path}\
			\n\tName ({hex(id(self.name))}) [{ctypes.c_long.from_address(id(self.name)).value}]:\t{self.name}'

a = TileModel('experiments/','model')
print(a)
print(gc.get_referrers(a))
print(sys.getrefcount(a))


