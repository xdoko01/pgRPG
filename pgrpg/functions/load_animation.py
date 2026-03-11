"""Load and prepare sprite images and animations from disk."""

import pygame
from pathlib import Path

def load_image(image_folder_path: Path, resize: tuple=None) -> pygame.image:
	"""Load a single image and optionally resize it.

	Args:
		image_folder_path: Path to the image file.
		resize: Target ``(width, height)`` to scale the image to.
			None keeps the original size.

	Returns:
		The loaded (and optionally resized) pygame Surface.

	Raises:
		ValueError: If the image cannot be loaded.
	"""
	try:
		image = pygame.image.load(str(image_folder_path)).convert()
		if resize: image = pygame.transform.scale(image, resize)
		return image
	except AttributeError:
		print(f'Unexpected error while loading an image "{str(image_folder_path)}".')
		raise ValueError


def load_animation(background_folder_path: Path, filetype_mask: str = '**/*.gif', resize: tuple=None) -> list:
	"""Load all images from a folder as animation frames.

	Args:
		background_folder_path: Path to the folder containing the
			animation frame images.
		filetype_mask: Glob pattern for selecting image files.
		resize: Target ``(width, height)`` to scale each frame to.
			None keeps the original size.

	Returns:
		List of pygame Surfaces, one per animation frame.

	Raises:
		ValueError: If the folder does not exist or an image fails
			to load.
	"""

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
