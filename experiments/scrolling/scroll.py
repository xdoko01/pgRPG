''' Proof of concept for implementation of scrolling using a camera
'''
import pygame

class Player:
	''' Sample player class storing players possition and image (Surface)
	'''
	def __init__(self, x, y):
		self.image = pygame.image.load("experiments/scrolling/images/player1.png")
		self.x = x
		self.y = y

class Map:
	''' Sample map class storing map data about tiles
	'''
	def __init__(self):
		''' Map consists of layers and tileset
		'''
		self.ground_layer = [
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		]

		self.wall_layer = [
			[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,2,2,0,2,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,2,2,2,2,0,0,0,0,0,2,0,2,2,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
			[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		]

		ground_tile = pygame.image.load("experiments/scrolling/images/ground_tile.png")
		wall_tile = pygame.image.load("experiments/scrolling/images/wall_tile.png")

		self.tilewidth = len(self.ground_layer[0])
		self.tileheight = len(self.ground_layer)

		self.width = self.tilewidth * 64
		self.height = self.tileheight * 64

		self.tileset = {
			1 : ground_tile,
			2 : wall_tile
		}

	def get_tile(self, layer, map_x, map_y) -> pygame.Surface:
		''' Return the Surface of the particular tile
		'''

		if layer == 'ground':
			return self.tileset.get(self.ground_layer[map_y][map_x])
		
		elif layer == 'wall':
			return self.tileset.get(self.wall_layer[map_y][map_x])


class Camera:

	def __init__(self, width, height):
		# Here we track the offset
		#self.camera = pygame.Rect(offset_x, offset_y, width, height)
		
		self.offset_x = 0
		self.offset_y = 0
		self.width = width
		self.height = height
		#
		self.screen = pygame.Surface((width, height))

	def apply(self, pos=(0,0)):
		''' Applying camera offset to some position object
		returns new position
		'''
		# Move the sprite of the entity - returns new shifted rectangle
		# return entity.move(self.camera.topleft)
		return (pos[0] + self.offset_x, pos[1] + self.offset_y)

	def update(self, target):
		'''  Updates camera offset based on position of the target.
		Target is object that the camera follows. Target must have
		pixel coordinates stored in x,y properties.
		'''
		# Offset moves opposite direction than the object + we need to keep it in the centre of the screen
		x = -target.x + int(self.width / 2)
		y = -target.y + int(self.height / 2)
		
		# print(f'Camera - unchanged [{x}, {y}], adjusted [{min(0, x)}, {min(0, y)}]')
		# Correction - do not centre at the edge of the map
		x = min(0, x)
		y = min(0, y)

		# Map dimensions 1920x1920
		x = max(-(1920 - self.width), x)
		y = max(-(1920 - self.height), y)
		
		# Update the offset
		self.offset_x, self.offset_y = x, y


def draw_map(map, screen):
	''' Draw map is using camera to draw the map
	'''

	for i in range(len(map.ground_layer)): # Y axis	
		for j in range(len(map.ground_layer[0])): # X axis
			if map.ground_layer[i][j] != 0:
				screen.blit(map.get_tile('ground', j, i), camera.apply((j*64, i*64)))

	for i in range(len(map.wall_layer)): # Y axis	
		for j in range(len(map.wall_layer[0])): # X axis
			if map.wall_layer[i][j] != 0:
				screen.blit(map.get_tile('wall', j, i), camera.apply((j*64, i*64)))

def draw_player(screen):
	screen.blit(player.image, camera.apply((player.x, player.y)))

def run():
	# Initialize Pygame stuff
	pygame.init()
	window = pygame.display.set_mode((640,480))
	pygame.display.set_caption("Esper Pygame example")
	clock = pygame.time.Clock()
	pygame.key.set_repeat(1, 1)

	running = True
	while running:

		window.fill((0,0,0))

		# Read the keys pressed, mouse, win resize etc.
		key_events = pygame.event.get()

		# Check for End Game
		for event in key_events:
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
				elif event.key == pygame.K_UP:
					player.y -= 5
				elif event.key == pygame.K_DOWN:
					player.y += 5
				elif event.key == pygame.K_LEFT:
					player.x -= 5
				elif event.key == pygame.K_RIGHT:
					player.x += 5

		camera.update(player)

		draw_map(_maps.get('map01'), camera.screen)
		draw_player(camera.screen)

		window.blit(camera.screen, (10, 10))

		# Flip the framebuffers
		pygame.display.update()

		# Keep game at 30 FPS
		clock.tick(30)
	
	running = False

if __name__ == "__main__":
	
	_maps = {}
	
	sample_map = Map()	
	print(f'Map dimensions: [{sample_map.width}, {sample_map.height}]')
	
	_maps.update({'map01' : sample_map})
	
	player = Player(20,30)
	player.image.convert_alpha()

	camera = Camera(400,400)

	print(_maps.get('map01').get_tile('ground', 0, 0))
	print(_maps.get('map01').get_tile('ground', 0, 0).get_rect())
	
	run()
	pygame.quit()