''' Script for setting value of comp parameter for given entity.

    Parameters passed from console:
        :param game_ctx: Reference to the console entry point to the game (main module). 
                         Depends on the console configuration.
        :type game_ctx: ref

        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "set_value -h"      ... get usage instructions
        "set_value --help"  ... get usage instructions
        "set_value 1 position:Position x=50 y=60" ... set new position parameters for entity 1 - x=50, y=60
        "set_value player01 position:Position x=50 y=60 -a" ... set new position parameters for entity player01 - x=50, y=60
'''

instructions = """
    Examples of usage:
        "set_value -h"      ... get usage instructions
        "set_value --help"  ... get usage instructions
        "set_value 1 position:Position x=50 y=60" ... set new position parameters for entity 1 - x=50, y=60
        "set_value player01 position:Position x=50 y=60 -a" ... set new position parameters for entity player01 - x=50, y=60
"""

def initialize(register, module_name):
    '''Script registers itself at Console'''
    # Mandatory line
    register(fnc=cons_cmd_set_value, alias=module_name)

def cons_cmd_set_value(game_ctx, params):
    ''' Script that sets value of the entity component.
    '''

    # Save all parameters passed from the Console in the list
    all_params = params.split()
    no_of_params = len(all_params) - 1 # exclude the script name

    # Show instructions if the last parametr indicates so
    if all_params[-1] in ('-h','--help', '?', 'help') or no_of_params == 0:
        print(instructions)

    # Set the component value
    else:

        # Get the last parameter - list details
        list_all_attrs = (all_params[-1] in ('-a', '--all'))

        # Get the entity if alias is present in the parameter (2nd param)
        try:
            ent = all_params[1]
        except IndexError:
            print(f'Missing mandatory parameter entity/alias.')
            raise ValueError()

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
                raise ValueError()

        # Translate entity to alias
        elif isinstance(ent, int):
            entity = ent
            alias = game_ctx.engine.ecs_manager.entity_to_alias.get(entity, None)
            if alias is None:
                print(f'Entity {entity} does not exist.')
                raise ValueError()
        else:
            print(f'Parameter "{ent}" does not represent any entity.')
            raise ValueError()

        # Get the particular component for the entity (3rd param)
        try:
            comp_str = all_params[2]
        except IndexError:
            print(f'Missing mandatory parameter component.')
            raise ValueError()

        # Convert component string to component class
        try:
            comp_class = game_ctx.engine.ecs_manager.get_comp_class_from_def(comp_str)
        except:
            print(f'String "{comp_str}" does not represent any component.')
            raise ValueError()

        # Get the component instance for the entity
        try:
            component = game_ctx.engine.ecs_manager.component_for_entity(entity, comp_class)
        except KeyError:
            print(f'Component "{comp_str}" does not exist for entity "{alias}"({entity}).')
            raise ValueError()

        # Loop through the variable expr in parameters and process them
        for expr in (all_params[3:-1] if list_all_attrs else all_params[3:]):

            # Assignment must contain left side=attr, equal sign, right side=value
            try:
                attr, value = expr.split('=')
            except ValueError:
                print(f'Incorect expression: {expr}. Skipping assignment.')
                raise ValueError()

            # Check if given component has the attribute
            try:
                comp_attr = getattr(component, attr)
            except:
                print(f'Problem obtaining attr "{attr}" from component "{comp_str}".')
                raise ValueError()

            # Process the right side of the expression so that int is not string but int etc.
            try:
                new_value = eval(value)
            except:
                print(f'Problem getting value "{value}" for attr "{attr}".')
                raise ValueError()

            # Finally, process the assignment
            try:
                setattr(component, attr, new_value)
                print(f'{comp_str}.{attr} set to value {value} successfully.')
            except:
                print(f'Problem while assigning value "{value}" to {comp_str}.{attr}.')
                continue

        if list_all_attrs:
            attrs = ''
            for slot in component.__slots__:
                attrs = f'{attrs} {slot}={getattr(component, slot)}'

            print(f'V: {attrs}')
