import pygame
from pygame.locals import *  # used for wait(function)

def wait(*continue_keys):
	''' Waits for one of the given keys to be pressed
	Enter in this case but can be enhanced to any key.
	'''

	pygame.event.clear()

	while True:
		event = pygame.event.wait()
		if event.type == QUIT:
			return
		elif event.type == KEYDOWN:
			if event.key in continue_keys:
				return
