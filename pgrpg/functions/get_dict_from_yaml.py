"""Load a dictionary from a YAML file."""

import yaml
from pathlib import Path

def get_dict_from_yaml(filepath: Path) -> dict:
    """Parse a YAML file into a dictionary.

    Args:
        filepath: Path to the YAML file.

    Returns:
        Dictionary of parsed YAML data.

    Raises:
        FileNotFoundError: If the file does not exist.
    """

    try:
        with open(filepath, 'r') as yaml_file:
            try:
                return yaml.safe_load(yaml_file)
            except yaml.YAMLError as e:
                raise e
    except FileNotFoundError as e:
        raise e
