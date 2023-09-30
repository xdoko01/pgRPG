''' Module implementing new_move_noadd command
'''

import logging
#!import pyrpg.core.engine as engine # To reference the world 

from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove # To work with components in commands (remove search add ...)

# Init logger
logger = logging.getLogger(__name__)

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_new_move_noadd, alias=module_name)

def cmd_new_move_noadd(*args, **kwargs):
    ''' Move command that does not support adding moves to already existing
    moves.
    Typical example is pressing 'up' + 'left' at the same time which results
    in moving only to the left (the latter move) in case this command is used.
    '''

    # Get the world
    world = kwargs.get("world")

    # Get the entity
    entity = kwargs.get("entity")

    # Direction is a list of movements to process
    moves = kwargs.get("moves", [])


    # Always create FlagDoMove
    new_component = FlagDoMove(moves=moves)
    world.add_component(entity, new_component)

    logger.debug(f'{__name__} - new component created {new_component}')

    return 0