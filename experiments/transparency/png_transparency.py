''' Experiments with set_colorkey method to define transparent parts of the picture
'''
import pygame


IMAGE_BLACK_PATH = "experiments/transparency/images/red_on_black.png"
IMAGE_WHITE_PATH = "experiments/transparency/images/red_on_white.png"

if __name__ == "__main__":
	
	# Initialize Display
	pygame.init()
	window = pygame.display.set_mode((640,480))
	pygame.display.set_caption("PNG transparency experiments")

	image_black = pygame.image.load(IMAGE_BLACK_PATH)
	image_black.convert()
	pygame.Surface.set_colorkey(image_black, pygame.Color(0,0,0))

	image_white = pygame.image.load(IMAGE_WHITE_PATH)
	image_white.convert()
	pygame.Surface.set_colorkey(image_white, pygame.Color(255,255,255))
	
	running = True
	while running:

		window.fill((128, 128, 128))
		window.blit(image_white, (0, 0))
		window.blit(image_black, (50, 50))

		# Read the keys pressed, mouse, win resize etc.
		key_events = pygame.event.get()

		# Check for End Game
		for event in key_events:
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False

		# Flip the framebuffers
		pygame.display.update()

	
	pygame.quit()