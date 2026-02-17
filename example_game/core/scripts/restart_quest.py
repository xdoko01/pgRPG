"""
Can be run from the console by putting following command

XXXX
"""

from pgrpg.core import main

def initialize(register, module_name):
    """Script registers itself at ScriptManager"""
    # Mandatory line
    register(fnc=script_restart_quest, alias=module_name)
    # Optional names for the script
    register(fnc=script_restart_quest, alias="restart_quest")

def script_restart_quest(event, *args, **kwargs):
    """ Script that clears all scenes and loads new one again.
    """

    scene = kwargs.get("scene")

    main.engine.load_scene(scene_file=scene)

    return 0
