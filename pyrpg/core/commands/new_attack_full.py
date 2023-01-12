''' Module implementing attack command
'''
import pygame
from pyrpg.core.ecs.components.new.flag_do_attack import FlagDoAttack # To work with components in commands (remove search add ...)

def cmd_new_attack_full(*args, **kwargs):
    ''' Add FlagDoAttack to the entity so long to fill the full attack animation cycle
    '''

	# Get the brain to access brain looper variables
    brain = kwargs.get("brain", None)

    # Get the world
    world = kwargs.get("world")

    # Get parameters for attack
    entity = kwargs.get("entity")

	# How many FlagDoAttack generate in a row
    attack_time_ms = kwargs.get("attack_time_ms", 500)

    current_time = pygame.time.get_ticks()

    if current_time - brain.cmd_first_call_time >= attack_time_ms:
        # Unit has been executed long enough - continue without exception
        return 0
    else:
        # There is still time to execute - return exception
        world.add_component(entity, FlagDoAttack())
        return -1
