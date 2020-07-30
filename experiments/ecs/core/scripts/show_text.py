import core.engine as engine
import core.ecs.processors as processors
import functions as func

import pygame
from pygame.locals import *  # used for wait(function)

def script_show_text(event, *args, **kwargs):
    ''' Show text pane over the whole game window
    and wait for the key press
    '''

    font = pygame.font.Font(None, 20)

    # Draw square on the screen
    #pygame.draw.rect(engine.window, (128, 128, 128, 128), pygame.Rect(10, 10, 600, 600), width=0, border_radius = 10)

    # Text is the list of texts that should be displayed
    texts = kwargs.get('texts', [])

    # Show the texts separatelly and wait for the key press between
    for text in texts:

        engine.world.get_processor(processors.UpdateCameraOffsetProcessor).process()
        engine.world.get_processor(processors.RenderMapProcessor).process()

        pygame.draw.rect(engine.window, (128, 128, 128, 0), pygame.Rect(10, 10, 600, 600))
        engine.window.blit(font.render(text, True, pygame.Color('white')), (20, 20) )

        # Blit the text on the screen
        #engine.window.blit()
        # Refresh the screen
        pygame.display.update()
        # Wait for the key pressed
        func.wait(pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE)

    # Return success
    return 0
