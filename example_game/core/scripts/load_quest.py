'''
Can be run from the console by putting following command

XXXX
'''

from pyrpg import main

def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_load_quest, alias=module_name)
    # Optional names for the script
    register(fnc=script_load_quest, alias='load_quest')

def script_load_quest(event, *args, **kwargs):
    ''' Script that loads aa new scene
    '''

    scene_file = kwargs.get('scene_file')

    # Do not show progress information and do not clear anything
    main.engine.new_game(filepath=scene_file, clear_before_load=False, show_progress=False)

    # Return success
    return 0
