''' Script for listing of entities with given component(s) and component attributes.

    Parameters passed from console:
        :params: The whole command passed from console containing the script name and parameters

    Examples:
        "py_script get_components AmmoPack -a"
            ... get all entities having AmmoPack component and list comp attributes

        "py_script get_components AmmoPack Position"
            ... get all components having AmmoPack and Position component and do not list comp attributes

'''
# Save all parameters passed from the Console in the list
all_params = params.split()

# Get the last parameter - list variables and values
list_all_attrs = (all_params[-1] in ('-a', '--all'))

# Get list of all components in parameters as a list
components = list()

# Loop the parameters (except the first/last - filename/toggle) - entity or alias name
for comp_str in (all_params[1:-1] if list_all_attrs else all_params[1:]):

    # Convert component string to component class
    try:
        comp_class = getattr(game.components, comp_str)
        components.append(comp_class)
    except:
        print(f'String "{comp_str}" does not represent any component. Skipping.')
        continue

# Print information abour entity, alias and component attributes with values
for record in game.world.get_components(*components):

    entity = record[0]
    alias = game.entity_to_alias.get(entity)
    comp_instances = record[1] # tuple

    # Print entity/alias details
    print(f'E: {entity} A: {alias}')

    # Print all components of entity/alias
    for component in comp_instances:
        print(f'C: {component}')

        if list_all_attrs:
            attrs = ''
            for slot in component.__slots__:
                attrs = f'{attrs} {slot}={getattr(component, slot)}'

            print(f'V: {attrs}')
