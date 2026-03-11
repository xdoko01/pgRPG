"""Dictionary and collection manipulation utilities.

Provides functions for creating, searching, modifying, and merging
nested dictionaries and collections used throughout the engine.

Run ``python -m pgrpg.functions.dict_utils -v`` for doctests.
"""

def _create_dict_list(path: list, value) -> dict:
    """Create a nested dictionary from a list of keys.

    The value is placed at the innermost key.

    Args:
        path: List of nested keys to create in the dictionary.
        value: Value to assign to the deepest key.

    Returns:
        A nested dictionary following the key path.

    Examples:
        >>> print(_create_dict_list(['a', 'b', 'c'], "hello"))
        {'a': {'b': {'c': 'hello'}}}
    """

    new_dict = {path[-1]: value}

    for p in reversed(path[:-1]):
        new_dict = {p: new_dict}

    return new_dict

def _create_dict_str(path: str, value, sep: str='.') -> None:
    """Create a nested dictionary from a dot-separated path string.

    Args:
        path: Dot-separated (or custom separator) string of nested keys.
        value: Value to assign to the deepest key.
        sep: Separator used between keys in the path string.

    Returns:
        A nested dictionary following the key path.

    Examples:
        >>> print(_create_dict_str('a.b.c', 'hello'))
        {'a': {'b': {'c': 'hello'}}}

        >>> print(_create_dict_str('a/b/c', 'hello', sep='/'))
        {'a': {'b': {'c': 'hello'}}}
    """

    return _create_dict_list(path.split(sep), value)

def get_dict_keys_having_value(d: dict, value, sep: str|None=None) -> list:
    """Find all key paths in a dictionary that contain a given value.

    Args:
        d: Dictionary to search.
        value: Value to search for.
        sep: If provided, join key paths into strings using this
            separator. Otherwise return paths as lists of keys.

    Returns:
        List of key paths where the value was found.

    Examples:
        >>> d = {"items": {\
                    "weapons": {"sword": {"weapon": [2, 3]}},\
                    "coins": {"golden" : [10,22,33], "copper": [1,2,3]}\
                }\
            }
        >>> res = get_dict_keys_having_value(d, 3)
        >>> print(res)
        [['items', 'weapons', 'sword', 'weapon'], ['items', 'coins', 'copper']]

        >>> res = get_dict_keys_having_value(d, 3, sep='.')
        >>> print(res)
        ['items.weapons.sword.weapon', 'items.coins.copper']
    """
    results = []

    def recursive_search(obj, path):
        if isinstance(obj, dict):
            for k, v in obj.items():
                recursive_search(v, path + [k])
        elif isinstance(obj, (list, set, tuple)):
            # only record path once if value is inside
            if value in obj:
                results.append(path)
            # still check deeper (in case of nested dicts inside list)
            for item in obj:
                if isinstance(item, dict):
                    recursive_search(item, path)
        else:
            if obj == value:
                results.append(path)

    recursive_search(d, [])

    if sep is not None:
        return [sep.join(keys) for keys in results]
    return results


def del_dict_value(d: dict, value) -> dict:
    """Delete a specific value from all nested locations in a dictionary.

    Modifies the dictionary in place, removing the value from dicts,
    lists, and sets at any nesting depth.

    Args:
        d: Dictionary to modify.
        value: Value to remove.

    Raises:
        TypeError: If the input is not a dictionary.

    Examples:
        >>> d = {"items": {\
                    "weapons": {"sword": {"weapon": [2, 3]}},\
                    "coins": {"golden" : [10,22,33], "copper": [1,2,3]}\
                }\
            }
        >>> del_dict_value(d, 3)
        >>> print(d)
        {'items': {'weapons': {'sword': {'weapon': [2]}}, 'coins': {'golden': [10, 22, 33], 'copper': [1, 2]}}}
    """

    if not isinstance(d, dict):
        raise TypeError("Input must be a dictionary")

    def recursive_clean(obj):
        if isinstance(obj, dict):
            keys_to_delete = []
            for k, val in obj.items():
                if val == value:
                    keys_to_delete.append(k)
                else:
                    new_val = recursive_clean(val)
                    if new_val is None or new_val == value:
                        keys_to_delete.append(k)
                    else:
                        obj[k] = new_val
            for k in keys_to_delete:
                del obj[k]
            return obj

        elif isinstance(obj, list):
            i = 0
            while i < len(obj):
                if obj[i] == value:
                    obj.pop(i)
                else:
                    new_val = recursive_clean(obj[i])
                    if new_val is None or new_val == value:
                        obj.pop(i)
                    else:
                        obj[i] = new_val
                        i += 1
            return obj

        elif isinstance(obj, set):
            to_remove = {item for item in obj if item == v}
            to_add = set()
            for item in list(obj):
                if item != value:
                    new_val = recursive_clean(item)
                    if new_val is None or new_val == value:
                        to_remove.add(item)
                    elif new_val != item:
                        to_remove.add(item)
                        to_add.add(new_val)
            obj.difference_update(to_remove)
            obj.update(to_add)
            return obj

        else:
            return obj if obj != value else None

    recursive_clean(d)

