import pyrpg.core.engine as engine
import pyrpg.core.ecs.processors as processors
from pyrpg.functions import wait # import wait function

import pygame
from pyrpg.core.config.keys import K_SUBMIT

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

        engine.world.get_processor(processors.RenderBackgroundProcessor).process()
        engine.world.get_processor(processors.RenderCameraBackgroundProcessor).process()
        engine.world.get_processor(processors.UpdateCameraOffsetProcessor).process()
        engine.world.get_processor(processors.RenderMapProcessor).process()

        # Draw game window surface
        s = pygame.Surface((600, 600))   # per-pixel alpha
        s.set_alpha(128)
        s.fill((128, 128, 128))
        engine.window.blit(s, (10, 10))

        # Draw game window text
        engine.window.blit(font.render(text, True, pygame.Color('white')), (20, 20) )

        # Blit the text on the screen
        #engine.window.blit()
        # Refresh the screen
        pygame.display.update()
        # Wait for the key pressed
        wait(K_SUBMIT, pygame.K_ESCAPE)

    # Return success
    return 0
