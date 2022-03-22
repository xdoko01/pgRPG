import pygame
import random

from pathlib import Path

pygame.init()

def load_image(image_folder_path: Path, resize: tuple=None) -> pygame.image:
	''' load and resize image from the given path
	'''
	try:
		image = pygame.image.load(str(image_folder_path))
		image.set_colorkey((0,0,0))
		image.set_alpha(100)
		if resize: image = pygame.transform.scale(image, resize)
		return image.convert()
	except AttributeError:
		print(f'Unexpected error while loading an image "{str(image_folder_path)}".')
		raise ValueError


def load_animation(background_folder_path: Path, resize: tuple=None) -> list:
	''' Load all pictures from folder, resize them and
	store them in the list for further use.

	:return: list of images
	'''

	list_of_images = []

	# get the folder path and list of all files in the folder
	pathlist = Path(background_folder_path).glob('**/*.gif')

	for path in pathlist:

		try:
			list_of_images.append(load_image(path, resize))
			#path_in_str = str(path)
			#print(path_in_str)
			#image = pygame.image.load(str(path))
			#if resize: image = pygame.transform.scale(image, resize)
			#image.convert()
			#list_of_images.append(image)
		except ValueError:
			print(f'Unexpected error while loading an animation from "{str(background_folder_path)}".')
			raise ValueError

	return list_of_images

pygame.display.set_caption('Rainy Overlay')
window_surface = pygame.display.set_mode((800, 450))

background = pygame.image.load('pyrpg/resources/images/quake.png').convert()
background = pygame.transform.scale(background, (800, 450))

flash = pygame.Surface((800, 450))
flash.fill(pygame.Color('#FFFFFF'))
flash.set_alpha(200)

images = load_animation(Path('pyrpg/resources/images/weather_effects/rainy/'), (800, 450))


while True:

	for image in images:

		window_surface.blit(background, (0, 0))

		# random flash
		if random.randrange(100) > 95:
			window_surface.blit(flash, (0, 0))

		# rain
		window_surface.blit(image, (0, 0))
		
		pygame.display.update()
		pygame.time.wait(50)

		# Trivial pygame stuff.
		if pygame.key.get_pressed()[pygame.K_ESCAPE]:
			quit()
		for ev in pygame.event.get():
			if ev.type == pygame.QUIT:
				quit()

def quit():
	pygame.quit()