def set_dict_value(d: dict, path: str, value, sep: str='.') -> None:
    """Set a value at a nested path in a dictionary.

    Creates intermediate keys if they do not exist.

    Args:
        d: Dictionary to modify.
        path: Dot-separated (or custom separator) string of nested keys.
        value: Value to set at the target path.
        sep: Separator used between keys in the path string.

    Examples:
        >>> d = {"items": {\
                    "weapons": {"sword": {"weapon": [2, 3]}},\
                    "coins": {"golden" : [10,22,33], "copper": [1,2,3]}\
                }\
            }
        >>> set_dict_value(d, 'items.coins.silver', 'value')
        >>> print(d)
        {'items': {'weapons': {'sword': {'weapon': [2, 3]}}, 'coins': {'golden': [10, 22, 33], 'copper': [1, 2, 3], 'silver': 'value'}}}
    """

    # For tracing the path
    parse_path = path.split(sep)

    # For keeping track how deep we made it in the dict, starting in the root
    depth = 0

    try:
        # Dive deep into the dictionary
        for p in parse_path[:-1]:
            d = d[p]
            depth += 1

        # Set the value on the leaf
        d[parse_path[-1]] = value

    except KeyError:
        # If path no longer exists, create the necessary keys
        d.update(_create_dict_list(parse_path[depth:], value))

def get_dict_value(d: dict, path: str, sep :str='.', not_found=None):
    """Get a value from a nested dictionary by dot-separated path.

    Args:
        d: Dictionary to search.
        path: Dot-separated (or custom separator) key path. Empty string
            returns the entire dictionary.
        sep: Separator used between keys in the path string.
        not_found: Value returned when the key path does not exist.

    Returns:
        The value at the given path, or ``not_found`` if the path is
        missing.

    Examples:
        >>> d = {"items": {\
                "weapons": {"sword": {"weapon": [2, 3]}},\
                "coins": {"golden" : [10,22,33], "copper": [1,2,3]}\
            }\
        }

        # Get the whole dict
        >>> print(f"{get_dict_value(d, '')}")
        {'items': {'weapons': {'sword': {'weapon': [2, 3]}}, 'coins': {'golden': [10, 22, 33], 'copper': [1, 2, 3]}}}

        # Get all available sword weapon
        >>> print(f"{get_dict_value(d, 'items.weapons.sword.weapon')}")
        [2, 3]

        # Get number of golden coins available
        >>> print(f"Number of golden coins: {len(get_dict_value(d, 'items.coins.golden', not_found=[]))}")
        Number of golden coins: 3

        # Get number of silver coins available
        >>> print(f"Number of silver coins: {len(get_dict_value(d, 'items.coins.silver', not_found=[]))}")
        Number of silver coins: 0
    """

    # In case path is not specified, return the whole dict
    if not path: return d

    # For narrowed down dictionary
    parse_dict = d
    try:
        # Dive deep into the dictionary
        for p in path.split(sep):
            parse_dict = parse_dict[p]

        return parse_dict
    except KeyError:
        return not_found

