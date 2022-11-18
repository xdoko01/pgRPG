def translate(trans_dict, value):
    ''' Takes value and translates it to another value based on the
    translation dictionary. It is used to substitute entity aliases
    with entity ids while creating component from json definition.

    Parameters:
        :param trans_dict: Dictionary hodling source -> destination mapping
        :type trans_dict: dict

        :param value: Value for translation
        :type value: int, str, dict, list, tuple

        :returns: Translated value
    '''
    try:
        if isinstance(value, dict):
            translated_dict = {}
            for i_key, i_value in value.items():
                translated_dict = {**translated_dict, **{i_key : translate(trans_dict, i_value)}}
            return translated_dict
        elif isinstance(value, list):
            return [translate(trans_dict, item) for item in value]
        elif isinstance(value, tuple):
            return tuple([translate(trans_dict, item) for item in value])
        else:
            return trans_dict.get(value, value)
    except:
        print(f'Cannot translate "{value}" by using translation dictionary "{trans_dict}"')
        raise ValueError

if __name__ == '__main__':
    ''' Test the translate function on different examples
    '''

    trans_dict = {
        "first_value" : 1,
        "second_value" : 2,
        "third_value" : 3,
        "first_list" : [ "item1", "item2", "item3"],
        "first_dict" : { "a" : "dict1"}
    }

    input1 = {
        "first_key" : "first_value",
        "second_key" : ["first_value", "second_value"],
        "third_key" : { "third_key_1" : ["second_value", {"first_value" : "third_value"}]}
    }

    print(f'Translation dict:\n{trans_dict}')
    print(f'Original input:\n{input1}')
    print(f'Translated output:\n{translate(trans_dict, input1)}')

    print(dict(zip([],[])))
    print(f'Translated output:\n{translate(dict(zip([],[])), input1)}')