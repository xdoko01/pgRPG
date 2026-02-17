from pgrpg import main

def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=condition_entity_exists, alias=module_name)
    # Optional names for the script
    register(fnc=condition_entity_exists, alias='entity_exists')

def condition_entity_exists(event, *args, **kwargs):
    '''Test if the entity alias exists in the game.
    '''
    return kwargs.get("alias") in main.engine.ecs_manager.get_all_entities()