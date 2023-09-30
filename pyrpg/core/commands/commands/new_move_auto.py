''' Module implementing new_move_auto command
'''

from pyrpg.core.ecs.components.new.position import Position # To work with components in commands (remove search add ...)
from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove # To work with components in commands (remove search add ...)

import pygame.time

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_new_move_auto, alias=module_name)

def cmd_new_move_auto(*args, **kwargs):
    ''' Move in the current direction of the entity. Can be used for 
    movements of projectiles.
    '''

    # Get the world
    world = kwargs.get("world")

    # Get the entity
    entity = kwargs.get("entity")
    
    # Get the duration for auto movement in ms 
    duration = kwargs.get("duration", None)

    # Get the brain instance to measure time
    brain = kwargs.get("brain", None)

    current_time = pygame.time.get_ticks()

    # Continue movement if time is not yet up or no duration was specified or duration is None
    if (current_time - brain.cmd_first_call_time < duration) if duration is not None else (duration is None):

        # Get the direction from position of the entity
        position = world.try_component(entity, Position)

        # Create new FlagDoMove component
        new_component = FlagDoMove(moves=[position.dir_name])
        world.add_component(entity, new_component)

        # There is still some time to move - return exception
        return -1
    else:
        # Stop auto movement
        return 0

