import pygame
import os
from pathlib import Path

pygame.init()

pygame.display.set_caption('Animated Background')
window_surface = pygame.display.set_mode((800, 450))

background = pygame.Surface((800, 450))
background.fill(pygame.Color('#000000'))


def load_image(image_folder_path: Path, resize: tuple=None) -> pygame.image:
	''' load and resize image from the given path
	'''
	try:
		image = pygame.image.load(str(image_folder_path))
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

images = load_animation(Path('pyrpg/resources/images/background/'), (800, 450))


while True:

	for image in images:
		window_surface.blit(image, (0, 0))
		pygame.display.update()
		pygame.time.wait(130)
