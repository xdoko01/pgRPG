def _create_dict_list(path: list, value) -> dict:
    '''Create a dictionary(tree) specified by the list of
    embeded keys. The value is put to the deepest key.
    
    Paramaters:
        :param path: List of embeded keys to be created in the dictionary
        :type path: list

        :param value: Value to be added to the most inner key of the dict
        :type value: any
    
    Tests:
        >>> print(_create_dict_list(['a', 'b', 'c'], "hello"))
        {'a': {'b': {'c': 'hello'}}}
    '''

    new_dict = {path[-1]: value}

    for p in reversed(path[:-1]):
        new_dict = {p: new_dict}
    
    return new_dict

def _create_dict_str(path: str, value, sep: str='.') -> dict:
    '''Create a dictionary(tree) specified by path and
    put the value to the deepest key.

    Parameters:
        :param path: List of embeded keys as a string separated by separator
        :type path: str

        :param value: Value to be added to the most inner key
        :type value: any

        :param sep: Separator used to separate the keys in path string
        :type sep: str

    Tests:
        >>> print(_create_dict_str('a.b.c', 'hello'))
        {'a': {'b': {'c': 'hello'}}}

        >>> print(_create_dict_str('a/b/c', 'hello', sep='/'))
        {'a': {'b': {'c': 'hello'}}}
    '''

    return _create_dict_list(path.split(sep), value)


def set_dict_value(d: dict, path: str, value, sep: str='.') -> None:
    '''Create a new path in the dictionary and
    put the required value there.

    Parameters:
        :param d: Dictionary that is being modified (by adding new value)
        :type d: dict

        :param path: List of keys in form of a string separated by sep
                     where new value should be added.
        :type path: str

        :param value: Value to be added to the most inner key in path
        :type value: any

        :param sep: Separator used to separate the keys in path string
        :type sep: str

    Tests:
        >>> d = {"items": {\
                    "weapons": {"sword": {"weapon": [2, 3]}},\
                    "coins": {"golden" : [10,22,33], "copper": [1,2,3]}\
                }\
            }
        >>> set_dict_value(d, 'items.coins.silver', 'value')
        >>> print(d)
        {'items': {'weapons': {'sword': {'weapon': [2, 3]}}, 'coins': {'golden': [10, 22, 33], 'copper': [1, 2, 3], 'silver': 'value'}}}
    '''

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
    '''Get the value from the dictionary that
    is on the path specified by the path string.

    Parameters:
        :param d: Dictionary that is being searched
        :type d: dict

        :param path: List of keys in form of a string separated by sep
                     where new value should be found.
        :type path: str

        :param sep: Separator used to separate the keys in path string
        :type sep: str

        :param not_found: Value that is returned in case the searched
                          key and its value is not found.
        :type not_found: any

    Tests:
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
    '''

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
    '''Add new value to the dictionary. Do not overwrite
    the existing value but convert to set and add it to
    the set.

    Parameters:
        :param d: Dictionary that is being modified (by adding new value)
        :type d: dict

        :param path: List of keys in form of a string separated by sep
                     where new value should be added.
        :type path: str

        :param value: Value to be appended to the most inner key in path
        :type value: any

        :param sep: Separator used to separate the keys in path string
        :type sep: str

        :returns: Number of items stored in the set that is the value of the key

    Tests:
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
    '''

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
    '''Parse the dictionary and get all the values as
    generator.
    By calling list(get_all_dict_values(d)) or
    set(get_all_dict_values(d)) the result can be obtained
    in form of the set or the list.

    Parameters:
        :param d: Dictionary that is being modified (by adding new value)
        :type d: dict

    Tests:
        >>> d = {"items": {\
                    "weapons": {"sword": {"weapon": [2, 3]}},\
                    "coins": {"golden" : [10,22,33], "copper": [1,2,3]}\
                }\
            }
        >>> next(get_all_dict_values(d))
        2
        >>> next(get_all_dict_values(d))
        3
        >>> set(get_all_dict_values(d))
        {33, 2, 3, 1, 10, 22}
        >>> set(get_all_dict_values(d['items']['weapons']))
        {2, 3}
    '''

    for val in d.values():
        if isinstance(val, dict):
            yield from get_all_dict_values(val)
        elif isinstance(val, list) or isinstance(val, set):
            for v in val:
                yield v
        else:
            yield val


if __name__ == '__main__':
    import doctest
    doctest.testmod()
