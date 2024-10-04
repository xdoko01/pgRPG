
from .str_utils import parse_fnc_str, parse_fnc_list, get_args_kwargs_from_list, get_kw_from_str
from .translate import translate
from .get_dict import get_dict

from pathlib import Path

def get_dict_params(definition, storage: dict=None, dir: Path=Path('')) -> dict:
    '''Takes template name and parameters as one string (definition). Fills the parameters
    into the template and returns the resulting dictionary.
    
    Parameters:
        :param definition: Identifies template name/path 
        :type definition: str | list

        :param storage: Reference to the dictionary, where the template might
                                be stored. If not found there, function will continue to
                                look for the template in the json or yaml file stored
                                in the template_dir.
        :type storage: dict

        :param dir: Directory where to look for the template file
        :type dir: Path

        :returns: Dictionary with data substituted using parameters
    
    Examples:
        (definition)
            t_tile_pos(5, 5, test_arena_sand)
        (template)
            {
                "id": "t_tile_pos",
                "vars": ["$tileX", "$tileY", "$map"],
                "components": [
                    {"type" : "position:Position", "params" : {"tile_x" : "$tileX", "tile_y" : "$tileY", "map" : "$map"}}
                ]
            }

    Tests:

        >>> storage = { \
            "t_tile_pos": { \
                "id": "t_tile_pos", \
                "vars": ["$tileX=0", "$tileY=0", "$map"], \
                "components": [ \
                    {"type" : "position:Position", "params" : {"tile_x" : "$tileX", "tile_y" : "$tileY", "map" : "$map"}} \
                ] \
            } \
        }
        
        # Cases for template and parameters parsed as s string
        >>> print(get_dict_params(definition="t_tile_pos(5, 5, test_arena_sand)", storage=storage))
        {'id': 't_tile_pos', 'vars': ['$tileX=0', '$tileY=0', 'test_arena_sand'], 'components': [{'type': 'position:Position', 'params': {'tile_x': 5, 'tile_y': 5, 'map': 'test_arena_sand'}}]}

        >>> print(get_dict_params(definition="t_tile_pos(5, 5, $map=test_arena_sand)", storage=storage))
        {'id': 't_tile_pos', 'vars': ['$tileX=0', '$tileY=0', 'test_arena_sand'], 'components': [{'type': 'position:Position', 'params': {'tile_x': 5, 'tile_y': 5, 'map': 'test_arena_sand'}}]}

        >>> print(get_dict_params(definition="t_tile_pos(1, 2, 3, 4, 5, $map=test_arena_sand)", storage=storage))
        {'id': 't_tile_pos', 'vars': ['$tileX=0', '$tileY=0', 'test_arena_sand'], 'components': [{'type': 'position:Position', 'params': {'tile_x': 1, 'tile_y': 2, 'map': 'test_arena_sand'}}]}

        >>> print(get_dict_params(definition="t_tile_pos($tileX = 5, $tileY=2, 3, 4, 5, $map=test_arena_sand)", storage=storage))
        {'id': 't_tile_pos', 'vars': ['$tileX=0', '$tileY=0', 'test_arena_sand'], 'components': [{'type': 'position:Position', 'params': {'tile_x': 5, 'tile_y': 2, 'map': 'test_arena_sand'}}]}

        # Cases for template and parameters as a list
        >>> print(get_dict_params(definition=["t_tile_pos", [3,4,5], {"$tileX": 5, "$tileY": 2, "$map": "test_arena_sand"}], storage=storage))
        {'id': 't_tile_pos', 'vars': ['$tileX=0', '$tileY=0', 'test_arena_sand'], 'components': [{'type': 'position:Position', 'params': {'tile_x': 5, 'tile_y': 2, 'map': 'test_arena_sand'}}]}

        >>> print(get_dict_params(definition=["t_tile_pos", {"$tileX": 5, "$tileY": 2, "$map": "test_arena_sand"}], storage=storage))
        {'id': 't_tile_pos', 'vars': ['$tileX=0', '$tileY=0', 'test_arena_sand'], 'components': [{'type': 'position:Position', 'params': {'tile_x': 5, 'tile_y': 2, 'map': 'test_arena_sand'}}]}

        >>> print(get_dict_params(definition=["t_tile_pos", [5,2,"test_arena_sand"]], storage=storage))
        {'id': 't_tile_pos', 'vars': ['$tileX=0', '$tileY=0', 'test_arena_sand'], 'components': [{'type': 'position:Position', 'params': {'tile_x': 5, 'tile_y': 2, 'map': 'test_arena_sand'}}]}

        # Default parameters of the template are used
        >>> print(get_dict_params(definition=["t_tile_pos", {"$map": "test_arena_sand"}], storage=storage))
        {'id': 't_tile_pos', 'vars': ['$tileX=0', '$tileY=0', 'test_arena_sand'], 'components': [{'type': 'position:Position', 'params': {'tile_x': 0, 'tile_y': 0, 'map': 'test_arena_sand'}}]}

        >>> print(get_dict_params(definition="t_tile_pos(5, 2, 4, $map=test_arena_sand)", storage=storage))
        {'id': 't_tile_pos', 'vars': ['$tileX=0', '$tileY=0', 'test_arena_sand'], 'components': [{'type': 'position:Position', 'params': {'tile_x': 5, 'tile_y': 2, 'map': 'test_arena_sand'}}]}

    '''
    ###
    # Based on the type of definition, decide how to handle the parameters and the template
    # Either handle it as a string or as a list with template and parameters definition
    ###
    assert isinstance(definition, str) or isinstance(definition, list), f'Template call must be either string or list' 
    name, args, kwargs = parse_fnc_str(definition) if isinstance(definition, str) else parse_fnc_list(definition)

    raw_data = get_dict(dictpath=name, storage=storage, dir=dir)

    # Get the definition of args, kwargs from the template, empty list/dict if no variables are defined
    vars_all, vars_args, vars_kwargs = get_args_kwargs_from_list(for_parse=raw_data.get('vars', []))

    ###
    # Generate the translation dictionary
    ###

    # 1/ create dictionary based on kwargs in the vars of the template (default values) - will go first and can be overwritten by anything
    # 2/ create dictionary from regular positional arguments - take only so many args as it is stored in vars - will go second in priority
    d_from_args = dict(zip(vars_all, args[:len(vars_all)]))
    # 3/ create dictionary from kwargs passed to the template - will go third as the one with the highest priority

    d_trans = {**vars_kwargs, **d_from_args, **kwargs}

    # Fill the template with the variables
    translated_data = translate(
        d_trans, # Translation dictionary made from list of variables and their values
        raw_data
    )

    return translated_data

if __name__ == '__main__':
    import doctest
    doctest.testmod()
