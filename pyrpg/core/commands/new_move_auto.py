''' Module implementing new_move_auto command
'''

import pyrpg.core.engine as engine # To reference the world 
from pyrpg.core.ecs.components.new.position import Position # To work with components in commands (remove search add ...)
from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove # To work with components in commands (remove search add ...)

import pygame.time

def cmd_new_move_auto(*args, **kwargs):
    ''' Move in the current direction of the entity. Can be used for 
    movements of projectiles.
    '''

    # Get the entity
    entity = kwargs.get("entity")
    
    # Get the duration for auto movement in ms
    duration = kwargs.get("duration", 0)

    # Get the brain instance to measure time
    brain = kwargs.get("brain", None)

    current_time = pygame.time.get_ticks()

    if current_time - brain.cmd_first_call_time >= duration:
        # Movement is long enough - continue without exception
        return 0
    else:
        # Get the direction from position of the entity
        position = engine.world.try_component(entity, Position)

        # Create new FlagDoMove component
        new_component = FlagDoMove(moves=[position.dir_name])
        engine.world.add_component(entity, new_component)

        # There is still some time to move - return exception
        return -1
