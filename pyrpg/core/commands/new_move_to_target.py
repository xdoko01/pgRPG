''' Module implementing move_to_target command
'''
import pygame
from pyrpg.core.ecs.components.new.position import Position # To work with components in commands (remove search add ...)
from .new_move_add import cmd_new_move_add
import math # for calculation of square root move_to

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_new_move_to_target, alias=module_name)

def cmd_new_move_to_target(*args, **kwargs):
    ''' Move to the position of certain entity on the current map.
    Returns exception until the destination entity is reached. So it needs to be
    redirected to itself in order to repeat this command until destination is reached. 

    TODO - change direction not immediatelly but after some time or number of steps
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
    near_radius = kwargs.get("radius", 10)

    # How often to get updates about the target position
    update_time_ms = kwargs.get("update_time_ms", 1000)

    # Get the coordinate of the moving entity
    position = world.component_for_entity(entity, Position)

    # Get the actual position of the target - not always, we do not want to be mega precise
    # as it does not look good.
    # - if the unit is called for the first time
    # - every specific delay

    # When the unit is called for the first time, remember the target position and the time
    # when we obtained the position and store it into the brain.
    if brain.cmd_first_call:
        target = world.component_for_entity(target_ent, Position)
        brain.var_1, brain.var_2 = target.x, target.y
        brain.var_3 = brain.cmd_first_call_time 

        # Decide on which axis we will be closing the gap
        # Bigger gap on X-axis
        if abs(brain.var_1 - position.x) > abs(brain.var_2 - position.y):
            brain.var_4 = 'X'
        else:
            brain.var_4 = 'Y'

    # Update the target position after specific amount of time
    current_time = pygame.time.get_ticks()

    if current_time - brain.var_3 >= update_time_ms:
        target = world.component_for_entity(target_ent, Position)
        brain.var_1, brain.var_2 = target.x, target.y
        brain.var_3 = current_time 

        # Decide on which axis we will be closing the gap
        # Bigger gap on X-axis
        if abs(brain.var_1 - position.x) > abs(brain.var_2 - position.y):
            brain.var_4 = 'X'
        else:
            brain.var_4 = 'Y'


    # If the distance is close, end
    if math.sqrt( (brain.var_1 - position.x)**2 + (brain.var_2 - position.y)**2 ) < near_radius:
        return 0

    else:
        # If gap is big, continue
        if brain.var_4 == 'X':
            cmd_new_move_add(world=world, entity=entity, moves=['left' if brain.var_1 - position.x < 0 else 'right' if brain.var_1 - position.x > 0 else None])
        else:
            cmd_new_move_add(world=world, entity=entity, moves=['up' if brain.var_2 - position.y < 0 else 'down' if brain.var_2 - position.y > 0 else None])

    return -1

    """
    else:
        # Create movement so to minimise the distance between entity and the target
        if abs(brain.var_1 - position.x) > abs(brain.var_2 - position.y):
            # Close on x-axis
            cmd_new_move_add(world=world, entity=entity, moves=['left' if brain.var_1 - position.x < 0 else 'right' if brain.var_1 - position.x > 0 else None])
        else:
            # Close on y-axis
            cmd_new_move_add(world=world, entity=entity, moves=['up' if brain.var_2 - position.y < 0 else 'down' if brain.var_2 - position.y > 0 else None])

        return -1
    """