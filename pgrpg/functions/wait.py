"""Blocking key-wait utility for pygame."""

import pygame
from pygame.locals import *  # used for wait(function)

def wait(*continue_keys):
	"""Block until one of the specified keys is pressed.

	Clears the event queue, then waits for a KEYDOWN event matching
	one of the given key constants. Also returns on QUIT events.

	Args:
		*continue_keys: One or more pygame key constants that will
			end the wait when pressed.
	"""

	pygame.event.clear()

	while True:
		event = pygame.event.wait()
		if event.type == QUIT:
			return
		elif event.type == KEYDOWN:
			if event.key in continue_keys:
				return
