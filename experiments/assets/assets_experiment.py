import pygame
from mapentity import MapEntity
from assets import Assets

# Init pygame and prepare game window
pygame.init()
pygame.display.set_caption('test')
window = pygame.display.set_mode([640,480])

key1 = MapEntity('grey_key')
key2 = MapEntity('grey_key')
key3 = MapEntity('grey_key')

print(key1)
print(key2)
print(key3)

print(Assets._all_tile_models)

window.blit(key3.model.tex.get('default')[0].get('tile'), (0,0))
window.blit(key3.model.tex.get('default')[1].get('tile'), (64,0))
window.blit(key3.model.tex.get('default')[2].get('tile'), (128,0))

pygame.display.update()

'''
while True:
	keys = pygame.key.get_pressed()
	if keys[pygame.K_LEFT]:
		pygame.quit()
		sys.exit()
'''