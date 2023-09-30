from pathlib import Path
from get_dict_from_json import get_dict_from_json
from get_dict_from_yaml import get_dict_from_yaml

def get_dict_from_file(filepath: Path, dir: Path=Path('')) -> dict:
    '''Loads dictionary from the file specified by the filepath
    either using absolute or relative path. Also filepath can
    specify the file without file suffix. The functionality will
    try to guess the suffix and load.
    
    Parameters:
        :param filepath: Path to the json/yaml file in the dir directory or absolute path.
                        It is not necessary to specify the suffix.
        :type dict_path: Path

        :param dir: Relative path, where to look for json/yaml file specified by filepath.
        :type dir: Path

        :returns: dict
    
    Tests:
        >>> d = get_dict_from_file(filepath=Path('C:/Users/otakar/OneDrive/Personal/Python/pyRPG/config.json'))
        >>> d = get_dict_from_file(filepath=Path('C:/Users/otakar/OneDrive/Personal/Python/pyRPG/config'))
        >>> d = get_dict_from_file(filepath=Path('config.json'), dir=Path('C:/Users/otakar/OneDrive/Personal/Python/pyRPG'))
        >>> d = get_dict_from_file(filepath=Path('config'), dir=Path('C:/Users/otakar/OneDrive/Personal/Python/pyRPG'))
    '''

    # Check if the filepath has some file extension specified - if not we will try to guess json or yaml
    file_extension = filepath.suffix

    # Check if path to the dictionary is absolute or relative and construct the full path to the file
    filepath = filepath if filepath.is_absolute() else dir / filepath

    # Try to open the filepath - if suffix is not present, try to guess it
    try:
        if file_extension in ['.yaml']:
            res = get_dict_from_yaml(filepath)
        elif file_extension in ['.json']:
            res = get_dict_from_json(filepath)
        else:
            try:
                res = get_dict_from_yaml(Path(str(filepath) + '.yaml'))
            except FileNotFoundError:
                res = get_dict_from_json(Path(str(filepath) + '.json'))
    except FileNotFoundError:
        raise ValueError(f'Cannot load dict from file "{filepath}".')

    return res

if __name__ == '__main__':
    import doctest
    doctest.testmod()
