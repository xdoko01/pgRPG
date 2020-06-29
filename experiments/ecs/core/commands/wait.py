''' Module implementing wait command
'''

import pygame.time # pygame.ime

def cmd_wait(*args, **kwargs):
    ''' Wait command used for example to slow done the motion
    '''
    wait_time = kwargs.get("time", 0)
    brain = kwargs.get("brain", None)

    current_time = pygame.time.get_ticks()

    if current_time - brain.cmd_first_call_time >= wait_time:
        # Unit has waited long enough - continue without exception
        return 0
    else:
        # There is still some time to wait - return exception
        return -1
