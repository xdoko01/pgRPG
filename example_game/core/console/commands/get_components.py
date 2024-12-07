''' Script for listing of entities with given component(s) and component attributes.

    Parameters passed from console:
        :param game_ctx: Reference to the console entry point to the game (main module). 
                         Depends on the console configuration.
        :type game_ctx: ref

        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "get_components AmmoPack -a" ... get all entities having AmmoPack component and list comp attributes
        "get_components AmmoPack Position" ... get all components having AmmoPack and Position component and do not list comp attributes
'''

instructions = """
Examples of usage:
    "get_components -h"      ... get usage instructions
    "get_components --help"  ... get usage instructions
    "get_components AmmoPack -a" ... get all entities having AmmoPack component and list comp attributes
    "get_components AmmoPack Position" ... get all entities having AmmoPack and Position component and do not list comp attributes
"""

def initialize(register, module_name):
    '''Script registers itself at Console'''
    # Mandatory line
    register(fnc=cons_get_components, alias=module_name)

def cons_get_components(game_ctx, params):
    ''' Script that shows the components
    '''

    # Save all parameters passed from the Console in the list
    all_params = params.split()
    no_of_params = len(all_params) - 1 # exclude the script name

    # Show instructions if the last parametr indicates so
    if all_params[-1] in ('-h','--help', '?', 'help') or no_of_params == 0:
        print(instructions)

    # Show the components
    else:
        # Get the last parameter - list variables and values
        list_all_attrs = (all_params[-1] in ('-a', '--all'))

    # Get list of all components in parameters as a list
    components = list()

    # Loop the parameters (except the first/last - filename/toggle) - entity or alias name
    for comp_str in (all_params[1:-1] if list_all_attrs else all_params[1:]):

        # Convert component string to component class
        try:
            comp_class = getattr(game_ctx.components, comp_str)
            components.append(comp_class)
        except:
            print(f'String "{comp_str}" does not represent any component. Skipping.')
            continue

    # Print information abour entity, alias and component attributes with values
    for record in game_ctx.world.get_components(*components):

        entity = record[0]
        alias = game_ctx.entity_to_alias.get(entity)
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
