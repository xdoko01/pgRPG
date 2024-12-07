''' Script for listing of all components for given entities.

    Parameters passed from console:
        :param game_ctx: Reference to the console entry point to the game (main module). 
                         Depends on the console configuration.
        :type game_ctx: ref

        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "get_entities"         ... get usage instructions
        "get_entities -h"      ... get usage instructions
        "get_entities --help"  ... get usage instructions
        "get_entities 1 -a" ... get all components for entity 1 including list of attributes and values
        "get_entities 1 wooden_bow" ... get all components for entities 1 and wooden bow without attribute details
'''

instructions = """
Examples of usage:
    "get_entities 1 -a" ... get all components for entity 1 including list of attributes and values
    "get_entities 1 wooden_bow" ... get all components for entities 1 and wooden bow without attribute details
"""

def initialize(register, module_name):
    '''Script registers itself at Console'''
    # Mandatory line
    register(fnc=cons_cmd_get_entities, alias=module_name)

def cons_cmd_get_entities(game_ctx, params):
    ''' Script that shows entities in the game
    '''
    # Save all parameters passed from the Console in the list
    all_params = params.split()
    no_of_params = len(all_params) - 1 # exclude the script name

    # Show instructions if the last parametr indicates so
    if all_params[-1] in ('-h','--help', '?', 'help') or no_of_params == 0:
        print(instructions)

    # Show entites
    else:
        # Get the last parameter - list variables and values
        list_all_attrs = (all_params[-1] in ('-a','--all'))

        # Loop the parameters (except the first/last - filename/toggle) - entity or alias name
        for ent in (all_params[1:-1] if list_all_attrs else all_params[1:]):

            # Try to re-type the string parameter to int
            try:
                ent = int(ent)
            except ValueError:
                pass

            # Translate alias to entity id
            if isinstance(ent, str):
                alias = ent
                entity = game_ctx.engine.ecs_manager.get_entity_id(alias)
                if entity is None:
                    print(f'Alias "{alias}" does not represent any entity.')
                    continue
            # Translate entity to alias
            elif isinstance(ent, int):
                entity = ent
                alias = game_ctx.engine.ecs_manager.get_entity_alias(entity)
                if alias is None:
                    print(f'Entity {entity} does not exist.')
                    continue
            else:
                print(f'Parameter "{ent}" does not represent any entity.')
            
            # Print entity/alias details
            print(f'E: {entity} A: {alias}')

            # Print all components of entity/alias
            for component in game_ctx.engine.ecs_manager._world.components_for_entity(entity):
                print(f'C: {component}')

                if list_all_attrs:
                    attrs = ''
                    for slot in component.__slots__:
                        attrs = f'{attrs} {slot}={getattr(component, slot)}'

                    print(f'V: {attrs}')
