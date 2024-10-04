def _get_coll_value(coll, keys: list):
    '''Get the value specified on the path (specified by sequence of keys) 
    from the collection.

    Parameters:
        :param coll: Collection that is being searched
        :type coll: dict/list/tuple/set/...

        :param keys: List of keys where new value should be found.
        :type keys: list
    '''

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
    '''Get the value specified on the path from the collection.

    Parameters:
        :param coll: Collection that is being searched
        :type coll: dict/list/tuple/set/...

        :param path: List of keys in form of a string separated by sep
                     where new value should be found.
        :type path: str

        :param sep: Separator used to separate the keys in path string
        :type sep: str


    Tests:
        >>> ex = {\
            'entities': [\
                {\
                    'id': 'NPC',\
                    'components': [\
                        {"type" : "collidable:Collidable", "params" :  {"x": 15, "y": 27, "dx": 0, "dy": 8}},\
                        {"type" : "new.damageable:Damageable", "params" : {"health" : 100}},\
                        {"type" : "new.destroy_on_no_health:DestroyOnNoHealth", "params" : {"ttl" : 10000, 'handlers': [11,22,33]}}\
                    ]\
                },\
                {\
                    'id': 'PLAYER',\
                    'components': [\
                        {"type" : "collidable:Collidable", "params" :  {"x": 15, "y": 27, "dx": 0, "dy": 8}},\
                        {"type" : "new.damageable:Damageable", "params" : {"health" : 100}},\
                        {"type" : "new.destroy_on_no_health:DestroyOnNoHealth", "params" : {"ttl" : 10000, 'handlers': [111,222,333]}}\
                    ]\
                }\
            ]\
        }

        # List all components - 2 lists for components of 2 entities
        >>> print([i for i in get_coll_value(coll=ex, path='entities/components', sep='/')])
        [[{'type': 'collidable:Collidable', 'params': {'x': 15, 'y': 27, 'dx': 0, 'dy': 8}}, {'type': 'new.damageable:Damageable', 'params': {'health': 100}}, {'type': 'new.destroy_on_no_health:DestroyOnNoHealth', 'params': {'ttl': 10000, 'handlers': [11, 22, 33]}}], [{'type': 'collidable:Collidable', 'params': {'x': 15, 'y': 27, 'dx': 0, 'dy': 8}}, {'type': 'new.damageable:Damageable', 'params': {'health': 100}}, {'type': 'new.destroy_on_no_health:DestroyOnNoHealth', 'params': {'ttl': 10000, 'handlers': [111, 222, 333]}}]]
        
        # List all component types
        >>> print([i for i in get_coll_value(coll=ex, path='entities/components/type', sep='/')])
        ['collidable:Collidable', 'new.damageable:Damageable', 'new.destroy_on_no_health:DestroyOnNoHealth', 'collidable:Collidable', 'new.damageable:Damageable', 'new.destroy_on_no_health:DestroyOnNoHealth']
        
        # List all entity ids
        >>> print([i for i in get_coll_value(coll=ex, path='entities/id', sep='/')])
        ['NPC', 'PLAYER']

        # List all healths
        >>> print([i for i in get_coll_value(coll=ex, path='entities/components/params/health', sep='/')])
        [100, 100]

        # List all collidable components
        >>> print( list( filter( lambda x: x["type"] == "collidable:Collidable", reduce( lambda x,y: x+y, get_coll_value(coll=ex, path='entities/components', sep='/') ) ) ) )
        [{'type': 'collidable:Collidable', 'params': {'x': 15, 'y': 27, 'dx': 0, 'dy': 8}}, {'type': 'collidable:Collidable', 'params': {'x': 15, 'y': 27, 'dx': 0, 'dy': 8}}]
    '''
    keys = [] if path == '' else path.split(sep)
    yield from _get_coll_value(coll=coll, keys=keys)