def add_dict_value(d: dict, path: str, value, sep: str='.') -> int:
    """Add a value to a set stored at a nested dictionary path.

    If the path already holds an iterable, the value is added to it
    (converted to a set). If the path does not exist, a new single-
    element set is created.

    Args:
        d: Dictionary to modify.
        path: Dot-separated (or custom separator) key path.
        value: Value to add to the set.
        sep: Separator used between keys in the path string.

    Returns:
        Number of items in the set after adding the value.

    Examples:
        >>> d = {"items": {\
                    "weapons": {"sword": {"weapon": [2, 3]}},\
                    "coins": {"golden" : [10,22,33], "copper": [1,2,3]}\
                }\
            }

        >>> add_dict_value(d, 'items.coins.golden', 34)
        4
        >>> add_dict_value(d, 'items.coins.golden', 35)
        5
        >>> add_dict_value(d, 'items.coins.golden', 38)
        6

        >>> add_dict_value(d, 'items.coins.iron', 555)
        1
        >>> add_dict_value(d, 'items.coins.iron', 777)
        2
    """

    try:
        #assert isinstance(value, int), f'Value must be integer.'

        current_value = get_dict_value(d, path, sep=sep)

        # If there is currently already some value stored
        if current_value:
            assert (isinstance(current_value, list) or isinstance(current_value, set) or isinstance(current_value, tuple)), f'Current Value must be iterable.'
            new_value = set(current_value)
            new_value.add(value)
            set_dict_value(d, path, new_value, sep=sep)
            return len(new_value)
        else:
            set_dict_value(d, path, set([value]), sep=sep)
            return 1
    except AssertionError:
        raise

def get_all_dict_values(d: dict):
    """Yield all leaf values from a nested dictionary.

    Recursively traverses dicts, lists, and sets, yielding every
    non-container value encountered.

    Args:
        d: Dictionary to extract values from.

    Yields:
        Individual leaf values from the nested structure.

    Examples:
        >>> d = {"items": {\
                    "weapons": {"sword": {"weapon": [2, 3]}},\
                    "coins": {"golden" : [10,22,33], "copper": [1,2,3]}\
                }\
            }
        >>> set(get_all_dict_values(d))
        {33, 2, 3, 1, 10, 22}
        >>> set(get_all_dict_values(d['items']['weapons']))
        {2, 3}
    """

    for val in d.values():
        if isinstance(val, dict):
            yield from get_all_dict_values(val)
        elif isinstance(val, list) or isinstance(val, set):
            for v in val:
                yield v
        else:
            yield val

def _get_coll_len(coll, keys: list) -> int:
    """Get the length of a collection at a path specified by a list of keys.

    Args:
        coll: Collection (dict, list, tuple, or set) to search.
        keys: List of keys forming the path to the target collection.

    Returns:
        Length of the found collection, or count of matching items.
    """
    if len(keys) == 0: return len(coll)

    sum = 0

    if isinstance(coll, dict):
        try:
            if len(keys) == 1: # Yield the results
                sub_coll = coll[keys[0]]
                if sub_coll is not None:
                    if isinstance(sub_coll, list) or isinstance(sub_coll, tuple) or isinstance(sub_coll, set):
                        return sum + len(sub_coll)
                    else:
                        return  sum + 1
                else:
                    return 0 # is None
            else:
                # If some parts of path exist, continue
                return sum +_get_coll_len(coll=coll[keys[0]], keys=keys[1:])
        except KeyError:
            return sum + 0 # key was not found in the dictionary, return 0

    elif isinstance(coll, list) or isinstance(coll, tuple) or isinstance(coll, set):
        for item in coll:
            sum = sum  + _get_coll_len(coll=item, keys=keys)
        return sum

