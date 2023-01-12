''' Module implementing guard command
'''
import pygame
from pyrpg.core.ecs.components.new.position import Position # To work with components in commands (remove search add ...)
import math # for calculation of square root move_to


def cmd_new_guard(*args, **kwargs):
    ''' Stay at the guarded position. Once enemy spotted, guard ends.
    '''

    # Brain reference
    brain = kwargs.get("brain", None)

    # World reference
    world = kwargs.get("world")

    # Who (entity) is guarding
    entity = kwargs.get("entity")

    # Who (entity) needs to be reached target coordinates
    enemy = kwargs.get("enemy")

    # How close to get to the enemy
    near_radius = kwargs.get("radius", 10)

    # How often to get updates of direction
    update_time_ms = kwargs.get("update_time_ms", 1000)

    # Once every specific time, change the direction and check if the enemy is in your direction
    if brain.cmd_first_call:
        brain.var_1 =['down', 'left', 'up', 'right']
        brain.var_2 = 0 #start with down direction
        brain.var_3 = brain.cmd_first_call_time 
        brain.var_4 = world.component_for_entity(entity, Position)
        brain.var_5 = world.component_for_entity(enemy, Position)

    # Update the target position after specific amount of time
    current_time = pygame.time.get_ticks()

    if current_time - brain.var_3 >= update_time_ms:
        brain.var_2 = (brain.var_2 + 1) % 4
        # Get the coordinate of the entity
        brain.var_4.set_direction(brain.var_1[brain.var_2])
        brain.var_3 = current_time


    # Check if enemy was spotted
    if math.sqrt( (brain.var_5.x - brain.var_4.x)**2 + (brain.var_5.y - brain.var_4.y)**2 ) < near_radius:
        if brain.var_4.y < brain.var_5.y and brain.var_4.dir_name == 'down':
            return 0
        if brain.var_4.y >= brain.var_5.y and brain.var_4.dir_name == 'up':
            return 0
        if brain.var_4.x > brain.var_5.x and brain.var_4.dir_name == 'left':
            return 0
        if brain.var_4.x <= brain.var_5.x and brain.var_4.dir_name == 'right':
            return 0

    return -1
