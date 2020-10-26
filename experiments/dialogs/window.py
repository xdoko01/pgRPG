'''
    Module that implements window with different game information

      - every quest has defined its dialogs

    	"dialogs" : [
				{
					"id" : "welcome_dlg",
					"template" : "welcome.json",
                    "params" : {????},
					"data" : {
						"frames" : [
							{
								"dimensions" : [100, 100],
								"background_color" : "#FFFFFF",
								"background_alpha" : 128
							}
						]
					}
				}
			]

      - dialog is then used during quest phase
						"actions" : [
							["execute_script", {"script_body" : "print(f'QUEST HAS STARTED')"}],
							["show_dialog", {"dialog_id" : "welcome_dlg"}]



    Idea:
        - module reads json/dictionary and based on the details in json/dictionary
        - based on the specs, module displays the dialog window - generates pygame.Surface 
          ready to be blitted anywhere.
        - question is if the function should handle input as well - wait for enter to be pressed in order to display next frame ...
            - probably this is not good idea. For start, just display it and that is it
v            - target_surface is the surface on which we will blit the dialog window surface
            - dict with spec might be the dictionary containing specification how the window should look like
            - no_of_frame is optional and shows given frame from the dialog window specification
            - returns -1 if no frame is available

    Features that I need to implement:
        - bitmap fonts and frames

    {
	  frames : [
		  {
			  background_color:
			  background_transparency:
			  ttl: 300
			  texts: [
				  {
					  text : 'sdfsdf dsffsda asdfsdf'
					  position : [100, 100]
				  },
				  {
					  text : 'sdfsdf dsffsda asdfsdf'
					  position : [200, 200]
				  }
			  ],
			  pictures : [
				  {
					  picture : imaes/sdfsdf.png
					  position: [30,30]
				  },
				  {
					  picture : imaes/sdfsdf.png
					  position: [30,30]
				  }
			  ]
		  }
  }
'''
import json
import pygame
import utils

FONT_PATH = 'resources/fonts'

def get_dlg_frame(file, frame):
    ''' Returns pygame.Surface with the generated dialog frame
    '''

    try:
        with open(file, 'r') as dlg_file:
            json_dlg_data = dlg_file.read()
            dlg_data = json.loads(json_dlg_data)
    except FileNotFoundError:
        print(f"Dialog file '{file}' not found.")
        raise

    # Get frame data
    frame_data = dlg_data.get('frames')[frame]

    # Prepare the frame for displaying
    frame_surf = pygame.Surface(frame_data.get('dimensions'), )
    frame_surf.fill(pygame.Color(frame_data.get('background_color')))
    frame_surf.set_alpha(frame_data.get('background_alpha'))

    # Prepare the text if it is defined for the frame
    for text_data in frame_data.get('texts',[]):
        text = text_data.get('text', '')
        font = text_data.get('font_path', frame_data.get('font_path', dlg_data.get('font_path')))
        size = text_data.get('font_size', frame_data.get('font_size', dlg_data.get('font_size', None)))
        color = text_data.get('font_color', frame_data.get('font_color', dlg_data.get('font_color', None)))
        color = pygame.Color(color) if color else None
        align = text_data.get('font_align', frame_data.get('font_align', dlg_data.get('font_align', None)))
        position = text_data.get('position', [0, 0])

        # Prepare font object
        text_font = utils.BitmapFont(font, size=size, color=color)

        # Render the font surface + paste the text on frame position
        frame_surf.blit(text_font.render(text, color=color, align=align), position)

    return frame_surf

def display_dlg_frame(target, position, file, frame):
    ''' Display the dialog frame on a target on a position
    '''

    try:
        with open(file, 'r') as dlg_file:
            json_dlg_data = dlg_file.read()
            dlg_data = json.loads(json_dlg_data)
    except FileNotFoundError:
        print(f"Dialog file '{file}' not found.")
        raise

    # Get frame data
    frame_data = dlg_data.get('frames')[frame]

    # Prepare the frame for displaying
    frame_surf = pygame.Surface(frame_data.get('dimensions'), )
    frame_surf.fill(pygame.Color(frame_data.get('background_color')))
    frame_surf.set_alpha(frame_data.get('background_alpha'))

    # Blit the result to the target surface
    target.blit(frame_surf, (position[0], position[1]))


if __name__ == "__main__":

    ##############
    # INIT PYGAME
    ##############

    # Init pygame
    pygame.init()

    # Prepare the main window
    window = pygame.display.set_mode([850, 850], 0, 32)
    window.fill((50, 0, 0))

    ##############
    # PREPARE DIALOGS
    ##############

    # Display the frame on given position
    display_dlg_frame(target=window, position=(100, 100), file='experiments/dialogs/example.json', frame=0)

    # Alternativelly, display it manually
    window.blit(get_dlg_frame(file='experiments/dialogs/example.json', frame=0), (200, 200))

    ##############
    # DISPLAY THE DIALOGS
    ##############

    # Show the result
    pygame.display.update()

    # Quit - wait for closing of the window
    pygame.event.clear()

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