def get_coll_len(coll, path: str, sep: str='.'):
    """Get the total length of values at a path in a nested collection.

    Args:
        coll: Collection (dict, list, tuple, or set) to search.
        path: Separator-delimited key path to the target.
        sep: Separator used between keys in the path string.

    Returns:
        Total count of items found at the specified path across all
        matching sub-collections.

    Examples:
        >>> ex = {\
            'prereqs': [],\
            'entities': [\
                {\
                    'id': 'NPC',\
                    'components': [\
                        {"type" : "collidable:Collidable", "params" :  {"x": 15, "y": 27, "dx": 0, "dy": 8}},\
                        {"type" : "damageable:Damageable", "params" : {"health" : 100}},\
                        {"type" : "destroy_on_no_health:DestroyOnNoHealth", "params" : {"ttl" : 10000, 'handlers': [11,22,33]}}\
                    ]\
                },\
                {\
                    'id': 'PLAYER',\
                    'components': [\
                        {"type" : "collidable:Collidable", "params" :  {"x": 15, "y": 27, "dx": 0, "dy": 8}},\
                        {"type" : "damageable:Damageable", "params" : {"health" : 100}},\
                        {"type" : "destroy_on_no_health:DestroyOnNoHealth", "params" : {"ttl" : 10000, 'handlers': [111,222,333]}}\
                    ]\
                }\
            ]\
        }

        # Length of all components
        >>> print(get_coll_len(coll=ex, path='entities/components', sep='/'))
        6

        # Length of all component types
        >>> print(get_coll_len(coll=ex, path='entities/components/type', sep='/'))
        6

        # length of all entity ids
        >>> print(get_coll_len(coll=ex, path='entities/id', sep='/'))
        2

        # Length of all healths
        >>> print(get_coll_len(coll=ex, path='entities/components/params/health', sep='/'))
        2

        # Length of empty collection
        >>> print(get_coll_len(coll=ex, path='prereqs', sep='/'))
        0
    """
    keys = [] if path == '' else path.split(sep)
    return _get_coll_len(coll=coll, keys=keys)

def _get_coll_value(coll, keys: list):
    """Yield values at a path specified by a list of keys in a collection.

    Args:
        coll: Collection (dict, list, tuple, or set) to search.
        keys: List of keys forming the path to the target values.

    Yields:
        Values found at the specified path.
    """

    if len(keys) == 0: yield coll

    if isinstance(coll, dict):
        try:
            if len(keys) == 1: # Yield the results
                sub_coll = coll[keys[0]]
                if sub_coll:
                    if isinstance(sub_coll, list) or isinstance(sub_coll, tuple) or isinstance(sub_coll, set):
                        for item in sub_coll: yield item
                    else:
                        yield sub_coll
            else:
                # If some parts of path exist, continue
                yield from _get_coll_value(coll=coll[keys[0]], keys=keys[1:])
        except KeyError:
            return # key was not found in the dictionary, return nothing

    elif isinstance(coll, list) or isinstance(coll, tuple) or isinstance(coll, set):
        for item in coll:
            yield from _get_coll_value(coll=item, keys=keys)

def get_coll_value(coll, path: str, sep: str='.'):
    """Yield values at a path in a nested collection.

    Args:
        coll: Collection (dict, list, tuple, or set) to search.
        path: Separator-delimited key path to the target.
        sep: Separator used between keys in the path string.

    Yields:
        Values found at the specified path across all matching
        sub-collections.

    Examples:
        >>> ex = {\
            'prereqs': [],\
            'entities': [\
                {\
                    'id': 'NPC',\
                    'components': [\
                        {"type" : "collidable:Collidable", "params" :  {"x": 15, "y": 27, "dx": 0, "dy": 8}},\
                        {"type" : "damageable:Damageable", "params" : {"health" : 100}},\
                        {"type" : "destroy_on_no_health:DestroyOnNoHealth", "params" : {"ttl" : 10000, 'handlers': [11,22,33]}}\
                    ]\
                },\
                {\
                    'id': 'PLAYER',\
                    'components': [\
                        {"type" : "collidable:Collidable", "params" :  {"x": 15, "y": 27, "dx": 0, "dy": 8}},\
                        {"type" : "damageable:Damageable", "params" : {"health" : 100}},\
                        {"type" : "destroy_on_no_health:DestroyOnNoHealth", "params" : {"ttl" : 10000, 'handlers': [111,222,333]}}\
                    ]\
                }\
            ]\
        }

        # List all components
        >>> print([i for i in get_coll_value(coll=ex, path='entities/components', sep='/')])
        [{'type': 'collidable:Collidable', 'params': {'x': 15, 'y': 27, 'dx': 0, 'dy': 8}}, {'type': 'damageable:Damageable', 'params': {'health': 100}}, {'type': 'destroy_on_no_health:DestroyOnNoHealth', 'params': {'ttl': 10000, 'handlers': [11, 22, 33]}}, {'type': 'collidable:Collidable', 'params': {'x': 15, 'y': 27, 'dx': 0, 'dy': 8}}, {'type': 'damageable:Damageable', 'params': {'health': 100}}, {'type': 'destroy_on_no_health:DestroyOnNoHealth', 'params': {'ttl': 10000, 'handlers': [111, 222, 333]}}]

        # List all component types
        >>> print([i for i in get_coll_value(coll=ex, path='entities/components/type', sep='/')])
        ['collidable:Collidable', 'damageable:Damageable', 'destroy_on_no_health:DestroyOnNoHealth', 'collidable:Collidable', 'damageable:Damageable', 'destroy_on_no_health:DestroyOnNoHealth']

        # List all entity ids
        >>> print([i for i in get_coll_value(coll=ex, path='entities/id', sep='/')])
        ['NPC', 'PLAYER']

        # List all healths
        >>> print([i for i in get_coll_value(coll=ex, path='entities/components/params/health', sep='/')])
        [100, 100]

        # List all collidable components
        >>> print( list( filter( lambda x: x["type"] == "collidable:Collidable", get_coll_value(coll=ex, path='entities/components', sep='/') ) ) )
        [{'type': 'collidable:Collidable', 'params': {'x': 15, 'y': 27, 'dx': 0, 'dy': 8}}, {'type': 'collidable:Collidable', 'params': {'x': 15, 'y': 27, 'dx': 0, 'dy': 8}}]

    """
    keys = [] if path == '' else path.split(sep)
    yield from _get_coll_value(coll=coll, keys=keys)

