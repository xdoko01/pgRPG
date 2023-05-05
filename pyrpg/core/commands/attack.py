''' Module implementing attack command
'''

import backup.core.engine as engine # To reference the world 
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_attack, alias=module_name)

def cmd_attack(*args, **kwargs):
    ''' Simply set HasWeapon.has_attacked flag to True
    '''

    # Get parameters for movement
    entity = kwargs.get("entity")

    # if HasWeapon component does not exist on entity then error is not raised
    try:
        # Get the HasWeapon component from the entity
        has_weapon = engine.world.try_component(entity, (components.HasWeapon))

        has_weapon.has_attacked = True

        return 0

    except (KeyError, AttributeError):
        return -1
