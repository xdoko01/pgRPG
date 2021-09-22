''' Module implementing attack command
'''

import pyrpg.core.engine as engine # To reference the world 
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)

def cmd_new_attack(*args, **kwargs):
    ''' Add NewFlagDoAttack to the entity
    '''

    # Get parameters for attack
    entity = kwargs.get("entity")

    engine.world.add_component(entity, components.NewFlagDoAttack())

    return 0