if __name__ == "__main__":

    from pprint import pprint
    from functools import reduce

    ex = 123
    print([i for i in get_coll_value(coll=ex, path='aa', sep='/')])
    print([i for i in get_coll_value(coll=ex, path='', sep='/')])
    print([i for i in get_coll_value(coll=ex, path='', sep='/')])


    ex = {"type" : "collidable:Collidable", "params" :  {"x": 15, "y": 27, "dx": 0, "dy":  8}}

    print([i for i in get_coll_value(coll=ex, path='aa', sep='/')])
    print([i for i in get_coll_value(coll=ex, path='params', sep='/')])


    ex = {
        'entities': [
            {
                'id': 'NPC',
                'components': [
                    {"type" : "collidable:Collidable", "params" :  {"x": 15, "y": 27, "dx": 0, "dy": 8}},
                    {"type" : "new.damageable:Damageable", "params" : {"health" : 100}},
                    {"type" : "new.destroy_on_no_health:DestroyOnNoHealth", "params" : {"ttl" : 10000, 'handlers': [11,22,33]}}
                ]
            },
            {
                'id': 'PLAYER',
                'components': [
                    {"type" : "collidable:Collidable", "params" :  {"x": 15, "y": 27, "dx": 0, "dy": 8}},
                    {"type" : "new.damageable:Damageable", "params" : {"health" : 100}},
                    {"type" : "new.destroy_on_no_health:DestroyOnNoHealth", "params" : {"ttl" : 10000, 'handlers': [111,222,333]}}
                ]
            }
        ]
    }

    # List all components - 2 lists for components of 2 entities
    pprint([i for i in get_coll_value(coll=ex, path='entities/components', sep='/')])

    # List all component types
    pprint([i for i in get_coll_value(coll=ex, path='entities/components/type', sep='/')])

    # List all entity ids
    pprint([i for i in get_coll_value(coll=ex, path='entities/id', sep='/')])

    # List all healths
    pprint([i for i in get_coll_value(coll=ex, path='entities/components/params/health', sep='/')])

    # List all collidable components
    '''
    print(
        list(
            filter(
                lambda x: x["type"] == "collidable:Collidable", 
                reduce(
                    lambda x,y: x+y, 
                    get_coll_value(coll=ex, path='entities/components', sep='/')
                )
            )
        )
    )
    '''

    ex = {"type" : "collidable:Collidable", "params" :  {"x": 15, "y": 27, "dx": 0, "dy":  8}}

    print([i for i in get_coll_value(coll=ex, path='aa', sep='/')])
    print([i for i in get_coll_value(coll=ex, path='params', sep='/')])
    print([i for i in get_coll_value(coll=ex, path='params/x', sep='/')])
    print([i for i in get_coll_value(coll=ex, path='params/aa', sep='/')])
    print([i for i in get_coll_value(coll=ex, path='params/aa/bb', sep='/')])

    ex = { "s": {1,2,3,4,5} }

    print([i for i in get_coll_value(coll=ex, path='xx', sep='/')])
    print([i for i in get_coll_value(coll=ex, path='s', sep='/')])

    ex = [ {"a": 10}, {"b": 20}, {"c": 30}, {"a": 100}, {"d": { "a": 1000}} ]

    print([i for i in get_coll_value(coll=ex, path='a', sep='/')])
    print([i for i in get_coll_value(coll=ex, path='d', sep='/')])
    print([i for i in get_coll_value(coll=ex, path='d/a', sep='/')])

    ex = {

        "$schema": "../../../../../core/schemas/new/quest.schema.json",

        "id" : "guard_and_fight_back_if_ambushed",
        "title" : "Test commands for fighting",
        "description" : "Test commands for fighting",
        "objective" : "POC of NPC controlled by the script",

        "prereqs" : []
    }

    print('Prereqs')
    print([i for i in get_coll_value(coll=ex, path='prereqs', sep='/')])

    print('Prereqs inc empty')
    print([i for i in get_coll_value(coll=ex, path='prereqs', sep='/', inc_empty=True)])

    print('Prereqs for cycle')
    data_to_process = get_coll_value(coll=ex, path='prereqs', sep='/') # generator

    for item in data_to_process:
        print(f'About to process following item "{item}" using function "".')

    print('Prereqs for cycle inc empty')
    data_to_process = get_coll_value(coll=ex, path='prereqs', sep='/', inc_empty=True) # generator

    for item in data_to_process:
        print(f'About to process following item "{item}" using function "".')

    ex = {
            "processors" : [
                ["new.movement_system.remove_flag_do_move_processor:RemoveFlagDoMoveProcessor", {}],
                ["attack_system.remove_flag_do_attack_processor:RemoveFlagDoAttackProcessor", {}]
            ]
    }

    print('Processors')
    data_to_process = get_coll_value(coll=ex, path='processors', sep='/') # generator

    for item in data_to_process:
        print(f'About to process following item "{item}" using function "".')
