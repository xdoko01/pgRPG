''' Module implementing attack command
'''

import pyrpg.core.engine as engine # To reference the world 
from pyrpg.core.ecs.components.new_flag_do_attack import NewFlagDoAttack # To work with components in commands (remove search add ...)

def cmd_new_attack(*args, **kwargs):
    ''' Add NewFlagDoAttack to the entity
    '''

    # Get parameters for attack
    entity = kwargs.get("entity")

    engine.world.add_component(entity, NewFlagDoAttack())

    return 0
