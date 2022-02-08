import pygame
import pygame_gui

pygame.init()

pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((800, 600))

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#000000'))

is_running = True
clock = pygame.time.Clock()

manager = pygame_gui.UIManager((800, 600), 'experiments/gui/theme.json')

options_window = pygame_gui.elements.UIWindow(rect=pygame.Rect((10,10), (500,500)), manager=manager)

hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text='Say Hello', manager=manager, container=options_window)

select_file_window = pygame_gui.windows.UIFileDialog(
	rect=pygame.Rect((10,10), (500,500)), 
	manager=manager, 
	window_title='File Dialog', 
	initial_file_path= None, 
	allow_existing_files_only=False,
	allow_picking_directories=False)

confirm_dialog = pygame_gui.windows.UIConfirmationDialog(rect=pygame.Rect((20,20), (200,100)), manager=manager, action_long_desc='Exit')

free_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text='Say Hello', manager=manager, container=None)

message_window = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((20,20), (200,100)), html_message = 'baf', manager=manager)
test_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 50)), text='Hello', manager=manager, container=message_window)


while is_running:
	dt = clock.tick(60)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			is_running = False
		
		if event.type == pygame_gui.UI_BUTTON_PRESSED:
			if event.ui_element == hello_button:
				print('Hello World!')
		if event.type == pygame_gui.UI_WINDOW_CLOSE:
			if event.ui_element == options_window:
				print('Bye World!')
		if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
			print(event.text)


		manager.process_events(event)

	manager.update(dt/1000) # in seconds

		
	window_surface.blit(background, (0, 0))
	manager.draw_ui(window_surface)


	pygame.display.update()