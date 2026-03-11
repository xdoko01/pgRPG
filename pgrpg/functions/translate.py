"""Translate entity aliases to entity IDs using a translation dictionary.

Used during component creation from JSON definitions to substitute
string aliases with integer ECS entity IDs.
"""

def translate(trans_dict, value, prefix=''):
    """Recursively translate values using a translation dictionary.

    Walks dicts, lists, and tuples, replacing any value found in
    ``trans_dict`` with its mapped counterpart. When ``prefix`` is set,
    only strings starting with that prefix are translated (after
    stripping the prefix).

    Args:
        trans_dict: Source-to-destination mapping dictionary.
        value: Value to translate. Can be int, str, dict, list, or tuple.
        prefix: If set, only translate strings starting with this prefix
            (the prefix is removed before lookup).

    Returns:
        The translated value, with the same structure as the input.

    Raises:
        KeyError: If a prefixed value is not found in the translation
            dictionary.
        ValueError: If translation fails for any other reason.
    """
    try:
        if isinstance(value, dict):
            translated_dict = {}
            for i_key, i_value in value.items():
                translated_dict = {**translated_dict, **{i_key : translate(trans_dict, i_value, prefix)}}
            return translated_dict
        elif isinstance(value, list):
            return [translate(trans_dict, item, prefix) for item in value]
        elif isinstance(value, tuple):
            return tuple([translate(trans_dict, item, prefix) for item in value])


        # Extra part only due to prefix functionality.
        # Only translate, if the value has desired prefix if prefix defined.
        elif isinstance(value, str):
            if prefix:
                if value.startswith(prefix):
                    try:
                        return trans_dict[value.removeprefix(prefix)] # must find the value in the translation dictionary else exception
                    except KeyError:
                        raise KeyError(f'Cannot find value {value=} in the translation dictionary {trans_dict=}')
                else:
                    return value
            else:
                return trans_dict.get(value, value)


        else:
            return trans_dict.get(value, value)

    except:
        #print(f'Cannot translate "{value}" by using translation dictionary "{trans_dict}"')
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

    input2 = {
        "first_key" : "first_value",
        "second_key" : ["first_value", "second_value"],
        "third_key" : { "third_key_1" : ["second_value", {"first_value" : "^third_value"}]}
    }

    print(f'Translation dict:\n{trans_dict}')
    print(f'Original input:\n{input1}')
    print(f'Translated output:\n{translate(trans_dict, input1)}')

    print(dict(zip([],[])))
    print(f'Translated output:\n{translate(dict(zip([],[])), input1)}')
    print(f'Translated output using prefix:\n{translate(trans_dict, input2, prefix="^")}') # with prefix ^
