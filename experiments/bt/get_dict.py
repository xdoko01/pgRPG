from pathlib import Path
from get_dict_from_file import get_dict_from_file
from dict_utils import get_dict_value

def get_dict(dictpath: str, storage: dict=None, dir: Path=Path('')) -> dict:
    '''Loads dictionary specified by the dictpath either from other dictionary (storage) or from json/yaml file
    using absolute or relative path.
    
    Parameters:
        :param dictpath: Can be either path to the key in the storage dictionary, or 
                        path to the json/yaml file in the dir directory.
        :type dictpath: str

        :param storage: Reference to the dictionary, where the dictionary might
                        be stored. If not found there, function will continue to
                        look for the template in the json or yaml file stored
                        in the dir directory.
        :type storage: dict

        :param dir: Directory, where to look for json/yaml file that has the same name
                    as the dict_path.
        :type dir: Path

        :returns: dict

    Logic:
        - first, try to loog for the dictionary in the storage using the path
        - if not found, try to look for the yaml/json file using dict_path as an absolute path.
        - if not found, try to look for yaml/json file using a relative path using dir as a relative directory.
    
    Tests:
        >>> storage = { \
                'conf': "This is config", \
                'a': { \
                    'aa': {'aaa': 'AAA', 'aab': 'AAB', 'aac': 'AAC'}, \
                    'ab': {'aba': 'ABA', 'abb': 'ABB', 'abc': 'ABC'} \
                }, \
                'b': { \
                    'ba': 'BA', \
                    'bc': 'BC' \
                } \
            } \

        >>> get_dict(dictpath='a', storage=storage)
        {'aa': {'aaa': 'AAA', 'aab': 'AAB', 'aac': 'AAC'}, 'ab': {'aba': 'ABA', 'abb': 'ABB', 'abc': 'ABC'}}
        
        >>> get_dict(dictpath='a/aa', storage=storage)
        {'aaa': 'AAA', 'aab': 'AAB', 'aac': 'AAC'}
        
        >>> get_dict(dictpath='a/aa/aab', storage=storage)
        'AAB'

        >>> bool(get_dict(dictpath='C:/Users/otakar/OneDrive/Personal/Python/pyRPG/config.json'))
        True
        
        >>> bool(get_dict(dictpath='C:/Users/otakar/OneDrive/Personal/Python/pyRPG/config'))
        True

        >>> relative_path = Path('C:/Users/otakar/OneDrive/Personal/Python/pyRPG')
        >>> bool(get_dict(dictpath='config.json', dir=relative_path))
        True

        >>> get_dict(dictpath='conf', storage=storage, dir=relative_path)
        'This is config'

        >>> bool(get_dict(dictpath='config', storage=storage, dir=relative_path))
        True
    '''

    # Try to look in the storage
    if storage:
        res = get_dict_value(d=storage, path=dictpath, sep='/')
        # If the key was successfully found in the storage, finish
        if res: 
            return res

    # Continue looking in the files
    return get_dict_from_file(filepath=Path(dictpath), dir=dir)

if __name__ == '__main__':
    import doctest
    doctest.testmod()