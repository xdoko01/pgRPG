

def parse_fnc_str(for_parse: str) -> tuple:
    '''Parses function call defined as a string into 
    function name and list of parameters.

    Examples:
        for_parse = 'sum(1, 2)'
        returns ('sum', [1, 2], {})

        for_parse = 'sum'
        returns ('sum', [], {})

        for parse = 'sum()'
        returns ('sum', [], {})
    '''

    start_pos = None
    end_pos = None

    args_as_str = ''

    for pos, c in enumerate(for_parse):
        if c == '(':
            start_pos = pos
            assert end_pos is None, f'Closing bracket preceeds opening bracket'
            assert start_pos > 0, f'Name cannot start with opening bracket'
        elif c == ')':
            end_pos = pos
            assert start_pos is not None, f'Closing bracket preceeds opening bracket'
            assert end_pos > 0, f'Name cannot start with closing bracket'
            args_as_str = for_parse[start_pos+1:end_pos]
            break

    # Now, the parameters including all spaces are stored in args variable as a str

    # Now we have exactly determined the function name
    fnc_name = for_parse[:start_pos]

    # Now we need to get all argumet from args_as_str string as a list and as a dict
    args = []
    kwargs = {}
    
    for v in args_as_str.split(","):

        v = v.strip() # Get rid of wite-spaces
        if len(v) == 0: continue # Skip empty strings

        # Normal arg, not kwarg
        if '=' not in v:
            print(v)
            v = eval(v) # Convert to the proper type
            args.append(v) # add to the args list

        # Kwarg, not arg
        else:
            key, value = v.split('=')
            key=key.replace(' ','') # Key cannot contain any space
            kwargs.update({key: eval(value)}) # Convert value to the proper type and store

    return (fnc_name, args, kwargs)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    f = 'sum(   1   ,  2 , arg1  =  True , arg2=False)'
    f = 'sum(   1+1   ,  2 , arg1  =  True , arg2=False)'
    f = 'sum(   1   ,  2 , arg1  =  {"a":"hello", "b":"hello"} , arg2=False)'
    f = 'sum(   1+1   ,  2 , arg1  =  True , arg2=False, 3)'

    print(parse_fnc_str(f))


