import yaml
from pathlib import Path

def get_dict_from_yaml(filepath: Path) -> dict:
    ''' Returns dictionary based on yaml file.

    Parameters:
        :param filepath: Path to the yaml file
        :type filepath: Path

        :returns: Dictionary of data
    '''

    try:
        with open(filepath, 'r') as yaml_file:
            try:
                return yaml.safe_load(yaml_file)
            except yaml.YAMLError as e:
                raise e
    except FileNotFoundError as e:
        raise e
