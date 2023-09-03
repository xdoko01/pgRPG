''' Module implementing attack command
'''

from pyrpg.core.ecs.components.new.flag_do_attack import FlagDoAttack # To work with components in commands (remove search add ...)

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_new_attack, alias=module_name)

def cmd_new_attack(*args, **kwargs):
    ''' Add FlagDoAttack to the entity
    '''

    # Get the world
    world = kwargs.get("world")

    # Get parameters for attack
    entity = kwargs.get("entity")

    world.add_component(entity, FlagDoAttack())

    return 0
