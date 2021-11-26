''' Module implementing new_move_add command
'''

import logging
import pyrpg.core.engine as engine # To reference the world 
from pyrpg.core.ecs.components.new_flag_do_move import NewFlagDoMove # To work with components in commands (remove search add ...)

# Init logger
logger = logging.getLogger(__name__)

def cmd_new_move_add(*args, **kwargs):
    ''' Move command that supports adding moves to already existing
    moves and hence constructs FlagDoMove entity from multiple commands.
    Typical example is pressing 'up' + 'left' at the same time which results
    in moving diagonaly in case this command is used.
    '''

    # Get the entity
    entity = kwargs.get("entity")

    # Direction is a list of movements to process
    moves = kwargs.get("moves", [])

    # if NewFlagDoMove does not exist, create it.
    # if it already exists, recalculate the move_vect on the entity
    try:
        # Get the NewFlagDoMove component from the entity
        flag_do_move = engine.world.component_for_entity(entity, NewFlagDoMove)

        logger.debug(f'Entity {entity} - already existing component {flag_do_move}.')

        # Add the movements to the NewFlafDoMove entity - for example if 'up' and 'left' are pressed
        # at the same time then 2 move commands will be sent and processed and we need to make sure 
        # that both are taken into account in calculation of the final move vector. Hence, we need 
        # to add to the already existing moves.
        flag_do_move.add_moves(moves)

        logger.debug(f'Entity {entity} - moves added to already existing component {flag_do_move}.')

        return 0

    except KeyError:
        # Create new NewFlagDoMove component
        new_component = NewFlagDoMove(moves=moves)
        engine.world.add_component(entity, new_component)
        logger.debug(f'Entity {entity} - new component created {new_component}.')

        return 0
