import pgrpg.core.main as main

from pgrpg.core.config import FILEPATHS

def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_play_music, alias=module_name)
    # Optional names for the script
    register(fnc=script_play_music, alias='play_music')

def script_play_music(event, *args, **kwargs):
    ''' Script that starts playing a music
    '''

    music_file = kwargs.get('music_file')
    volume = kwargs.get('volume')


    main.engine.sound_manager.play_music(FILEPATHS["MUSIC_PATH"] / music_file, volume if volume else 1.0)
    

    # Return success
    return 0
