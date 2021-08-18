''' Module implementing new_move_auto command
'''

import pyrpg.core.engine as engine # To reference the world 
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)


def cmd_new_move_auto(*args, **kwargs):
    ''' Move in the current direction of the entity. Can be used for 
    movements of projectiles.
    '''

    # Get the entity
    entity = kwargs.get("entity")

    # Get the direction from position of the entity
    position = engine.world.try_component(entity, components.Position)

    # Create new NewFlagDoMove component
    new_component = components.NewFlagDoMove(moves=[position.dir_name])

    engine.world.add_component(entity, new_component)
    print(f'{__name__} - new component created {new_component}')

    return 0
