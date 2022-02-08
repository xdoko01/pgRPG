import pygame
from pathlib import Path

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


def load_animation(background_folder_path: Path, filetype_mask: str = '**/*.gif', resize: tuple=None) -> list:
	''' Load all pictures from folder, resize them and
	store them in the list for further use.

	Parameters:
		:param background_folder_path: Path to the folder containing images from which the animation should be created.
		:type background_folder_path: Path

		:param filetype_mask: Wildcard used for selection of files from which the animation should be created.
		:type filetype_mask: str

		:param resize: New width and height for images to be resized.
		:type resize: tuple

		:return: list of images
	'''

	list_of_images = []

	# check that the path is valid
	if not Path(background_folder_path).exists(): 
		raise ValueError(f'Path {background_folder_path} does not exist.')

	# get the folder path and list of all files in the folder
	pathlist = Path(background_folder_path).glob(filetype_mask)

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
