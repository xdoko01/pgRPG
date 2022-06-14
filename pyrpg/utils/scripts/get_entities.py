''' Script for listing of all components for given entities.

    Parameters passed from console:
        :params: The whole command passed from console containing the script name and parameters

    Examples:
        "py_script get_entities 1 -a"
            ... get all components for entity 1 including list of attributes and values

        "py_script get_entities 1 wooden_bow"
            ... get all components for entities 1 and wooden bow without attribute details
'''
# Save all parameters passed from the Console in the list
all_params = params.split()

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
        entity = game.main.engine.ecs_manager.get_entity_id(alias)
        if entity is None:
            print(f'Alias "{alias}" does not represent any entity.')
            continue
    # Translate entity to alias
    elif isinstance(ent, int):
        entity = ent
        alias = game.main.engine.ecs_manager.get_entity_alias(entity)
        if alias is None:
            print(f'Entity {entity} does not exist.')
            continue
    else:
        print(f'Parameter "{ent}" does not represent any entity.')
    
    # Print entity/alias details
    print(f'E: {entity} A: {alias}')

    # Print all components of entity/alias
    for component in game.main.engine.ecs_manager.get_game_world().components_for_entity(entity):
        print(f'C: {component}')

        if list_all_attrs:
            attrs = ''
            for slot in component.__slots__:
                attrs = f'{attrs} {slot}={getattr(component, slot)}'

            print(f'V: {attrs}')
