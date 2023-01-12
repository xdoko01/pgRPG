''' Module implementing move_to_target_range command
'''
import pygame
from pyrpg.core.ecs.components.new.position import Position # To work with components in commands (remove search add ...)
from .new_move_add import cmd_new_move_add
import math # for calculation of square root move_to


def cmd_new_move_to_target_range(*args, **kwargs):
    ''' Move to the position where the enemy entity is in the range of the projectile
    Returns exception until such position is reached. So it needs to be
    redirected to itself in order to repeat this command until destination is reached. 
    '''

    # Brain reference
    brain = kwargs.get("brain", None)

    # World reference
    world = kwargs.get("world")

    # Who (entity) needs to move
    entity = kwargs.get("entity")

    # Who (entity) needs to be reached target coordinates
    target_ent = kwargs.get("target")

    # How close to get to the target
    range = kwargs.get("range", 500)

    # How often to get updates about the enemy position
    update_time_ms = kwargs.get("update_time_ms", 1000)


    # Get the actual position of the target - not always, we do not want to be mega precise
    # as it does not look good.
    # - if the unit is called for the first time
    # - every specific delay

    # When the unit is called for the first time, remember the entity and enemy position components, 
    # and the time when we obtained the position and store it into the brain.
    if brain.cmd_first_call:
        # Get the coordinate of the moving entity
        brain.var_4 = world.component_for_entity(entity, Position)
        brain.var_5 = world.component_for_entity(target_ent, Position)
        brain.var_3 = brain.cmd_first_call_time 

    # Update the target position after specific amount of time
    current_time = pygame.time.get_ticks()

    if current_time - brain.var_3 >= update_time_ms:
        brain.var_3 = current_time 

        # Decide on which axis we will be closing the gap - close the smaller gap in order
        # to be able to shoot quicker.
        # Bigger gap on X-axis
        if abs(brain.var_5.x - brain.var_4.x) > abs(brain.var_5.y - brain.var_4.y):
            brain.var_1 = 'Y'
        else:
            brain.var_1 = 'X'


    # If the distance is closed, end
    if abs(brain.var_5.y - brain.var_4.y) < 10 and abs(brain.var_5.x - brain.var_4.x) < range:
        if brain.var_5.x < brain.var_4.x:
            brain.var_4.set_direction('left')
        else:
            brain.var_4.set_direction('right')
        return 0

    if abs(brain.var_5.x - brain.var_4.x) < 10 and abs(brain.var_5.y - brain.var_4.y) < range:
        if brain.var_5.y < brain.var_4.y:
            brain.var_4.set_direction('up')
        else:
            brain.var_4.set_direction('down')
        return 0

    else:
        # If gap is big, continue
        if brain.var_4 == 'X':
            cmd_new_move_add(world=world, entity=entity, moves=['left' if brain.var_5.x - brain.var_4.x < 0 else 'right' if brain.var_5.x - brain.var_4.x > 0 else None])
        else:
            cmd_new_move_add(world=world, entity=entity, moves=['up' if brain.var_5.y - brain.var_4.y < 0 else 'down' if brain.var_5.y - brain.var_4.y > 0 else None])

    return -1
