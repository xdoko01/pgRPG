''' Module implementing wait_key command
'''

import pygame

def cmd_wait_key(*args, **kwargs):
    ''' Wait until key specified in parameter is pressed. Then continue.
    '''

    continue_key = kwargs.get("key", None)

    # Get the pressed key from global - CommandProcessor
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        return 0
    else:
        return -1