def merge_dicts(orig: dict, new: dict) -> dict:
    """Recursively merge two dictionaries.

    Values from ``new`` take precedence. Nested dicts are merged
    recursively rather than replaced wholesale.

    Args:
        orig: Base dictionary (lower priority).
        new: Override dictionary (higher priority).

    Returns:
        Merged dictionary combining both inputs.

    Examples:
        >>> orig = {\
            "RESOLUTION" : [640, 480],\
            "BITDEPTH" : 32,\
            "FULLSCREEN" : False,\
            "MAX_FPS" : 250,\
            "SHOW_FPS" : True\
        }

        >>> new = {\
            "RESOLUTION" : [800, 600],\
            "BITDEPTH" : 24,\
            "FULLSCREEN" : True,\
            "MAX_FPS" : 500,\
            "SHOW_FPS" : False,\
            "GUI_WINDOW_RATIO": 1.8\
        }

        >>> merged = merge_dicts(orig, new)
        >>> merged["RESOLUTION"]
        [800, 600]
        >>> merged["FULLSCREEN"]
        True
        >>> merged["SHOW_FPS"]
        False

        >>> empty = dict()
        >>> merged = merge_dicts(orig, empty)
        >>> merged["FULLSCREEN"]
        False
    """

    # Add items that exist in new but not in original
    merged = {k: v for k,v in new.items() if k not in orig}

    for orig_key in orig:
        # check if exists in orig dict
        if orig_key not in new:
            merged[orig_key] = orig[orig_key]
        else:
            # key exists in both original and new
            # if in the new dict the value is not dict - merge it
            if not isinstance(new[orig_key], dict):
                merged[orig_key] = new[orig_key]
            else: # the value is again dict
                merged[orig_key] = merge_dicts(orig[orig_key], new[orig_key])

    return merged


if __name__ == '__main__':


    import doctest
    doctest.testmod()
    '''
    ex = {
            'prereqs': [],
            'entities': [
                {
                    'id': 'NPC',
                    'components': [
                        {"type" : "collidable:Collidable", "params" :  {"x": 15, "y": 27, "dx": 0, "dy": 8}},
                        {"type" : "damageable:Damageable", "params" : {"health" : 100}},
                        {"type" : "destroy_on_no_health:DestroyOnNoHealth", "params" : {"ttl" : 10000, 'handlers': [11,22,33]}}
                    ]
                },
                {
                    'id': 'PLAYER',
                    'components': [
                        {"type" : "collidable:Collidable", "params" :  {"x": 15, "y": 27, "dx": 0, "dy": 8}},
                        {"type" : "damageable:Damageable", "params" : {"health" : 100}},
                        {"type" : "destroy_on_no_health:DestroyOnNoHealth", "params" : {"ttl" : 10000, 'handlers': [111,222,333]}}
                    ]
                }
            ]
        }

    print(get_coll_len(coll=ex, path='entities/components/params/health', sep='/'))
    '''