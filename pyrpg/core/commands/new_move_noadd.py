''' Module implementing new_move_noadd command
'''

import pyrpg.core.engine as engine # To reference the world 
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)


def cmd_new_move_noadd(*args, **kwargs):
    ''' Move command that does not support adding moves to already existing
    moves.
    Typical example is pressing 'up' + 'left' at the same time which results
    in moving only to the left (the latter move) in case this command is used.
    '''

    # Get the entity
    entity = kwargs.get("entity")

    # Direction is a list of movements to process
    moves = kwargs.get("moves", [])


    # Always create NewFlagDoMove
    new_component = components.NewFlagDoMove(moves=moves)
    engine.world.add_component(entity, new_component)

    print(f'{__name__} - new component created {new_component}')

    return 0