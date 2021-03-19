import pygame
import pygame_gui

pygame.init()

pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((800, 600))

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#000000'))

is_running = True
clock = pygame.time.Clock()

manager = pygame_gui.UIManager((800, 600))

options_window = pygame_gui.elements.UIWindow(rect=pygame.Rect((10,10), (500,500)), manager=manager)

hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text='Say Hello', manager=manager, container=options_window)


while is_running:
	dt = clock.tick(60)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			is_running = False
		
		if event.type == pygame.USEREVENT:
			if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
				if event.ui_element == hello_button:
					print('Hello World!')
			if event.user_type == pygame_gui.UI_WINDOW_CLOSE:
				if event.ui_element == options_window:
					print('Bye World!')

		manager.process_events(event)

	manager.update(dt/1000) # in seconds

		
	window_surface.blit(background, (0, 0))
	manager.draw_ui(window_surface)


	pygame.display.update()