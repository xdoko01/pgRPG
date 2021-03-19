
class MapEntity:

	def __init__(self):

		self.map = None
		self.pos = '[0, 0]'

	def setup(self, params={}):

		self.map = params.get('map')
		self.pos = params.get('pos')

	def __str__(self):
		return f"MapEntity {self.map} , {self.pos}"


class Item(MapEntity):

	def __init__(self):

		super().__init__()

		self.action = None

	def setup(self, params={}):

		super().setup(params)		

		self.action = params.get('action')

	def __str__(self):
		return f"Item {self.map} , {self.pos} , {self.action}"


class Teleport(Item):

	def __init__(self):

		super().__init__()

		self.target_map = None
		self.target_pos = '[0, 0]'

	def setup(self, params={}):

		super().setup(params)		

		self.target_map = params.get('target_map')
		self.target_pos = params.get('target_pos')

	def __str__(self):
		return f"Teleport {self.map} , {self.pos} , {self.target_map} , {self.target_pos}"


class Character(MapEntity):

	def __init__(self):

		super().__init__()

		self.health = 100
		self.wearable = {}
		self.inventory = []

	def setup(self, params={}):

		super().setup(params)		

		self.health = params.get('health')
		self.wearable = params.get('wearable')
		self.inventory = params.get('inventory')

	def __str__(self):
		return f"Character {self.map} , {self.pos} , {self.health} , {self.wearable}, {self.inventory}"



# It is possible to have one setup function for all MapEntity objects and subordinate objects
dataTeleport = { 'map' : 'map01', 'pos' : '[1,1]', 'target_map' : 'map02', 'target_pos' : '[2,2]'}

t = Teleport()
i = Item()

entities = []

entities.append(t)
entities.append(i)


for ent in entities:
	ent.setup(dataTeleport)
	print(ent)

a = str(ent) + '.json'
print(a)