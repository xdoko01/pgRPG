''' Module implementing new_move_vect_noadd command
'''
# Initiate logging
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_new_move_vect_noadd, alias=module_name)

def cmd_new_move_vect_noadd(*args, **kwargs):
    ''' Move command that does not support adding moves to already existing
    moves. Is defined by vector of movement.
    Typical example is pressing 'up' + 'left' at the same time which results
    in moving only to the left (the latter move) in case this command is used.
    '''

    # Get the world
    world = kwargs.get("world")

    # Get the entity
    entity = kwargs.get("entity")

    # Direction is a vector to process
    vector = kwargs.get("vector", [0, 0])

    # Always create FlagDoMove
    new_component = FlagDoMove(vector=vector)
    world.add_component(entity, new_component)
    logger.debug(f'{__name__} - new component created {new_component}')

    return 0