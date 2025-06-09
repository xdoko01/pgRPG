'''
Can be run from the console by putting following command

XXXX
'''

import pyrpg.core.main as main

def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_exit, alias=module_name)
    # Optional names for the script
    register(fnc=script_exit, alias='exit')

def script_exit(event, *args, **kwargs):
    ''' Script that exits the game
    '''

    # Do not show progress information and do not clear anything
    main.end()

    # Return success
    return 0
