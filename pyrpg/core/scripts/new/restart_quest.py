'''
Can be run from the console by putting following command

XXXX
'''

from pyrpg.main import main
from pathlib import Path

def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_restart_quest, alias=module_name)
    # Optional names for the script
    register(fnc=script_restart_quest, alias='restart_quest')

def script_restart_quest(event, *args, **kwargs):
    ''' Script that clears all quests and loads new one again.
    '''

    quest = kwargs.get('quest')

    main.engine.new_game(Path(quest))

    # Return success
    return 0
