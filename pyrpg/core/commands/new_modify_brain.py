''' Module implementing modify_brain command
'''

from pyrpg.core.ecs.components.new.brain import Brain

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_new_modify_brain, alias=module_name)

def cmd_new_modify_brain(*args, **kwargs):
    ''' Resets and Adds new commands to the entity's brain.
    '''

    # Get the world
    world = kwargs.get("world")

    # Get the entity
    entity = kwargs.get("entity")

   # Get the brain of the entity
    try:
        brain = world.component_for_entity(entity, Brain)

        # Stop the brain
        brain.enabled = False

        # Delete and reset the brain with the new commands
        brain.reset(kwargs.get("commands", []))

        # Everything worked fine
        return 0

    except KeyError:
        # Entity has no brain
        return -1

