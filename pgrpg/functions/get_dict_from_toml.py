import toml
from pathlib import Path

def get_dict_from_toml(filepath: Path) -> dict:
    ''' Returns dictionary based on toml file.

    Parameters:
        :param filepath: Path to the yaml file
        :type filepath: Path

        :returns: Dictionary of data
    '''

    try:
        with open(filepath, 'r') as toml_file:
            return toml.load(toml_file)
    except FileNotFoundError as e:
        raise e
