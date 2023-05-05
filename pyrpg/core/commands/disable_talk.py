''' Module implementing disable_talk command
'''

import backup.core.engine as engine # To reference the world 
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_disable_talk, alias=module_name)

def cmd_disable_talk(*args, **kwargs):
    ''' Finish speaking when global brain wants to run cinematics
    '''

    # Get entity to stop speaking
    talk_ent = kwargs.get("entity", None)

    # Get CanTalk component for the entity
    try:
        can_talk = engine.world.component_for_entity(talk_ent, components.CanTalk)

        # Set text to empty string
        can_talk.text = ''

        # Successful finished
        return 0

    except KeyError:

        # Entity does not have component CanTalk
        return -1
